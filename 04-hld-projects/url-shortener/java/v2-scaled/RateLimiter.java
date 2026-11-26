/**
 * URL Shortener - V2 Scaled
 * 
 * Rate limiter for API protection.
 * Implements Token Bucket algorithm.
 */

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Rate limiter interface.
 */
interface RateLimiter {
    /**
     * Check if request should be allowed.
     * @param key The rate limit key (e.g., IP address, user ID)
     * @return true if allowed, false if rate limited
     */
    boolean allowRequest(String key);
    
    /**
     * Get remaining tokens for a key.
     * @param key The rate limit key
     * @return Number of remaining requests
     */
    int getRemainingTokens(String key);
}

/**
 * Token Bucket rate limiter implementation.
 * Allows burst traffic up to bucket capacity.
 */
class TokenBucketRateLimiter implements RateLimiter {
    
    private final int bucketCapacity;    // Max tokens
    private final int refillRate;        // Tokens added per second
    private final Map<String, Bucket> buckets;
    
    public TokenBucketRateLimiter(int bucketCapacity, int refillRate) {
        this.bucketCapacity = bucketCapacity;
        this.refillRate = refillRate;
        this.buckets = new ConcurrentHashMap<>();
    }
    
    @Override
    public boolean allowRequest(String key) {
        Bucket bucket = buckets.computeIfAbsent(key, 
            k -> new Bucket(bucketCapacity, refillRate));
        
        return bucket.tryConsume();
    }
    
    @Override
    public int getRemainingTokens(String key) {
        Bucket bucket = buckets.get(key);
        return bucket != null ? bucket.getTokens() : bucketCapacity;
    }
    
    /**
     * Internal bucket implementation.
     */
    private static class Bucket {
        private final int capacity;
        private final int refillRate;
        private double tokens;
        private long lastRefillTime;
        
        Bucket(int capacity, int refillRate) {
            this.capacity = capacity;
            this.refillRate = refillRate;
            this.tokens = capacity;
            this.lastRefillTime = System.currentTimeMillis();
        }
        
        synchronized boolean tryConsume() {
            refill();
            
            if (tokens >= 1) {
                tokens -= 1;
                return true;
            }
            
            return false;
        }
        
        synchronized int getTokens() {
            refill();
            return (int) tokens;
        }
        
        private void refill() {
            long now = System.currentTimeMillis();
            double secondsElapsed = (now - lastRefillTime) / 1000.0;
            
            tokens = Math.min(capacity, tokens + (secondsElapsed * refillRate));
            lastRefillTime = now;
        }
    }
}

/**
 * Sliding window rate limiter for more accurate rate limiting.
 */
class SlidingWindowRateLimiter implements RateLimiter {
    
    private final int maxRequests;
    private final long windowSizeMs;
    private final Map<String, java.util.LinkedList<Long>> requestLogs;
    
    public SlidingWindowRateLimiter(int maxRequests, long windowSizeMs) {
        this.maxRequests = maxRequests;
        this.windowSizeMs = windowSizeMs;
        this.requestLogs = new ConcurrentHashMap<>();
    }
    
    @Override
    public synchronized boolean allowRequest(String key) {
        long now = System.currentTimeMillis();
        long windowStart = now - windowSizeMs;
        
        java.util.LinkedList<Long> log = requestLogs.computeIfAbsent(key, 
            k -> new java.util.LinkedList<>());
        
        // Remove expired entries
        while (!log.isEmpty() && log.peekFirst() < windowStart) {
            log.pollFirst();
        }
        
        if (log.size() < maxRequests) {
            log.addLast(now);
            return true;
        }
        
        return false;
    }
    
    @Override
    public int getRemainingTokens(String key) {
        java.util.LinkedList<Long> log = requestLogs.get(key);
        
        if (log == null) {
            return maxRequests;
        }
        
        long now = System.currentTimeMillis();
        long windowStart = now - windowSizeMs;
        
        synchronized (log) {
            // Count valid entries
            int count = 0;
            for (Long timestamp : log) {
                if (timestamp >= windowStart) {
                    count++;
                }
            }
            return Math.max(0, maxRequests - count);
        }
    }
}
