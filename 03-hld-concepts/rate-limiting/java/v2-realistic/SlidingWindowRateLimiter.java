import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * V2: Sliding Window Counter Rate Limiter
 * 
 * A more accurate rate limiter using sliding window counter algorithm.
 * Combines the accuracy of sliding window with low memory overhead.
 * 
 * Features:
 * - Per-user rate limiting
 * - Sliding window for accuracy
 * - Configurable limits
 * - Statistics tracking
 * 
 * Algorithm:
 * - Divide time into fixed windows
 * - Weight previous window by overlap percentage
 * - weighted_count = prev_count * overlap + current_count
 */
public class SlidingWindowRateLimiter {
    
    private final long windowSizeMs;
    private final long maxRequests;
    private final ConcurrentHashMap<String, UserWindow> userWindows;
    
    // Statistics
    private final AtomicLong totalAllowed = new AtomicLong(0);
    private final AtomicLong totalRejected = new AtomicLong(0);
    
    /**
     * Window state for a single user.
     */
    private static class UserWindow {
        volatile long windowStart;
        volatile long prevCount;
        volatile long currCount;
        
        UserWindow(long windowStart) {
            this.windowStart = windowStart;
            this.prevCount = 0;
            this.currCount = 0;
        }
    }
    
    /**
     * Creates a sliding window rate limiter.
     * 
     * @param maxRequestsPerWindow Maximum requests per window
     * @param windowSizeSeconds Window size in seconds
     */
    public SlidingWindowRateLimiter(long maxRequestsPerWindow, int windowSizeSeconds) {
        this.maxRequests = maxRequestsPerWindow;
        this.windowSizeMs = windowSizeSeconds * 1000L;
        this.userWindows = new ConcurrentHashMap<>();
    }
    
    /**
     * Checks if a request should be allowed.
     * 
     * @param userId User identifier
     * @return RateLimitResult with allowed status and metadata
     */
    public RateLimitResult tryAcquire(String userId) {
        long now = System.currentTimeMillis();
        
        UserWindow window = userWindows.computeIfAbsent(
            userId, 
            k -> new UserWindow(now)
        );
        
        synchronized (window) {
            // Slide window if needed
            slideWindow(window, now);
            
            // Calculate weighted count
            double prevWeight = getPreviousWindowWeight(window, now);
            double weightedCount = window.prevCount * prevWeight + window.currCount;
            
            if (weightedCount < maxRequests) {
                window.currCount++;
                totalAllowed.incrementAndGet();
                return new RateLimitResult(true, 
                    maxRequests - (long)weightedCount - 1,
                    maxRequests,
                    getWindowResetTime(window));
            } else {
                totalRejected.incrementAndGet();
                long retryAfterMs = getRetryAfterMs(window, now, prevWeight);
                return new RateLimitResult(false, 0, maxRequests, retryAfterMs);
            }
        }
    }
    
    /**
     * Slides the window forward if current window has passed.
     */
    private void slideWindow(UserWindow window, long now) {
        long windowStart = window.windowStart;
        long elapsed = now - windowStart;
        
        if (elapsed >= windowSizeMs * 2) {
            // Both windows expired
            window.windowStart = now;
            window.prevCount = 0;
            window.currCount = 0;
        } else if (elapsed >= windowSizeMs) {
            // Previous window expired, current becomes previous
            window.windowStart = windowStart + windowSizeMs;
            window.prevCount = window.currCount;
            window.currCount = 0;
        }
    }
    
    /**
     * Gets the weight of the previous window based on overlap.
     */
    private double getPreviousWindowWeight(UserWindow window, long now) {
        long elapsedInWindow = now - window.windowStart;
        return 1.0 - ((double) elapsedInWindow / windowSizeMs);
    }
    
    /**
     * Gets time until window resets (for headers).
     */
    private long getWindowResetTime(UserWindow window) {
        return window.windowStart + windowSizeMs - System.currentTimeMillis();
    }
    
    /**
     * Estimates time until a request would be allowed.
     */
    private long getRetryAfterMs(UserWindow window, long now, double prevWeight) {
        // Simplified: return time until prev window fully expires
        return (long) (prevWeight * windowSizeMs);
    }
    
    /**
     * Gets statistics.
     */
    public Stats getStats() {
        return new Stats(totalAllowed.get(), totalRejected.get());
    }
    
    /**
     * Result of a rate limit check.
     */
    public static class RateLimitResult {
        private final boolean allowed;
        private final long remaining;
        private final long limit;
        private final long retryAfterMs;
        
        public RateLimitResult(boolean allowed, long remaining, long limit, long retryAfterMs) {
            this.allowed = allowed;
            this.remaining = remaining;
            this.limit = limit;
            this.retryAfterMs = retryAfterMs;
        }
        
        public boolean isAllowed() { return allowed; }
        public long getRemaining() { return remaining; }
        public long getLimit() { return limit; }
        public long getRetryAfterMs() { return retryAfterMs; }
        
        @Override
        public String toString() {
            return String.format("RateLimitResult{allowed=%s, remaining=%d, limit=%d}",
                allowed, remaining, limit);
        }
    }
    
    /**
     * Statistics.
     */
    public static class Stats {
        private final long allowed;
        private final long rejected;
        
        public Stats(long allowed, long rejected) {
            this.allowed = allowed;
            this.rejected = rejected;
        }
        
        public long getAllowed() { return allowed; }
        public long getRejected() { return rejected; }
        
        public double getAcceptanceRate() {
            long total = allowed + rejected;
            return total == 0 ? 100.0 : (allowed * 100.0) / total;
        }
        
        @Override
        public String toString() {
            return String.format("Stats{allowed=%d, rejected=%d, acceptanceRate=%.1f%%}",
                allowed, rejected, getAcceptanceRate());
        }
    }
}
