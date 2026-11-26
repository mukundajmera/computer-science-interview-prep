/**
 * TransactionStore for payment-system (v1-basic).
 */
public class TransactionStore {
    private final String id;

    public TransactionStore() {
        this.id = "TransactionStore";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "TransactionStore:" + id;
    }
}
