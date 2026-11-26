import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.Map;

public class RateLimiter {
    private final int limit;
    private final Map<String, AtomicInteger> counts = new ConcurrentHashMap<>();

    public RateLimiter(int limit) {
        this.limit = limit;
    }

    public boolean acquire(String channelType) {
        AtomicInteger count = counts.computeIfAbsent(channelType, k -> new AtomicInteger(0));
        while (true) {
            int current = count.get();
            if (current >= limit) {
                return false;
            }
            if (count.compareAndSet(current, current + 1)) {
                return true;
            }
        }
    }
}
