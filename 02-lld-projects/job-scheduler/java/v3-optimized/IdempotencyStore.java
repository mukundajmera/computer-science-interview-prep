/**
 * IdempotencyStore for job-scheduler (v3-optimized).
 */
public class IdempotencyStore {
    private final String id;

    public IdempotencyStore() {
        this.id = "IdempotencyStore";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "IdempotencyStore:" + id;
    }
}
