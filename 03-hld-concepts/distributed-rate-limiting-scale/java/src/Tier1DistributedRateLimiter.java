package implementation;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class Tier1DistributedRateLimiter {
    private final RedisSimulator redis;
    private final long globalLimit;
    private final long windowSec;
    private final long batchSize;

    private final ConcurrentHashMap<String, Long> localTokens = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, ReentrantLock> userLocks = new ConcurrentHashMap<>();

    public Tier1DistributedRateLimiter(RedisSimulator redis, long globalLimit, long windowSec, long batchSize) {
        this.redis = redis;
        this.globalLimit = globalLimit;
        this.windowSec = windowSec;
        this.batchSize = batchSize;
    }

    public boolean allowRequest(String userId, long currentTime) {
        ReentrantLock lock = userLocks.computeIfAbsent(userId, k -> new ReentrantLock());
        lock.lock();
        try {
            long tokens = localTokens.getOrDefault(userId, 0L);

            if (tokens > 0) {
                localTokens.put(userId, tokens - 1);

                if (tokens - 1 < batchSize * 0.2) {
                    triggerAsyncReplenish(userId, currentTime);
                }
                return true;
            }

            long fetched = fetchBatch(userId, currentTime);
            if (fetched > 0) {
                localTokens.put(userId, fetched - 1);
                return true;
            }

            return false;
        } finally {
            lock.unlock();
        }
    }

    private void triggerAsyncReplenish(String userId, long currentTime) {
        // Simulates async replenish in a simple way
        long fetched = fetchBatch(userId, currentTime);
        if (fetched > 0) {
            localTokens.put(userId, localTokens.getOrDefault(userId, 0L) + fetched);
        }
    }

    private long fetchBatch(String userId, long currentTime) {
        return redis.evalLua(
                "reserve_batch",
                new String[]{userId},
                new String[]{String.valueOf(globalLimit), String.valueOf(batchSize), String.valueOf(windowSec), String.valueOf(currentTime)}
        );
    }

    // Helper for testing local tokens amount
    public long getLocalTokens(String userId) {
        return localTokens.getOrDefault(userId, 0L);
    }
}
