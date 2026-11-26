import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

/**
 * IdempotencyService for payment-system (v2-extended).
 */
public class IdempotencyService {
    private final String id;
    private final Map<String, CacheEntry> store = new ConcurrentHashMap<>();

    private static class CacheEntry {
        String payloadHash;
        String response;

        CacheEntry(String payloadHash, String response) {
            this.payloadHash = payloadHash;
            this.response = response;
        }
    }

    public IdempotencyService() {
        this.id = "IdempotencyService";
    }

    public String checkOrAcquire(String key, String payloadHash) {
        synchronized (store) {
            CacheEntry entry = store.get(key);
            if (entry != null) {
                if (!entry.payloadHash.equals(payloadHash)) {
                    throw new IllegalArgumentException("Repeated idempotency key with changed payload");
                }
                return entry.response;
            } else {
                store.put(key, new CacheEntry(payloadHash, null));
                return null;
            }
        }
    }

    public void saveResponse(String key, String response) {
        synchronized (store) {
            CacheEntry entry = store.get(key);
            if (entry != null) {
                entry.response = response;
            }
        }
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "IdempotencyService:" + id;
    }
}
