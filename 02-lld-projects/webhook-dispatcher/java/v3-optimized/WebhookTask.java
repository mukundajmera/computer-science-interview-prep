
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public class WebhookTask implements Runnable {
    private final Event event;
    private final Subscriber subscriber;
    private final WebhookDispatcher dispatcher;
    private int attempt = 0;
    private final int maxRetries = 5;
    private final long baseDelayMs = 100;
    private final long maxDelayMs = 5000;

    public WebhookTask(Event event, Subscriber subscriber, WebhookDispatcher dispatcher) {
        this.event = event;
        this.subscriber = subscriber;
        this.dispatcher = dispatcher;
    }

    public Event getEvent() { return event; }
    public Subscriber getSubscriber() { return subscriber; }
    public int getAttempt() { return attempt; }
    public void resetAttempt() { attempt = 0; }
    public void setAttempt(int attempt) { this.attempt = attempt; }

    @Override
    public void run() {
        CircuitBreaker cb = dispatcher.getCircuitBreaker(subscriber.getEndpoint());
        if (!cb.allowRequest()) {
            handleFailure(cb);
            return;
        }
        
        String payloadStr = serializePayload(event.getPayload());
        String timestamp = String.valueOf(System.currentTimeMillis() / 1000L);
        
        String signature;
        try {
            signature = generateHmacSha256(subscriber.getSecret(), payloadStr, timestamp);
        } catch (Exception e) {
            System.err.println("Failed to generate HMAC: " + e.getMessage());
            return;
        }

        Map<String, String> headers = Map.of(
            "Content-Type", "application/json",
            "X-Webhook-Timestamp", timestamp,
            "X-Hub-Signature-256", "sha256=" + signature
        );

        boolean success = false;
        int statusCode = 0;
        try {
            dispatcher.acquireSemaphore(subscriber.getHost());
            try {
                DeliveryResult result = dispatcher.getHttpClient().post(subscriber.getEndpoint(), payloadStr, headers);
                if (result != null) {
                    success = result.isSuccess();
                    statusCode = result.getStatusCode();
                }
            } finally {
                dispatcher.releaseSemaphore(subscriber.getHost());
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return;
        } catch (Exception e) {
            System.err.println("Delivery failed: " + e.getMessage());
            statusCode = 500;
        }

        if (success) {
            cb.recordSuccess();
        } else {
            if (statusCode >= 500 || statusCode == 0) {
                cb.recordFailure();
            }
            handleFailure(cb);
        }
    }
    
    public void handleFailure(CircuitBreaker cb) {
        attempt++;
        if (attempt <= maxRetries) {
            // Full Jitter Backoff
            long temp = Math.min(maxDelayMs, baseDelayMs * (1L << attempt));
            long delayMs = (long) (Math.random() * temp);
            dispatcher.scheduleRetry(this, delayMs);
        } else {
            dispatcher.addToDlq(this);
        }
    }

    private String serializePayload(Map<String, Object> payload) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : payload.entrySet()) {
            if (!first) sb.append(",");
            sb.append("\"").append(entry.getKey()).append("\":");
            if (entry.getValue() instanceof Number) {
                sb.append(entry.getValue());
            } else {
                sb.append("\"").append(entry.getValue()).append("\"");
            }
            first = false;
        }
        sb.append("}");
        return sb.toString();
    }

    public static String generateHmacSha256(String secret, String data, String timestamp) throws NoSuchAlgorithmException, InvalidKeyException {
        String message = timestamp + "." + data;
        Mac mac = Mac.getInstance("HmacSHA256");
        SecretKeySpec secretKeySpec = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
        mac.init(secretKeySpec);
        byte[] hash = mac.doFinal(message.getBytes(StandardCharsets.UTF_8));
        return bytesToHex(hash);
    }
    
    public static boolean verifySignature(String secret, String data, String timestamp, String signature, int maxAgeSeconds) {
        try {
            long ts = Long.parseLong(timestamp);
            long now = System.currentTimeMillis() / 1000L;
            if (now - ts > maxAgeSeconds || now - ts < -5) {
                return false;
            }
            
            String expected = generateHmacSha256(secret, data, timestamp);
            return signature != null && signature.equals(expected);
        } catch (Exception e) {
            return false;
        }
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }
}
