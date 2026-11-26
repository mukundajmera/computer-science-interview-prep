import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Rate Limiter - V2 Extended
 * 
 * Sliding Window Log algorithm.
 * Stores exact timestamps of all requests within the window.
 * 
 * Properties:
 * - Exact request counting
 * - Memory usage proportional to request count
 * - No burst allowance - strict limit
 */
public class SlidingWindowLog implements RateLimitAlgorithm {
    private static final String ALGORITHM_NAME = "SlidingWindowLog";

    @Override
    public String getAlgorithmName() {
        return ALGORITHM_NAME;
    }

    @Override
    public ClientState createInitialState() {
        return new SlidingWindowLogState();
    }

    @Override
    public RateLimitResult tryAcquire(ClientState state, RateLimitConfig config) {
        if (!(state instanceof SlidingWindowLogState)) {
            throw new IllegalArgumentException("Invalid state type for SlidingWindowLog");
        }

        SlidingWindowLogState logState = (SlidingWindowLogState) state;
        long currentTimeMs = System.currentTimeMillis();
        long windowStartMs = currentTimeMs - config.getWindowSizeMs();

        // Remove timestamps outside the current window
        cleanOldEntries(logState, windowStartMs);

        int currentCount = logState.getRequestCount();

        if (currentCount < config.getMaxRequests()) {
            // Allow request - add timestamp
            logState.addRequest(currentTimeMs);

            return RateLimitResult.builder()
                    .allowed(true)
                    .remainingRequests(config.getMaxRequests() - currentCount - 1)
                    .resetTimeMs(calculateResetTime(logState, config, currentTimeMs))
                    .retryAfterMs(0)
                    .algorithmUsed(ALGORITHM_NAME)
                    .build();
        } else {
            // Reject - calculate when oldest request expires
            long oldestTimestamp = logState.getOldestTimestamp();
            long retryAfterMs = oldestTimestamp + config.getWindowSizeMs() - currentTimeMs;

            return RateLimitResult.builder()
                    .allowed(false)
                    .remainingRequests(0)
                    .resetTimeMs(oldestTimestamp + config.getWindowSizeMs())
                    .retryAfterMs(Math.max(0, retryAfterMs))
                    .algorithmUsed(ALGORITHM_NAME)
                    .build();
        }
    }

    @Override
    public int getRemainingRequests(ClientState state, RateLimitConfig config) {
        if (!(state instanceof SlidingWindowLogState)) {
            return config.getMaxRequests();
        }

        SlidingWindowLogState logState = (SlidingWindowLogState) state;
        long windowStartMs = System.currentTimeMillis() - config.getWindowSizeMs();
        cleanOldEntries(logState, windowStartMs);

        return Math.max(0, config.getMaxRequests() - logState.getRequestCount());
    }

    private void cleanOldEntries(SlidingWindowLogState state, long windowStartMs) {
        while (!state.isEmpty() && state.getOldestTimestamp() < windowStartMs) {
            state.removeOldest();
        }
    }

    private long calculateResetTime(SlidingWindowLogState state, RateLimitConfig config, long currentTimeMs) {
        if (state.isEmpty()) {
            return currentTimeMs + config.getWindowSizeMs();
        }
        return state.getOldestTimestamp() + config.getWindowSizeMs();
    }
}

/**
 * State for Sliding Window Log algorithm.
 */
class SlidingWindowLogState implements ClientState {
    private final Deque<Long> requestTimestamps;
    private final long createdAt;

    public SlidingWindowLogState() {
        this.requestTimestamps = new ArrayDeque<>();
        this.createdAt = System.currentTimeMillis();
    }

    public void addRequest(long timestamp) {
        requestTimestamps.addLast(timestamp);
    }

    public void removeOldest() {
        requestTimestamps.pollFirst();
    }

    public long getOldestTimestamp() {
        return requestTimestamps.peekFirst();
    }

    public int getRequestCount() {
        return requestTimestamps.size();
    }

    public boolean isEmpty() {
        return requestTimestamps.isEmpty();
    }

    @Override
    public long getCreatedAt() {
        return createdAt;
    }

    @Override
    public int getMemoryUsage() {
        // Approximate: 8 bytes per Long in queue
        return 8 * requestTimestamps.size();
    }
}
