package implementation;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class RedisSimulator {
    private final Map<String, Long> store = new HashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public long evalLua(String scriptName, String[] keys, String[] args) {
        lock.lock();
        try {
            if ("reserve_batch".equals(scriptName)) {
                return reserveBatch(keys, args);
            } else if ("sliding_window_increment".equals(scriptName)) {
                return slidingWindowIncrement(keys, args);
            }
            throw new IllegalArgumentException("Unknown script: " + scriptName);
        } finally {
            lock.unlock();
        }
    }

    private long reserveBatch(String[] keys, String[] args) {
        String userKey = keys[0];
        long globalLimit = Long.parseLong(args[0]);
        long batchSize = Long.parseLong(args[1]);
        long windowSec = Long.parseLong(args[2]);
        long now = Long.parseLong(args[3]);

        String currentWindowKey = userKey + ":" + (now / windowSec);
        long currentUsage = store.getOrDefault(currentWindowKey, 0L);

        if (currentUsage >= globalLimit) {
            return 0; // Rejected
        }

        long available = globalLimit - currentUsage;
        long allocated = Math.min(batchSize, available);

        store.put(currentWindowKey, currentUsage + allocated);
        return allocated;
    }

    private long slidingWindowIncrement(String[] keys, String[] args) {
        String userKey = keys[0];
        long limit = Long.parseLong(args[0]);
        long windowSec = Long.parseLong(args[1]);
        long now = Long.parseLong(args[2]);

        long currentWindowStart = (now / windowSec) * windowSec;
        long prevWindowStart = currentWindowStart - windowSec;

        String currKey = userKey + ":" + currentWindowStart;
        String prevKey = userKey + ":" + prevWindowStart;

        long currCount = store.getOrDefault(currKey, 0L);
        long prevCount = store.getOrDefault(prevKey, 0L);

        long elapsedInWindow = now - currentWindowStart;
        double weight = 1.0 - ((double) elapsedInWindow / windowSec);

        long estimatedCount = (long) (prevCount * weight) + currCount;

        if (estimatedCount >= limit) {
            return 0; // Rejected
        }

        store.put(currKey, currCount + 1);
        return 1; // Allowed
    }
}
