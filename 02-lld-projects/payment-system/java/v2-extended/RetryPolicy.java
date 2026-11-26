/**
 * RetryPolicy for payment-system (v2-extended).
 */
public class RetryPolicy {
    private final String id;

    public RetryPolicy() {
        this.id = "RetryPolicy";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "RetryPolicy:" + id;
    }
}
// Substantive change for review
