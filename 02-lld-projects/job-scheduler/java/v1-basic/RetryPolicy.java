package v1_basic;

public class RetryPolicy {
    private final int maxRetries;
    private final long initialBackoffMs;
    private final double multiplier;

    public RetryPolicy(int maxRetries, long initialBackoffMs, double multiplier) {
        this.maxRetries = maxRetries;
        this.initialBackoffMs = initialBackoffMs;
        this.multiplier = multiplier;
    }

    public int getMaxRetries() { return maxRetries; }
    public long getInitialBackoffMs() { return initialBackoffMs; }
    public double getMultiplier() { return multiplier; }
}
