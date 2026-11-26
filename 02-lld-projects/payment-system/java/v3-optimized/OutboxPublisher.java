/**
 * OutboxPublisher for payment-system (v3-optimized).
 */
public class OutboxPublisher {
    private final String id;

    public OutboxPublisher() {
        this.id = "OutboxPublisher";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "OutboxPublisher:" + id;
    }
}
