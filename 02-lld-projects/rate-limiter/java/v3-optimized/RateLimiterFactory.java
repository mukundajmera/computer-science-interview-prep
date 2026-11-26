/**
 * Rate Limiter - V3 Optimized
 * 
 * Factory for creating rate limiters with different algorithms.
 */
public class RateLimiterFactory {

    /**
     * Create a rate limiter using Sliding Window Counter algorithm.
     * 
     * Best for: Memory-efficient rate limiting with good accuracy
     */
    public static RateLimiter createSlidingWindowCounterLimiter(RateLimitConfig config) {
        return new RateLimiter(new SlidingWindowCounter(), config);
    }

    /**
     * Create a rate limiter using Sliding Window Counter without background cleanup.
     * Use when you want to manage cleanup manually.
     */
    public static RateLimiter createSlidingWindowCounterLimiter(RateLimitConfig config, boolean enableCleanup) {
        return new RateLimiter(new SlidingWindowCounter(), config, config.getWindowSizeMs() * 2, enableCleanup);
    }

    /**
     * Create a rate limiter for a specific number of requests per second.
     */
    public static RateLimiter perSecond(int requestsPerSecond) {
        RateLimitConfig config = RateLimitConfig.perSecond(requestsPerSecond);
        return createSlidingWindowCounterLimiter(config);
    }

    /**
     * Create a rate limiter for a specific number of requests per minute.
     */
    public static RateLimiter perMinute(int requestsPerMinute) {
        RateLimitConfig config = RateLimitConfig.perMinute(requestsPerMinute);
        return createSlidingWindowCounterLimiter(config);
    }
}
