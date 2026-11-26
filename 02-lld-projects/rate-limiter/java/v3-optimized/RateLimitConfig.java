/**
 * Rate Limiter - V1 Basic
 * 
 * Token Bucket algorithm implementation.
 * Simple rate limiting with configurable bucket size and refill rate.
 */

/**
 * Result of a rate limit check.
 */
class RateLimitResult {
    private final boolean allowed;
    private final int remainingTokens;
    private final long resetTimeMs;

    public RateLimitResult(boolean allowed, int remainingTokens, long resetTimeMs) {
        this.allowed = allowed;
        this.remainingTokens = remainingTokens;
        this.resetTimeMs = resetTimeMs;
    }

    public boolean isAllowed() {
        return allowed;
    }

    public int getRemainingTokens() {
        return remainingTokens;
    }

    public long getResetTimeMs() {
        return resetTimeMs;
    }

    @Override
    public String toString() {
        return String.format("RateLimitResult{allowed=%s, remaining=%d, resetMs=%d}",
                allowed, remainingTokens, resetTimeMs);
    }
}

/**
 * Configuration for rate limiting.
 */
class RateLimitConfig {
    private final int bucketCapacity;      // Maximum tokens in bucket
    private final double refillRatePerMs;  // Tokens added per millisecond

    public RateLimitConfig(int bucketCapacity, int refillPerSecond) {
        this.bucketCapacity = bucketCapacity;
        this.refillRatePerMs = refillPerSecond / 1000.0;
    }

    public int getBucketCapacity() {
        return bucketCapacity;
    }

    public double getRefillRatePerMs() {
        return refillRatePerMs;
    }

    /**
     * Create a config for X requests per second.
     */
    public static RateLimitConfig perSecond(int requestsPerSecond) {
        return new RateLimitConfig(requestsPerSecond, requestsPerSecond);
    }

    /**
     * Create a config for X requests per minute.
     */
    public static RateLimitConfig perMinute(int requestsPerMinute) {
        // Allow burst up to per-second equivalent, refill over minute
        int burstCapacity = Math.max(1, requestsPerMinute / 60);
        return new RateLimitConfig(burstCapacity, requestsPerMinute / 60);
    }
}
