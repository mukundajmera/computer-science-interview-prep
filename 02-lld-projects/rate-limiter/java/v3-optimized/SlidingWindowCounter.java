import java.util.concurrent.atomic.AtomicReference;

/**
 * Rate Limiter - V3 Optimized
 * 
 * Thread-safe Sliding Window Counter algorithm.
 * Memory efficient with O(1) space per client.
 * 
 * Algorithm:
 * - Maintain count for current and previous window
 * - Calculate weighted average based on window overlap
 * - Approximate but accurate for practical use
 */
public class SlidingWindowCounter implements RateLimitAlgorithm {
    private static final String ALGORITHM_NAME = "SlidingWindowCounter";

    @Override
    public String getAlgorithmName() {
        return ALGORITHM_NAME;
    }

    @Override
    public ClientState createInitialState() {
        return new SlidingWindowCounterState();
    }

    @Override
    public RateLimitResult tryAcquire(ClientState state, RateLimitConfig config) {
        if (!(state instanceof SlidingWindowCounterState)) {
            throw new IllegalArgumentException("Invalid state type for SlidingWindowCounter");
        }

        SlidingWindowCounterState counterState = (SlidingWindowCounterState) state;
        long currentTimeMs = System.currentTimeMillis();

        // Thread-safe state update
        CounterSnapshot snapshot = counterState.updateAndGet(currentTimeMs, config.getWindowSizeMs());
        
        // Calculate weighted count
        double weight = calculateWeight(currentTimeMs, snapshot.windowStart, config.getWindowSizeMs());
        double estimatedCount = snapshot.previousCount * weight + snapshot.currentCount;

        if (estimatedCount < config.getMaxRequests()) {
            // Allow and increment
            counterState.incrementCurrentCount();
            int remaining = (int) Math.max(0, config.getMaxRequests() - estimatedCount - 1);

            return RateLimitResult.builder()
                    .allowed(true)
                    .remainingRequests(remaining)
                    .resetTimeMs(snapshot.windowStart + config.getWindowSizeMs())
                    .retryAfterMs(0)
                    .algorithmUsed(ALGORITHM_NAME)
                    .build();
        } else {
            // Reject
            long resetTimeMs = snapshot.windowStart + config.getWindowSizeMs();
            long retryAfterMs = Math.max(0, resetTimeMs - currentTimeMs);

            return RateLimitResult.builder()
                    .allowed(false)
                    .remainingRequests(0)
                    .resetTimeMs(resetTimeMs)
                    .retryAfterMs(retryAfterMs)
                    .algorithmUsed(ALGORITHM_NAME)
                    .build();
        }
    }

    @Override
    public int getRemainingRequests(ClientState state, RateLimitConfig config) {
        if (!(state instanceof SlidingWindowCounterState)) {
            return config.getMaxRequests();
        }

        SlidingWindowCounterState counterState = (SlidingWindowCounterState) state;
        long currentTimeMs = System.currentTimeMillis();

        CounterSnapshot snapshot = counterState.updateAndGet(currentTimeMs, config.getWindowSizeMs());
        double weight = calculateWeight(currentTimeMs, snapshot.windowStart, config.getWindowSizeMs());
        double estimatedCount = snapshot.previousCount * weight + snapshot.currentCount;

        return (int) Math.max(0, config.getMaxRequests() - estimatedCount);
    }

    /**
     * Calculate weight for previous window based on overlap.
     * Weight = portion of previous window that overlaps with our sliding window
     */
    private double calculateWeight(long currentTimeMs, long windowStart, long windowSizeMs) {
        // How much time has passed in current window
        long elapsedInCurrentWindow = currentTimeMs - windowStart;
        
        // Weight is portion of window size that extends into previous window
        double weight = 1.0 - (elapsedInCurrentWindow / (double) windowSizeMs);
        
        return Math.max(0, Math.min(1, weight));
    }

    /**
     * Immutable snapshot of counter state.
     */
    static class CounterSnapshot {
        final int previousCount;
        final int currentCount;
        final long windowStart;

        CounterSnapshot(int previousCount, int currentCount, long windowStart) {
            this.previousCount = previousCount;
            this.currentCount = currentCount;
            this.windowStart = windowStart;
        }
    }
}

/**
 * Thread-safe state for Sliding Window Counter.
 */
class SlidingWindowCounterState implements ClientState {
    private final AtomicReference<SlidingWindowCounter.CounterSnapshot> snapshot;
    private final long createdAt;

    public SlidingWindowCounterState() {
        this.createdAt = System.currentTimeMillis();
        this.snapshot = new AtomicReference<>(
            new SlidingWindowCounter.CounterSnapshot(0, 0, createdAt)
        );
    }

    /**
     * Update state for current time and return snapshot.
     * Thread-safe using CAS loop.
     */
    public SlidingWindowCounter.CounterSnapshot updateAndGet(long currentTimeMs, long windowSizeMs) {
        while (true) {
            SlidingWindowCounter.CounterSnapshot current = snapshot.get();
            
            // Check if we need to advance to a new window
            long windowEnd = current.windowStart + windowSizeMs;
            
            if (currentTimeMs >= windowEnd) {
                // Calculate how many windows have passed
                long windowsPassed = (currentTimeMs - current.windowStart) / windowSizeMs;
                
                SlidingWindowCounter.CounterSnapshot newSnapshot;
                if (windowsPassed == 1) {
                    // Move to next window: current becomes previous
                    newSnapshot = new SlidingWindowCounter.CounterSnapshot(
                        current.currentCount,
                        0,
                        current.windowStart + windowSizeMs
                    );
                } else {
                    // Multiple windows passed: reset everything
                    long newWindowStart = current.windowStart + (windowsPassed * windowSizeMs);
                    newSnapshot = new SlidingWindowCounter.CounterSnapshot(0, 0, newWindowStart);
                }
                
                if (snapshot.compareAndSet(current, newSnapshot)) {
                    return newSnapshot;
                }
                // CAS failed, retry
            } else {
                return current;
            }
        }
    }

    /**
     * Increment current window count atomically.
     */
    public void incrementCurrentCount() {
        while (true) {
            SlidingWindowCounter.CounterSnapshot current = snapshot.get();
            SlidingWindowCounter.CounterSnapshot newSnapshot = new SlidingWindowCounter.CounterSnapshot(
                current.previousCount,
                current.currentCount + 1,
                current.windowStart
            );
            if (snapshot.compareAndSet(current, newSnapshot)) {
                return;
            }
        }
    }

    @Override
    public long getCreatedAt() {
        return createdAt;
    }

    @Override
    public int getMemoryUsage() {
        // Fixed size: 2 ints (8) + long (8) + reference overhead
        return 32;
    }
}
