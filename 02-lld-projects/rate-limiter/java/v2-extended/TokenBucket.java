/**
 * Rate Limiter - V1 Basic
 * 
 * Token Bucket algorithm - core implementation.
 * Tokens are added at a constant rate and consumed by requests.
 */

/**
 * State for a single client's token bucket.
 */
class TokenBucketState {
    private double tokens;
    private long lastRefillTimeMs;

    public TokenBucketState(double initialTokens) {
        this.tokens = initialTokens;
        this.lastRefillTimeMs = System.currentTimeMillis();
    }

    public double getTokens() {
        return tokens;
    }

    public void setTokens(double tokens) {
        this.tokens = tokens;
    }

    public long getLastRefillTimeMs() {
        return lastRefillTimeMs;
    }

    public void setLastRefillTimeMs(long lastRefillTimeMs) {
        this.lastRefillTimeMs = lastRefillTimeMs;
    }
}

/**
 * Token Bucket rate limiting algorithm.
 * 
 * Properties:
 * - Allows burst up to bucket capacity
 * - Smooth rate limiting over time
 * - O(1) time and space per operation
 */
class TokenBucket {
    private final RateLimitConfig config;

    public TokenBucket(RateLimitConfig config) {
        this.config = config;
    }

    /**
     * Create initial state for a new client.
     */
    public TokenBucketState createInitialState() {
        return new TokenBucketState(config.getBucketCapacity());
    }

    /**
     * Refill tokens based on elapsed time.
     */
    private void refillTokens(TokenBucketState state, long currentTimeMs) {
        long elapsedMs = currentTimeMs - state.getLastRefillTimeMs();
        
        if (elapsedMs > 0) {
            double tokensToAdd = elapsedMs * config.getRefillRatePerMs();
            double newTokens = Math.min(
                config.getBucketCapacity(),
                state.getTokens() + tokensToAdd
            );
            state.setTokens(newTokens);
            state.setLastRefillTimeMs(currentTimeMs);
        }
    }

    /**
     * Try to acquire a token for a request.
     */
    public RateLimitResult tryAcquire(TokenBucketState state) {
        long currentTimeMs = System.currentTimeMillis();
        
        // Refill tokens based on elapsed time
        refillTokens(state, currentTimeMs);
        
        if (state.getTokens() >= 1.0) {
            // Consume a token
            state.setTokens(state.getTokens() - 1.0);
            
            return new RateLimitResult(
                true,
                (int) state.getTokens(),
                calculateResetTime(currentTimeMs)
            );
        } else {
            // No tokens available
            long waitTimeMs = (long) ((1.0 - state.getTokens()) / config.getRefillRatePerMs());
            
            return new RateLimitResult(
                false,
                0,
                currentTimeMs + waitTimeMs
            );
        }
    }

    /**
     * Get remaining tokens without consuming.
     */
    public int getRemainingTokens(TokenBucketState state) {
        long currentTimeMs = System.currentTimeMillis();
        refillTokens(state, currentTimeMs);
        return (int) state.getTokens();
    }

    private long calculateResetTime(long currentTimeMs) {
        // Reset when bucket would be full
        return currentTimeMs + (long) (config.getBucketCapacity() / config.getRefillRatePerMs());
    }
}
