/**
 * V1: Simple Token Bucket Rate Limiter
 * 
 * A basic implementation of the token bucket algorithm.
 * Allows bursting up to bucket capacity while maintaining
 * average rate over time.
 * 
 * Features:
 * - Configurable capacity and refill rate
 * - Thread-safe for single user
 * - Simple API
 * 
 * Limitations:
 * - Single user only
 * - Not distributed
 */
public class TokenBucketRateLimiter {
    
    private final long capacity;          // Max tokens
    private final double refillRatePerMs; // Tokens per millisecond
    private double tokens;                // Current tokens
    private long lastRefillTime;          // Last refill timestamp
    
    /**
     * Creates a token bucket rate limiter.
     * 
     * @param capacity Maximum tokens (burst size)
     * @param refillRatePerSecond Tokens added per second
     */
    public TokenBucketRateLimiter(long capacity, double refillRatePerSecond) {
        this.capacity = capacity;
        this.refillRatePerMs = refillRatePerSecond / 1000.0;
        this.tokens = capacity;  // Start full
        this.lastRefillTime = System.currentTimeMillis();
    }
    
    /**
     * Attempts to consume one token.
     * 
     * @return true if request allowed, false if rate limited
     */
    public synchronized boolean tryAcquire() {
        return tryAcquire(1);
    }
    
    /**
     * Attempts to consume specified number of tokens.
     * 
     * @param tokensNeeded Number of tokens to consume
     * @return true if request allowed, false if rate limited
     */
    public synchronized boolean tryAcquire(int tokensNeeded) {
        refill();
        
        if (tokens >= tokensNeeded) {
            tokens -= tokensNeeded;
            return true;
        }
        
        return false;
    }
    
    /**
     * Refills tokens based on elapsed time.
     */
    private void refill() {
        long now = System.currentTimeMillis();
        long elapsed = now - lastRefillTime;
        
        double tokensToAdd = elapsed * refillRatePerMs;
        tokens = Math.min(capacity, tokens + tokensToAdd);
        lastRefillTime = now;
    }
    
    /**
     * Returns current token count (for monitoring).
     */
    public synchronized double getAvailableTokens() {
        refill();
        return tokens;
    }
    
    /**
     * Returns time until next token is available (in ms).
     */
    public synchronized long getWaitTimeMs() {
        refill();
        if (tokens >= 1) {
            return 0;
        }
        return (long) ((1 - tokens) / refillRatePerMs);
    }
}
