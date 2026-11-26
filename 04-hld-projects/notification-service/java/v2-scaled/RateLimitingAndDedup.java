/**
 * Notification Service - V2 Scaled
 * 
 * Rate limiting and deduplication.
 */

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

/**
 * Rate limiter for providers.
 */
class ProviderRateLimiter {
    
    private final Map<String, TokenBucket> buckets = new ConcurrentHashMap<>();
    
    /**
     * Configure rate limit for a provider.
     */
    public void configure(String providerId, int requestsPerSecond) {
        buckets.put(providerId, new TokenBucket(requestsPerSecond, requestsPerSecond));
    }
    
    /**
     * Check if request is allowed for provider.
     */
    public boolean allowRequest(String providerId) {
        TokenBucket bucket = buckets.get(providerId);
        if (bucket == null) {
            return true; // No limit configured
        }
        return bucket.tryConsume();
    }
    
    /**
     * Wait for rate limit to allow request.
     */
    public void waitForSlot(String providerId) throws InterruptedException {
        while (!allowRequest(providerId)) {
            Thread.sleep(10);
        }
    }
    
    private static class TokenBucket {
        private final int capacity;
        private final int refillRate;
        private double tokens;
        private long lastRefill;
        
        TokenBucket(int capacity, int refillRate) {
            this.capacity = capacity;
            this.refillRate = refillRate;
            this.tokens = capacity;
            this.lastRefill = System.currentTimeMillis();
        }
        
        synchronized boolean tryConsume() {
            refill();
            if (tokens >= 1) {
                tokens -= 1;
                return true;
            }
            return false;
        }
        
        private void refill() {
            long now = System.currentTimeMillis();
            double elapsed = (now - lastRefill) / 1000.0;
            tokens = Math.min(capacity, tokens + (elapsed * refillRate));
            lastRefill = now;
        }
    }
}

/**
 * Deduplication service to prevent duplicate notifications.
 */
class DeduplicationService {
    
    // In production: Use Redis with TTL
    private final Map<String, String> idempotencyStore = new ConcurrentHashMap<>();
    private final Map<String, Long> contentHashes = new ConcurrentHashMap<>();
    
    private static final long IDEMPOTENCY_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours
    private static final long CONTENT_DEDUP_WINDOW_MS = 60 * 60 * 1000; // 1 hour
    
    /**
     * Check if notification with this idempotency key was already processed.
     * @return Existing notification ID if duplicate, null if new
     */
    public String checkIdempotencyKey(String idempotencyKey) {
        if (idempotencyKey == null || idempotencyKey.isEmpty()) {
            return null;
        }
        return idempotencyStore.get(idempotencyKey);
    }
    
    /**
     * Store idempotency key after processing.
     */
    public void storeIdempotencyKey(String idempotencyKey, String notificationId) {
        if (idempotencyKey != null && !idempotencyKey.isEmpty()) {
            idempotencyStore.put(idempotencyKey, notificationId);
        }
    }
    
    /**
     * Check for content-based duplicate within time window.
     */
    public boolean isContentDuplicate(String userId, String templateId, 
                                      String channel, Map<String, String> variables) {
        String hash = computeContentHash(userId, templateId, channel, variables);
        Long previousSend = contentHashes.get(hash);
        
        if (previousSend != null) {
            if (System.currentTimeMillis() - previousSend < CONTENT_DEDUP_WINDOW_MS) {
                return true; // Duplicate within window
            }
        }
        
        contentHashes.put(hash, System.currentTimeMillis());
        return false;
    }
    
    private String computeContentHash(String userId, String templateId,
                                     String channel, Map<String, String> variables) {
        try {
            StringBuilder sb = new StringBuilder();
            sb.append(userId).append("|");
            sb.append(templateId).append("|");
            sb.append(channel).append("|");
            
            // Sort variables for consistent hash
            if (variables != null) {
                variables.entrySet().stream()
                    .sorted(Map.Entry.comparingByKey())
                    .forEach(e -> sb.append(e.getKey()).append("=")
                                   .append(e.getValue()).append(";"));
            }
            
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(sb.toString().getBytes(StandardCharsets.UTF_8));
            
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                hexString.append(String.format("%02x", b));
            }
            return hexString.toString();
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to compute hash", e);
        }
    }
    
    /**
     * Clean up expired entries (call periodically).
     */
    public void cleanup() {
        long now = System.currentTimeMillis();
        
        contentHashes.entrySet().removeIf(e -> 
            now - e.getValue() > CONTENT_DEDUP_WINDOW_MS);
    }
}

/**
 * Circuit breaker for provider failover.
 */
class ProviderCircuitBreaker {
    
    private final int failureThreshold;
    private final long resetTimeMs;
    
    private int failureCount = 0;
    private long lastFailureTime = 0;
    private boolean open = false;
    
    public ProviderCircuitBreaker(int failureThreshold, long resetTimeMs) {
        this.failureThreshold = failureThreshold;
        this.resetTimeMs = resetTimeMs;
    }
    
    public synchronized boolean isOpen() {
        if (open && System.currentTimeMillis() - lastFailureTime > resetTimeMs) {
            open = false;
            failureCount = 0;
        }
        return open;
    }
    
    public synchronized void recordSuccess() {
        failureCount = 0;
        open = false;
    }
    
    public synchronized void recordFailure() {
        failureCount++;
        lastFailureTime = System.currentTimeMillis();
        
        if (failureCount >= failureThreshold) {
            open = true;
        }
    }
}
