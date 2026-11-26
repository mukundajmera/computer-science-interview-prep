import java.util.HashMap;
import java.util.Map;

/**
 * Rate Limiter - V1 Basic
 * 
 * Main rate limiter class using Token Bucket algorithm.
 * Simple implementation for single-threaded use.
 */
public class RateLimiter {
    private final TokenBucket algorithm;
    private final Map<String, TokenBucketState> clientStates;

    public RateLimiter(RateLimitConfig config) {
        this.algorithm = new TokenBucket(config);
        this.clientStates = new HashMap<>();
    }

    /**
     * Check if a request from the given client should be allowed.
     * 
     * @param clientKey Unique identifier for the client (user ID, IP, API key)
     * @return RateLimitResult indicating if request is allowed
     */
    public RateLimitResult allowRequest(String clientKey) {
        if (clientKey == null || clientKey.isEmpty()) {
            throw new IllegalArgumentException("Client key cannot be null or empty");
        }

        TokenBucketState state = getOrCreateState(clientKey);
        return algorithm.tryAcquire(state);
    }

    /**
     * Get remaining requests for a client without consuming quota.
     */
    public int getRemainingRequests(String clientKey) {
        TokenBucketState state = clientStates.get(clientKey);
        if (state == null) {
            return algorithm.getRemainingTokens(algorithm.createInitialState());
        }
        return algorithm.getRemainingTokens(state);
    }

    /**
     * Reset rate limit state for a client.
     */
    public void resetClient(String clientKey) {
        clientStates.remove(clientKey);
    }

    /**
     * Get or create state for a client.
     */
    private TokenBucketState getOrCreateState(String clientKey) {
        return clientStates.computeIfAbsent(clientKey, k -> algorithm.createInitialState());
    }

    /**
     * Get the number of tracked clients.
     */
    public int getClientCount() {
        return clientStates.size();
    }
}
