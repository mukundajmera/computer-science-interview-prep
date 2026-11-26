/**
 * Rate Limiter - V2 Extended
 * 
 * Strategy interface for rate limiting algorithms.
 */
public interface RateLimitAlgorithm {
    
    /**
     * Get the name of this algorithm.
     */
    String getAlgorithmName();
    
    /**
     * Create initial state for a new client.
     */
    ClientState createInitialState();
    
    /**
     * Try to acquire permission for a request.
     * 
     * @param state The client's current state
     * @param config Rate limit configuration
     * @return Result indicating if request is allowed
     */
    RateLimitResult tryAcquire(ClientState state, RateLimitConfig config);
    
    /**
     * Get remaining requests without consuming quota.
     */
    int getRemainingRequests(ClientState state, RateLimitConfig config);
}

/**
 * Base interface for client state.
 */
interface ClientState {
    /**
     * When this state was created.
     */
    long getCreatedAt();
    
    /**
     * Approximate memory usage in bytes.
     */
    int getMemoryUsage();
}
