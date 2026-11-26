/**
 * Rate Limiter - V1 Basic
 * 
 * Token Bucket algorithm - core implementation.
 * Tokens are added at a constant rate and consumed by requests.
 */

import java.util.concurrent.atomic.AtomicReference;

class TokenBucketStateData {
    final double tokens;
    final long lastRefillTimeMs;

    TokenBucketStateData(double tokens, long lastRefillTimeMs) {
        this.tokens = tokens;
        this.lastRefillTimeMs = lastRefillTimeMs;
    }
}

/**
 * State for a single client's token bucket.
 */
class TokenBucketState {
    private final AtomicReference<TokenBucketStateData> stateRef;

    public TokenBucketState(double initialTokens) {
        this.stateRef = new AtomicReference<>(
            new TokenBucketStateData(initialTokens, System.currentTimeMillis())
        );
    }

    public AtomicReference<TokenBucketStateData> getStateRef() {
        return stateRef;
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

    private TokenBucketStateData calculateRefill(TokenBucketStateData current, long currentTimeMs) {
        long elapsedMs = currentTimeMs - current.lastRefillTimeMs;
        if (elapsedMs > 0) {
            double tokensToAdd = elapsedMs * config.getRefillRatePerMs();
            double newTokens = Math.min(
                config.getBucketCapacity(),
                current.tokens + tokensToAdd
            );
            return new TokenBucketStateData(newTokens, currentTimeMs);
        }
        return current;
    }

    /**
     * Try to acquire a token for a request.
     */
    public RateLimitResult tryAcquire(TokenBucketState state) {
        while (true) {
            long currentTimeMs = System.currentTimeMillis();
            TokenBucketStateData current = state.getStateRef().get();
            TokenBucketStateData refilled = calculateRefill(current, currentTimeMs);

            if (refilled.tokens >= 1.0) {
                TokenBucketStateData next = new TokenBucketStateData(
                    refilled.tokens - 1.0,
                    refilled.lastRefillTimeMs
                );
                
                if (state.getStateRef().compareAndSet(current, next)) {
                    return new RateLimitResult(
                        true,
                        (int) next.tokens,
                        calculateResetTime(currentTimeMs)
                    );
                }
            } else {
                if (current != refilled) {
                    state.getStateRef().compareAndSet(current, refilled);
                }
                long waitTimeMs = (long) ((1.0 - refilled.tokens) / config.getRefillRatePerMs());
                return new RateLimitResult(
                    false,
                    0,
                    currentTimeMs + waitTimeMs
                );
            }
        }
    }

    /**
     * Get remaining tokens without consuming.
     */
    public int getRemainingTokens(TokenBucketState state) {
        long currentTimeMs = System.currentTimeMillis();
        TokenBucketStateData current = state.getStateRef().get();
        TokenBucketStateData refilled = calculateRefill(current, currentTimeMs);
        return (int) refilled.tokens;
    }

    private long calculateResetTime(long currentTimeMs) {
        // Reset when bucket would be full
        return currentTimeMs + (long) (config.getBucketCapacity() / config.getRefillRatePerMs());
    }
}
