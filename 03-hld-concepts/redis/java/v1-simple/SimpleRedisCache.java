import java.util.HashMap;
import java.util.Map;

/**
 * Interview-scale Redis-like cache primitives with TTL and counters.
 */
public class SimpleRedisCache {
    private static final class Entry {
        private String value;
        private final long expiresAtMillis;

        private Entry(String value, long expiresAtMillis) {
            this.value = value;
            this.expiresAtMillis = expiresAtMillis;
        }
    }

    private final Map<String, Entry> data = new HashMap<>();

    public void set(String key, String value, long ttlMillis) {
        validateTtl(ttlMillis);
        data.put(key, new Entry(value, System.currentTimeMillis() + ttlMillis));
    }

    public boolean setIfAbsent(String key, String value, long ttlMillis) {
        validateTtl(ttlMillis);
        if (get(key) != null) {
            return false;
        }
        data.put(key, new Entry(value, System.currentTimeMillis() + ttlMillis));
        return true;
    }

    public String get(String key) {
        Entry entry = data.get(key);
        if (entry == null) {
            return null;
        }
        if (System.currentTimeMillis() >= entry.expiresAtMillis) {
            data.remove(key);
            return null;
        }
        return entry.value;
    }

    public long increment(String key, long delta, long ttlMillis) {
        validateTtl(ttlMillis);
        String current = get(key);
        long next = (current == null ? 0L : Long.parseLong(current)) + delta;
        set(key, Long.toString(next), ttlMillis);
        return next;
    }

    private void validateTtl(long ttlMillis) {
        if (ttlMillis <= 0) {
            throw new IllegalArgumentException("ttlMillis must be greater than 0");
        }
    }

    public static void main(String[] args) throws InterruptedException {
        SimpleRedisCache cache = new SimpleRedisCache();
        cache.set("session:42", "active", 500);
        System.out.println("session:42 -> " + cache.get("session:42"));
        System.out.println("counter -> " + cache.increment("counter", 1, 1000));
        Thread.sleep(600);
        System.out.println("session:42 after ttl -> " + cache.get("session:42"));
    }
}
