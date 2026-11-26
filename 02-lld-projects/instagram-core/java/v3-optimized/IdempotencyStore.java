import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class IdempotencyStore {
    private final Map<String, Long> store = new ConcurrentHashMap<>();

    public boolean claim(String key, long ttlMs) {
        long now = System.currentTimeMillis();
        Long expiry = store.get(key);
        if (expiry != null && expiry > now) {
            return false;
        }
        store.put(key, now + ttlMs);
        return true;
    }
}
