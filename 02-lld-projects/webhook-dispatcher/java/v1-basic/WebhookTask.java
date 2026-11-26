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
    private final int maxRetries = 3;
    private final long baseDelayMs = 100;

    public WebhookTask(Event event, Subscriber subscriber, WebhookDispatcher dispatcher) {
        this.event = event;
        this.subscriber = subscriber;
        this.dispatcher = dispatcher;
    }

    public Event getEvent() { return event; }
    public Subscriber getSubscriber() { return subscriber; }
    public int getAttempt() { return attempt; }

    @Override
    public void run() {
        String payloadStr = serializePayload(event.getPayload());
        
        String signature;
        try {
            signature = generateHmacSha256(subscriber.getSecret(), payloadStr);
        } catch (Exception e) {
            System.err.println("Failed to generate HMAC: " + e.getMessage());
            return;
        }

        Map<String, String> headers = Map.of(
            "Content-Type", "application/json",
            "X-Hub-Signature-256", "sha256=" + signature
        );

        boolean success = false;
        try {
            dispatcher.acquireSemaphore(subscriber.getEndpoint());
            try {
                DeliveryResult result = dispatcher.getHttpClient().post(subscriber.getEndpoint(), payloadStr, headers);
                success = result != null && result.isSuccess();
            } finally {
                dispatcher.releaseSemaphore(subscriber.getEndpoint());
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return;
        } catch (Exception e) {
            System.err.println("Delivery failed: " + e.getMessage());
        }

        if (!success) {
            attempt++;
            if (attempt <= maxRetries) {
                long maxDelayMs = baseDelayMs * (1L << attempt);
                long delayMs = (long) (Math.random() * maxDelayMs);
                dispatcher.scheduleRetry(this, delayMs);
            } else {
                dispatcher.addToDlq(this);
            }
        }
    }

    private String serializePayload(Map<String, Object> payload) {
        // Simple manual JSON serialization for stdlib-only constraint
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

    private String generateHmacSha256(String secret, String data) throws NoSuchAlgorithmException, InvalidKeyException {
        Mac mac = Mac.getInstance("HmacSHA256");
        SecretKeySpec secretKeySpec = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
        mac.init(secretKeySpec);
        byte[] hash = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));
        return bytesToHex(hash);
    }

    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }
}
