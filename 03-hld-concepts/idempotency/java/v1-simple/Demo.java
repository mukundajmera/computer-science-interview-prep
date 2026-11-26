
public class Demo {
    public static void main(String[] args) {
        IdempotencyKeyManager manager = new IdempotencyKeyManager(60000);

        String key = "req-123";
        String payload = "{\"amount\": 100}";

        IdempotencyKeyManager.Record record = manager.beginRequest(key, payload);
        if (record.status == IdempotencyKeyManager.Status.IN_PROGRESS) {
            System.out.println("Processing new request...");
            manager.completeRequest(key, "{\"status\": \"success\"}");
        }

        IdempotencyKeyManager.Record record2 = manager.beginRequest(key, payload);
        if (record2.status == IdempotencyKeyManager.Status.COMPLETED) {
            System.out.println("Returning cached response: " + record2.response);
        }

        try {
            manager.beginRequest(key, "{\"amount\": 200}");
        } catch (IdempotencyKeyManager.ConflictException e) {
            System.out.println("Conflict detected: " + e.getMessage());
        }
    }
}
