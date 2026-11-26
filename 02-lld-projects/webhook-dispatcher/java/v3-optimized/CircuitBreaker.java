
public class CircuitBreaker {
    private final int failureThreshold;
    private final long cooldownMs;
    private int failures = 0;
    
    public enum State { CLOSED, OPEN, HALF_OPEN }
    private State state = State.CLOSED;
    private long lastFailureTime = 0;

    public CircuitBreaker(int failureThreshold, long cooldownMs) {
        this.failureThreshold = failureThreshold;
        this.cooldownMs = cooldownMs;
    }

    public synchronized boolean allowRequest() {
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - lastFailureTime > cooldownMs) {
                state = State.HALF_OPEN;
                return true;
            }
            return false;
        }
        return true;
    }

    public synchronized void recordSuccess() {
        failures = 0;
        state = State.CLOSED;
    }

    public synchronized void recordFailure() {
        failures++;
        if (failures >= failureThreshold) {
            state = State.OPEN;
            lastFailureTime = System.currentTimeMillis();
        }
    }
    
    public State getState() {
        return state;
    }
}
