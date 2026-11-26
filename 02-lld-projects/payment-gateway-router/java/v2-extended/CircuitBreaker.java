
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import java.util.concurrent.atomic.AtomicInteger;

public class CircuitBreaker {
    public enum State {
        CLOSED, OPEN, HALF_OPEN
    }

    private State state = State.CLOSED;
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final int failureThreshold;
    private final long resetTimeoutMs;
    private long lastFailureTime;

    public CircuitBreaker(int failureThreshold, long resetTimeoutMs) {
        this.failureThreshold = failureThreshold;
        this.resetTimeoutMs = resetTimeoutMs;
    }

    public synchronized boolean allowRequest() {
        if (state == State.CLOSED) {
            return true;
        }

        if (state == State.OPEN) {
            if (System.currentTimeMillis() - lastFailureTime >= resetTimeoutMs) {
                state = State.HALF_OPEN;
                return true;
            }
            return false;
        }

        // State is HALF_OPEN, allow one request to test
        return true;
    }

    public synchronized void recordSuccess() {
        failureCount.set(0);
        state = State.CLOSED;
    }

    public synchronized void recordFailure() {
        lastFailureTime = System.currentTimeMillis();
        int failures = failureCount.incrementAndGet();
        
        if (failures >= failureThreshold) {
            state = State.OPEN;
        }
    }
}
