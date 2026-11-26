import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.LongSupplier;

public class CircuitBreaker {
    private final CircuitBreakerConfig config;
    private final AtomicReference<CircuitBreakerState> state;
    private volatile long lastStateTransitionTime;
    private volatile long generation;
    private final LongSupplier clock;
    
    // Simplistic circular buffer for count-based window
    private final boolean[] window;
    private final AtomicInteger windowIndex = new AtomicInteger(0);
    private final AtomicInteger currentCalls = new AtomicInteger(0);
    
    private final AtomicInteger halfOpenCalls = new AtomicInteger(0);

    public CircuitBreaker(CircuitBreakerConfig config) {
        this(config, System::currentTimeMillis);
    }
    
    public CircuitBreaker(CircuitBreakerConfig config, LongSupplier clock) {
        this.config = config;
        this.state = new AtomicReference<>(CircuitBreakerState.CLOSED);
        this.window = new boolean[config.getSlidingWindowSize()];
        this.clock = clock;
        this.generation = 0;
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
        
        try {
            T result = callable.call();
            onSuccess(callGeneration);
            return result;
        } catch (Exception e) {
            // Do not record fast-fail exception as backend failure
            if (!(e instanceof CircuitBreakerOpenException)) {
                onError(callGeneration);
            }
            if (fallback != null) {
                return fallback.apply(e);
            }
            throw e;
        }
    }

    private synchronized long checkState() {
        if (state.get() == CircuitBreakerState.OPEN) {
            long now = clock.getAsLong();
            if (now - lastStateTransitionTime >= config.getWaitDurationInOpenState()) {
                state.set(CircuitBreakerState.HALF_OPEN);
                halfOpenCalls.set(0);
                generation++;
            } else {
                throw new CircuitBreakerOpenException("Circuit Breaker is OPEN");
            }
        }
        
        if (state.get() == CircuitBreakerState.HALF_OPEN) {
            if (halfOpenCalls.incrementAndGet() > config.getPermittedNumberOfCallsInHalfOpen()) {
                throw new CircuitBreakerOpenException("Circuit Breaker is HALF_OPEN (No permits left)");
            }
        }
        return generation;
    }

    private synchronized void onSuccess(long callGeneration) {
        if (generation != callGeneration) return;
        if (state.get() == CircuitBreakerState.HALF_OPEN) {
            transitionToClosed();
        } else if (state.get() == CircuitBreakerState.CLOSED) {
            recordResult(true);
        }
    }

    private synchronized void onError(long callGeneration) {
        if (generation != callGeneration) return;
        if (state.get() == CircuitBreakerState.HALF_OPEN) {
            transitionToOpen();
        } else if (state.get() == CircuitBreakerState.CLOSED) {
            recordResult(false);
            if (currentCalls.get() >= config.getSlidingWindowSize() && calculateFailureRate() >= config.getFailureRateThreshold()) {
                transitionToOpen();
            }
        }
    }

    private void recordResult(boolean success) {
        int idx = windowIndex.getAndIncrement() % window.length;
        window[idx] = success;
        if (currentCalls.get() < window.length) {
            currentCalls.incrementAndGet();
        }
    }

    private int calculateFailureRate() {
        int failures = 0;
        for (int i = 0; i < currentCalls.get(); i++) {
            if (!window[i]) {
                failures++;
            }
        }
        return (failures * 100) / currentCalls.get();
    }

    private void transitionToClosed() {
        state.set(CircuitBreakerState.CLOSED);
        currentCalls.set(0);
        windowIndex.set(0);
        lastStateTransitionTime = clock.getAsLong();
        generation++;
    }

    private void transitionToOpen() {
        state.set(CircuitBreakerState.OPEN);
        lastStateTransitionTime = clock.getAsLong();
        generation++;
    }

    public CircuitBreakerState getState() {
        return state.get();
    }
}
