import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.*;

/**
 * V3: Production-Ready Distributed Rate Limiter
 * 
 * A production-grade rate limiter with:
 * - Multi-tier limits (per user, per endpoint, global)
 * - Redis-like storage abstraction
 * - Tiered rate limits (free, premium, enterprise)
 * - Comprehensive metrics
 * - HTTP headers support
 * 
 * This demonstrates patterns used in production API gateways
 * like Kong, AWS API Gateway, and Stripe.
 */
public class DistributedRateLimiter {
    
    private final RateLimitStore store;
    private final Map<String, TierConfig> tiers;
    private final Metrics metrics;
    private final ScheduledExecutorService scheduler;
    
    /**
     * Storage interface for rate limit data.
     * In production, this would be backed by Redis.
     */
    public interface RateLimitStore {
        /**
         * Increments counter and returns new value.
         * Should be atomic operation.
         */
        IncrementResult increment(String key, long windowMs);
        
        /**
         * Gets current count for a key.
         */
        long getCount(String key);
    }
    
    /**
     * Result of an increment operation.
     */
    public static class IncrementResult {
        public final long count;
        public final long ttlMs;
        
        public IncrementResult(long count, long ttlMs) {
            this.count = count;
            this.ttlMs = ttlMs;
        }
    }
    
    /**
     * Configuration for a rate limit tier.
     */
    public static class TierConfig {
        public final String name;
        public final long requestsPerWindow;
        public final long windowMs;
        public final long burstCapacity;
        
        public TierConfig(String name, long requestsPerWindow, int windowSeconds, long burstCapacity) {
            this.name = name;
            this.requestsPerWindow = requestsPerWindow;
            this.windowMs = windowSeconds * 1000L;
            this.burstCapacity = burstCapacity;
        }
    }
    
    /**
     * Rate limit decision.
     */
    public static class RateLimitDecision {
        private final boolean allowed;
        private final String tier;
        private final long limit;
        private final long remaining;
        private final long resetMs;
        private final long retryAfterMs;
        private final String limitedBy;  // Which limit was hit
        
        public RateLimitDecision(boolean allowed, String tier, long limit, 
                                  long remaining, long resetMs, long retryAfterMs,
                                  String limitedBy) {
            this.allowed = allowed;
            this.tier = tier;
            this.limit = limit;
            this.remaining = remaining;
            this.resetMs = resetMs;
            this.retryAfterMs = retryAfterMs;
            this.limitedBy = limitedBy;
        }
        
        public boolean isAllowed() { return allowed; }
        public String getTier() { return tier; }
        public long getLimit() { return limit; }
        public long getRemaining() { return remaining; }
        public long getResetMs() { return resetMs; }
        public long getRetryAfterMs() { return retryAfterMs; }
        public String getLimitedBy() { return limitedBy; }
        
        /**
         * Returns HTTP headers for rate limit response.
         */
        public Map<String, String> getHeaders() {
            Map<String, String> headers = new LinkedHashMap<>();
            headers.put("X-RateLimit-Limit", String.valueOf(limit));
            headers.put("X-RateLimit-Remaining", String.valueOf(Math.max(0, remaining)));
            headers.put("X-RateLimit-Reset", String.valueOf(System.currentTimeMillis() + resetMs));
            if (!allowed) {
                headers.put("Retry-After", String.valueOf(retryAfterMs / 1000));
            }
            return headers;
        }
    }
    
    /**
     * Metrics tracking.
     */
    public static class Metrics {
        private final AtomicLong totalRequests = new AtomicLong();
        private final AtomicLong allowedRequests = new AtomicLong();
        private final AtomicLong rejectedRequests = new AtomicLong();
        private final ConcurrentHashMap<String, AtomicLong> rejectionsByTier = new ConcurrentHashMap<>();
        private final ConcurrentHashMap<String, AtomicLong> rejectionsByUser = new ConcurrentHashMap<>();
        
        public void recordAllowed() {
            totalRequests.incrementAndGet();
            allowedRequests.incrementAndGet();
        }
        
        public void recordRejected(String tier, String userId) {
            totalRequests.incrementAndGet();
            rejectedRequests.incrementAndGet();
            rejectionsByTier.computeIfAbsent(tier, k -> new AtomicLong()).incrementAndGet();
            rejectionsByUser.computeIfAbsent(userId, k -> new AtomicLong()).incrementAndGet();
        }
        
        public long getTotalRequests() { return totalRequests.get(); }
        public long getAllowedRequests() { return allowedRequests.get(); }
        public long getRejectedRequests() { return rejectedRequests.get(); }
        
        public double getAcceptanceRate() {
            long total = totalRequests.get();
            return total == 0 ? 100.0 : (allowedRequests.get() * 100.0) / total;
        }
        
        public Map<String, Long> getRejectionsByTier() {
            Map<String, Long> result = new HashMap<>();
            rejectionsByTier.forEach((k, v) -> result.put(k, v.get()));
            return result;
        }
        
        @Override
        public String toString() {
            return String.format("Metrics{total=%d, allowed=%d, rejected=%d, rate=%.1f%%}",
                getTotalRequests(), getAllowedRequests(), getRejectedRequests(), getAcceptanceRate());
        }
    }
    
    /**
     * Creates a distributed rate limiter.
     */
    public DistributedRateLimiter(RateLimitStore store) {
        this.store = store;
        this.tiers = new ConcurrentHashMap<>();
        this.metrics = new Metrics();
        this.scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "rate-limiter-cleanup");
            t.setDaemon(true);
            return t;
        });
        
        // Add default tiers
        addTier(new TierConfig("free", 100, 60, 10));
        addTier(new TierConfig("basic", 500, 60, 50));
        addTier(new TierConfig("premium", 2000, 60, 200));
        addTier(new TierConfig("enterprise", 10000, 60, 1000));
    }
    
    /**
     * Adds or updates a rate limit tier.
     */
    public void addTier(TierConfig config) {
        tiers.put(config.name, config);
    }
    
    /**
     * Checks rate limit for a request.
     * 
     * @param userId User identifier
     * @param tierName Tier name (free, premium, etc.)
     * @param endpoint Optional endpoint for per-endpoint limits
     * @return Decision with allowed status and headers
     */
    public RateLimitDecision checkRateLimit(String userId, String tierName, String endpoint) {
        TierConfig tier = tiers.get(tierName);
        if (tier == null) {
            tier = tiers.get("free");  // Default to free tier
        }
        
        long now = System.currentTimeMillis();
        long windowStart = now - (now % tier.windowMs);
        
        // Check per-user limit
        String userKey = String.format("rate:%s:%s:%d", tierName, userId, windowStart);
        IncrementResult userResult = store.increment(userKey, tier.windowMs);
        
        if (userResult.count > tier.requestsPerWindow) {
            metrics.recordRejected(tierName, userId);
            return new RateLimitDecision(
                false, tierName, tier.requestsPerWindow,
                0, userResult.ttlMs, userResult.ttlMs,
                "user"
            );
        }
        
        // Optional: Check per-endpoint limit
        if (endpoint != null) {
            String endpointKey = String.format("rate:%s:endpoint:%s:%d", tierName, endpoint, windowStart);
            IncrementResult endpointResult = store.increment(endpointKey, tier.windowMs);
            
            // Endpoint gets higher limits
            long endpointLimit = tier.requestsPerWindow * 10;
            if (endpointResult.count > endpointLimit) {
                metrics.recordRejected(tierName, userId);
                return new RateLimitDecision(
                    false, tierName, endpointLimit,
                    0, endpointResult.ttlMs, endpointResult.ttlMs,
                    "endpoint"
                );
            }
        }
        
        metrics.recordAllowed();
        return new RateLimitDecision(
            true, tierName, tier.requestsPerWindow,
            tier.requestsPerWindow - userResult.count,
            userResult.ttlMs, 0,
            null
        );
    }
    
    /**
     * Simplified check without endpoint limit.
     */
    public RateLimitDecision checkRateLimit(String userId, String tierName) {
        return checkRateLimit(userId, tierName, null);
    }
    
    public Metrics getMetrics() {
        return metrics;
    }
    
    public void shutdown() {
        scheduler.shutdown();
    }
    
    // ================== In-Memory Store Implementation ==================
    
    /**
     * In-memory implementation of RateLimitStore.
     * In production, replace with Redis implementation.
     */
    public static class InMemoryRateLimitStore implements RateLimitStore {
        private final ConcurrentHashMap<String, AtomicLong> counters = new ConcurrentHashMap<>();
        private final ConcurrentHashMap<String, Long> expiries = new ConcurrentHashMap<>();
        
        @Override
        public IncrementResult increment(String key, long windowMs) {
            long now = System.currentTimeMillis();
            
            // Check if key expired
            Long expiry = expiries.get(key);
            if (expiry != null && now > expiry) {
                counters.remove(key);
                expiries.remove(key);
            }
            
            // Increment counter
            AtomicLong counter = counters.computeIfAbsent(key, k -> {
                expiries.put(k, now + windowMs);
                return new AtomicLong(0);
            });
            
            long count = counter.incrementAndGet();
            long ttl = expiries.getOrDefault(key, now + windowMs) - now;
            
            return new IncrementResult(count, Math.max(0, ttl));
        }
        
        @Override
        public long getCount(String key) {
            AtomicLong counter = counters.get(key);
            return counter == null ? 0 : counter.get();
        }
    }
}
