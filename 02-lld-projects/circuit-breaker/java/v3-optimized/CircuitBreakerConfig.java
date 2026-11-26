public class CircuitBreakerConfig {
    private final int failureRateThreshold;
    private final int slidingWindowSize;
    private final long waitDurationInOpenState;
    private final int permittedNumberOfCallsInHalfOpen;
    private final int slowCallRateThreshold;
    private final long slowCallDurationThresholdMs;

    public CircuitBreakerConfig(int failureRateThreshold, int slidingWindowSize, long waitDurationInOpenState, int permittedNumberOfCallsInHalfOpen, int slowCallRateThreshold, long slowCallDurationThresholdMs) {
        this.failureRateThreshold = failureRateThreshold;
        this.slidingWindowSize = slidingWindowSize;
        this.waitDurationInOpenState = waitDurationInOpenState;
        this.permittedNumberOfCallsInHalfOpen = permittedNumberOfCallsInHalfOpen;
        this.slowCallRateThreshold = slowCallRateThreshold;
        this.slowCallDurationThresholdMs = slowCallDurationThresholdMs;
    }

    public int getFailureRateThreshold() { return failureRateThreshold; }
    public int getSlidingWindowSize() { return slidingWindowSize; }
    public long getWaitDurationInOpenState() { return waitDurationInOpenState; }
    public int getPermittedNumberOfCallsInHalfOpen() { return permittedNumberOfCallsInHalfOpen; }
    public int getSlowCallRateThreshold() { return slowCallRateThreshold; }
    public long getSlowCallDurationThresholdMs() { return slowCallDurationThresholdMs; }
}
