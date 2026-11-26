package v1_basic;

public class CircuitBreaker {
    public enum State { CLOSED, OPEN, HALF_OPEN }
    
    private State state = State.CLOSED;
    private int failureCount = 0;
    private final int threshold = 3;
    
    public synchronized boolean allowRequest() {
        if (state == State.OPEN) {
            return false;
        }
        return true;
    }
    
    public synchronized void recordSuccess() {
        failureCount = 0;
        state = State.CLOSED;
    }
    
    public synchronized void recordFailure() {
        failureCount++;
        if (failureCount >= threshold) {
            state = State.OPEN;
        }
    }
    
    // For test simulation
    public synchronized void tripOpen() {
        state = State.OPEN;
    }
    
    public synchronized void reset() {
        state = State.CLOSED;
        failureCount = 0;
    }
}
