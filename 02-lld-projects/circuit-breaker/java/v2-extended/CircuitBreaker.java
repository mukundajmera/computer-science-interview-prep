import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.LongSupplier;

public class CircuitBreaker {
    private final CircuitBreakerConfig config;
    private final AtomicReference<CircuitBreakerState> state;
    private volatile long lastStateTransitionTime;
    
    private final Bucket[] buckets;
    private final long bucketSizeInMs = 1000;
    
    private final ReentrantLock windowLock = new ReentrantLock();
    private final AtomicInteger halfOpenCalls = new AtomicInteger(0);
    private final AtomicInteger generation = new AtomicInteger(0);
    private final LongSupplier clock;
    private final ReentrantLock stateLock = new ReentrantLock();

    public CircuitBreaker(CircuitBreakerConfig config) {
        this(config, System::currentTimeMillis);
    }
    
    public CircuitBreaker(CircuitBreakerConfig config, LongSupplier clock) {
        this.config = config;
        this.clock = clock;
        this.state = new AtomicReference<>(CircuitBreakerState.CLOSED);
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
        int currentGen;
        try {
            currentGen = checkState();
        } catch (CircuitBreakerOpenException e) {
            if (fallback != null) {
                return fallback.apply(e);
            }
            throw e;
        }
        
        try {
            T result = callable.call();
            onSuccess(currentGen);
            return result;
        } catch (Exception e) {
            if (!(e instanceof CircuitBreakerOpenException)) {
                onError(currentGen);
            }
            if (fallback != null) {
                return fallback.apply(e);
            }
            throw e;
        }
    }

    private int checkState() {
        stateLock.lock();
        try {
            if (state.get() == CircuitBreakerState.OPEN) {
                long now = clock.getAsLong();
                if (now - lastStateTransitionTime >= config.getWaitDurationInOpenState()) {
                    state.set(CircuitBreakerState.HALF_OPEN);
                    halfOpenCalls.set(0);
                    generation.incrementAndGet();
                } else {
                    throw new CircuitBreakerOpenException("Circuit Breaker is OPEN");
                }
            }
            
            if (state.get() == CircuitBreakerState.HALF_OPEN) {
                if (halfOpenCalls.incrementAndGet() > config.getPermittedNumberOfCallsInHalfOpen()) {
                    throw new CircuitBreakerOpenException("Circuit Breaker is HALF_OPEN (No permits left)");
                }
            }
            return generation.get();
        } finally {
            stateLock.unlock();
        }
    }

    private void onSuccess(int gen) {
        stateLock.lock();
        try {
            if (gen != generation.get()) return;

            if (state.get() == CircuitBreakerState.HALF_OPEN) {
                state.set(CircuitBreakerState.CLOSED);
                resetWindow();
                lastStateTransitionTime = clock.getAsLong();
                generation.incrementAndGet();
            } else if (state.get() == CircuitBreakerState.CLOSED) {
                recordResult(true);
            }
        } finally {
            stateLock.unlock();
        }
    }

    private void onError(int gen) {
        stateLock.lock();
        try {
            if (gen != generation.get()) return;

            if (state.get() == CircuitBreakerState.HALF_OPEN) {
                state.set(CircuitBreakerState.OPEN);
                lastStateTransitionTime = clock.getAsLong();
                generation.incrementAndGet();
            } else if (state.get() == CircuitBreakerState.CLOSED) {
                recordResult(false);
                if (calculateFailureRate() >= config.getFailureRateThreshold()) {
                    state.set(CircuitBreakerState.OPEN);
                    lastStateTransitionTime = clock.getAsLong();
                    generation.incrementAndGet();
                }
            }
        } finally {
            stateLock.unlock();
        }
    }

    private void recordResult(boolean success) {
        long now = clock.getAsLong();
        Bucket currentBucket = getCurrentBucket(now);
        if (success) {
            currentBucket.successCount.incrementAndGet();
        } else {
            currentBucket.failureCount.incrementAndGet();
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
                     Bucket oldest = buckets[0];
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

    private int calculateFailureRate() {
        windowLock.lock();
        try {
            int totalCalls = 0;
            int totalFailures = 0;
            
            long now = clock.getAsLong();
            long windowStart = now - (buckets.length * bucketSizeInMs);
            
            for (Bucket b : buckets) {
                if (b != null && b.startTime >= windowStart) {
                    totalCalls += b.successCount.get() + b.failureCount.get();
                    totalFailures += b.failureCount.get();
                }
            }
            
            if (totalCalls == 0) return 0;
            return (totalFailures * 100) / totalCalls;
        } finally {
            windowLock.unlock();
        }
    }

    private void resetWindow() {
        windowLock.lock();
        try {
             long now = clock.getAsLong();
             for (int i = 0; i < buckets.length; i++) {
                 buckets[i] = new Bucket(now - (buckets.length - i) * bucketSizeInMs);
             }
        } finally {
             windowLock.unlock();
        }
    }

    public CircuitBreakerState getState() {
        return state.get();
    }
}
