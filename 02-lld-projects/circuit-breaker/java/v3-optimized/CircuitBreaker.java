import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.LongSupplier;

public class CircuitBreaker {
    private final CircuitBreakerConfig config;
    private final AtomicReference<StateInfo> state;
    private final LongSupplier clock;
    
    private final Bucket[] buckets;
    private final long bucketSizeInMs = 1000;
    
    private final ReentrantLock windowLock = new ReentrantLock();

    private static class StateInfo {
        final CircuitBreakerState state;
        final long generation;
        final long transitionTime;
        final AtomicInteger halfOpenCalls;

        StateInfo(CircuitBreakerState state, long generation, long transitionTime) {
            this.state = state;
            this.generation = generation;
            this.transitionTime = transitionTime;
            this.halfOpenCalls = new AtomicInteger(0);
        }
    }

    public CircuitBreaker(CircuitBreakerConfig config) {
        this(config, System::currentTimeMillis);
    }
    
    public CircuitBreaker(CircuitBreakerConfig config, LongSupplier clock) {
        this.config = config;
        this.clock = clock;
        this.state = new AtomicReference<>(new StateInfo(CircuitBreakerState.CLOSED, 0, clock.getAsLong()));
        this.buckets = new Bucket[config.getSlidingWindowSize()];
        long now = clock.getAsLong();
        for (int i = 0; i < buckets.length; i++) {
            buckets[i] = new Bucket(now - (buckets.length - i) * bucketSizeInMs);
        }
    }

    public <T> T execute(Callable<T> callable) throws Exception {
        return execute(callable, null);
    }
    
    public <T> T execute(Callable<T> callable, Fallback<T> fallback) throws Exception {
        long callGeneration;
        try {
            callGeneration = checkState();
        } catch (CircuitBreakerOpenException e) {
            if (fallback != null) {
                return fallback.apply(e);
            }
            throw e;
        }

        long startTime = clock.getAsLong();
        try {
            T result = callable.call();
            long duration = clock.getAsLong() - startTime;
            onSuccess(duration, callGeneration);
            return result;
        } catch (Exception e) {
            long duration = clock.getAsLong() - startTime;
            if (!(e instanceof CircuitBreakerOpenException)) {
                onError(duration, callGeneration);
            }
            if (fallback != null) {
                return fallback.apply(e);
            }
            throw e;
        }
    }

    private long checkState() {
        while (true) {
            StateInfo current = state.get();
            if (current.state == CircuitBreakerState.OPEN) {
                long now = clock.getAsLong();
                if (now - current.transitionTime >= config.getWaitDurationInOpenState()) {
                    StateInfo next = new StateInfo(CircuitBreakerState.HALF_OPEN, current.generation + 1, now);
                    if (state.compareAndSet(current, next)) {
                        continue;
                    } else {
                        continue;
                    }
                } else {
                    throw new CircuitBreakerOpenException("Circuit Breaker is OPEN");
                }
            }
            
            if (current.state == CircuitBreakerState.HALF_OPEN) {
                if (current.halfOpenCalls.incrementAndGet() > config.getPermittedNumberOfCallsInHalfOpen()) {
                    throw new CircuitBreakerOpenException("Circuit Breaker is HALF_OPEN (No permits left)");
                }
            }
            return current.generation;
        }
    }

    private void onSuccess(long duration, long callGeneration) {
        StateInfo current = state.get();
        if (current.generation != callGeneration) {
            return;
        }

        if (current.state == CircuitBreakerState.HALF_OPEN) {
            long now = clock.getAsLong();
            StateInfo next = new StateInfo(CircuitBreakerState.CLOSED, current.generation + 1, now);
            if (state.compareAndSet(current, next)) {
                resetWindow(now);
            }
        } else if (current.state == CircuitBreakerState.CLOSED) {
            recordResult(true, duration);
            evaluateState(current);
        }
    }

    private void onError(long duration, long callGeneration) {
        StateInfo current = state.get();
        if (current.generation != callGeneration) {
            return;
        }

        if (current.state == CircuitBreakerState.HALF_OPEN) {
            long now = clock.getAsLong();
            StateInfo next = new StateInfo(CircuitBreakerState.OPEN, current.generation + 1, now);
            state.compareAndSet(current, next);
        } else if (current.state == CircuitBreakerState.CLOSED) {
            recordResult(false, duration);
            evaluateState(current);
        }
    }
    
    private void evaluateState(StateInfo current) {
        if (current.state != CircuitBreakerState.CLOSED) return;

        int[] rates = calculateRates();
        int failureRate = rates[0];
        int slowCallRate = rates[1];
        
        if (failureRate >= config.getFailureRateThreshold() || slowCallRate >= config.getSlowCallRateThreshold()) {
             long now = clock.getAsLong();
             StateInfo next = new StateInfo(CircuitBreakerState.OPEN, current.generation + 1, now);
             state.compareAndSet(current, next);
        }
    }

    private void recordResult(boolean success, long duration) {
        long now = clock.getAsLong();
        Bucket currentBucket = getCurrentBucket(now);
        if (success) {
            currentBucket.successCount.incrementAndGet();
        } else {
            currentBucket.failureCount.incrementAndGet();
        }
        
        if (duration > config.getSlowCallDurationThresholdMs()) {
            currentBucket.slowCallCount.incrementAndGet();
        }
    }

    private Bucket getCurrentBucket(long now) {
        windowLock.lock();
        try {
            Bucket latestBucket = null;
            for (Bucket b : buckets) {
                if (latestBucket == null || b.startTime > latestBucket.startTime) {
                    latestBucket = b;
                }
            }
            
            long currentBucketStartTime = now - (now % bucketSizeInMs);
            
            if (latestBucket != null && latestBucket.startTime != currentBucketStartTime) {
                long timeDiff = currentBucketStartTime - latestBucket.startTime;
                int shiftCount = (int) Math.min(timeDiff / bucketSizeInMs, buckets.length);
                
                for(int i = 0; i < shiftCount; i++) {
                     for(int j = 1; j < buckets.length; j++) {
                         buckets[j-1] = buckets[j];
                     }
                     buckets[buckets.length - 1] = new Bucket(currentBucketStartTime - (shiftCount - 1 - i) * bucketSizeInMs);
                }
            }
            return buckets[buckets.length - 1];
        } finally {
            windowLock.unlock();
        }
    }

    private int[] calculateRates() {
        windowLock.lock();
        try {
            int totalCalls = 0;
            int totalFailures = 0;
            int totalSlowCalls = 0;
            
            long now = clock.getAsLong();
            long windowStart = now - (buckets.length * bucketSizeInMs);
            
            for (Bucket b : buckets) {
                if (b != null && b.startTime >= windowStart) {
                    totalCalls += b.successCount.get() + b.failureCount.get();
                    totalFailures += b.failureCount.get();
                    totalSlowCalls += b.slowCallCount.get();
                }
            }
            
            if (totalCalls == 0) return new int[]{0, 0};
            return new int[]{
                (totalFailures * 100) / totalCalls,
                (totalSlowCalls * 100) / totalCalls
            };
        } finally {
            windowLock.unlock();
        }
    }

    private void resetWindow(long now) {
        windowLock.lock();
        try {
             for (int i = 0; i < buckets.length; i++) {
                 buckets[i] = new Bucket(now - (buckets.length - i) * bucketSizeInMs);
             }
        } finally {
             windowLock.unlock();
        }
    }

    public CircuitBreakerState getState() {
        return state.get().state;
    }
}
