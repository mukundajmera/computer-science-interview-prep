public class CircuitBreakerConfig {
    private final int failureRateThreshold;
    private final int slidingWindowSize;
    private final long waitDurationInOpenState;
    private final int permittedNumberOfCallsInHalfOpen;

    public CircuitBreakerConfig(int failureRateThreshold, int slidingWindowSize, long waitDurationInOpenState, int permittedNumberOfCallsInHalfOpen, int slowCallRateThreshold, long slowCallDurationThresholdMs) {
        this.failureRateThreshold = failureRateThreshold;
        this.slidingWindowSize = slidingWindowSize;
        this.waitDurationInOpenState = waitDurationInOpenState;
        this.permittedNumberOfCallsInHalfOpen = permittedNumberOfCallsInHalfOpen;
    }

    public int getFailureRateThreshold() { return failureRateThreshold; }
    public int getSlidingWindowSize() { return slidingWindowSize; }
    public long getWaitDurationInOpenState() { return waitDurationInOpenState; }
    public int getPermittedNumberOfCallsInHalfOpen() { return permittedNumberOfCallsInHalfOpen; }
}
