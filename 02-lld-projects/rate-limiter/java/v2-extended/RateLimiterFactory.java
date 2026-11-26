/**
 * Rate Limiter - V2 Extended
 * 
 * Factory for creating rate limiters with different algorithms.
 */
public class RateLimiterFactory {

    /**
     * Create a rate limiter using Token Bucket algorithm.
     * 
     * Best for: APIs that want to allow bursts up to capacity
     */
    public static RateLimiter createTokenBucketLimiter(RateLimitConfig config) {
        return new RateLimiter(new TokenBucket(), config);
    }

    /**
     * Create a rate limiter using Sliding Window Log algorithm.
     * 
     * Best for: Exact rate limiting with no burst allowance
     * Note: Higher memory usage - stores all request timestamps
     */
    public static RateLimiter createSlidingWindowLogLimiter(RateLimitConfig config) {
        return new RateLimiter(new SlidingWindowLog(), config);
    }

    /**
     * Create a rate limiter for a specific number of requests per second.
     * Uses Token Bucket by default.
     */
    public static RateLimiter perSecond(int requestsPerSecond) {
        RateLimitConfig config = RateLimitConfig.perSecond(requestsPerSecond);
        return createTokenBucketLimiter(config);
    }

    /**
     * Create a rate limiter for a specific number of requests per minute.
     * Uses Token Bucket by default.
     */
    public static RateLimiter perMinute(int requestsPerMinute) {
        RateLimitConfig config = RateLimitConfig.perMinute(requestsPerMinute);
        return createTokenBucketLimiter(config);
    }
}
