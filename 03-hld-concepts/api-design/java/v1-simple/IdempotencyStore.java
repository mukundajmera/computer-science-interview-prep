import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/** Simple idempotency key store for retry-safe API handling. */
public class IdempotencyStore {
    private final Map<String, String> responses = new HashMap<>();

    public synchronized void record(String key, String responseId) {
        validate(key, responseId);
        responses.putIfAbsent(key, responseId);
    }

    public synchronized String get(String key) {
        if (key == null || key.isBlank()) {
            throw new IllegalArgumentException("key must not be blank");
        }
        return responses.get(key);
    }

    public synchronized String processCreateRequest(String key, String generatedId) {
        validate(key, generatedId);
        return responses.computeIfAbsent(key, ignored -> generatedId);
    }

    private static void validate(String key, String responseId) {
        if (key == null || key.isBlank()) {
            throw new IllegalArgumentException("key must not be blank");
        }
        Objects.requireNonNull(responseId, "responseId");
    }
}
