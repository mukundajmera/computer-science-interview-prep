
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.concurrent.ConcurrentHashMap;

public class IdempotencyKeyManager {
    public enum Status {
        IN_PROGRESS, COMPLETED, FAILED
    }

    public static class Record {
        public final String key;
        public final String payloadHash;
        public Status status;
        public Object response;
        public final long expiresAt;

        public Record(String key, String payloadHash, long expiresAt) {
            this.key = key;
            this.payloadHash = payloadHash;
            this.status = Status.IN_PROGRESS;
            this.response = null;
            this.expiresAt = expiresAt;
        }
    }

    private final ConcurrentHashMap<String, Record> store = new ConcurrentHashMap<>();
    private final long ttlMillis;

    public IdempotencyKeyManager(long ttlMillis) {
        this.ttlMillis = ttlMillis;
    }

    private String hashPayload(String payload) {
        if (payload == null) return "";
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] encodedhash = digest.digest(payload.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder(2 * encodedhash.length);
            for (byte b : encodedhash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    public static class IdempotencyException extends RuntimeException {
        public IdempotencyException(String message) {
            super(message);
        }
    }

    public static class ConflictException extends IdempotencyException {
        public ConflictException(String message) {
            super(message);
        }
    }

    public static class ExpiredException extends IdempotencyException {
        public ExpiredException(String message) {
            super(message);
        }
    }

    public static class InProgressException extends IdempotencyException {
        public InProgressException(String message) {
            super(message);
        }
    }

    // Attempt to start a request.
    // Returns the record. If it's a new request, status is IN_PROGRESS.
    // If it exists, returns the existing record (could be COMPLETED or FAILED).
    // Throws InProgressException if the request is already in progress.
    // Throws ConflictException if the payload hash doesn't match.
    // Cleans up expired records lazily.
    public Record beginRequest(String key, String payload) {
        String hash = hashPayload(payload);
        long now = Instant.now().toEpochMilli();

        return store.compute(key, (k, existing) -> {
            if (existing != null) {
                if (existing.expiresAt < now) {
                    // Treat as a new request if expired
                    return new Record(k, hash, now + ttlMillis);
                }
                if (!existing.payloadHash.equals(hash)) {
                    throw new ConflictException("Payload mismatch for idempotency key");
                }
                if (existing.status == Status.IN_PROGRESS) {
                    throw new InProgressException("Request is already in progress");
                }
                return existing;
            }
            return new Record(k, hash, now + ttlMillis);
        });
    }

    public void completeRequest(String key, Object response) {
        store.computeIfPresent(key, (k, record) -> {
            record.status = Status.COMPLETED;
            record.response = response;
            return record;
        });
    }

    public void failRequest(String key) {
        store.computeIfPresent(key, (k, record) -> {
            record.status = Status.FAILED;
            return record;
        });
    }

    public void cleanup() {
        long now = Instant.now().toEpochMilli();
        store.entrySet().removeIf(entry -> entry.getValue().expiresAt < now);
    }
}
