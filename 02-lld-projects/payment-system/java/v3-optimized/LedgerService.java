/**
 * LedgerService for payment-system (v3-optimized).
 */
public class LedgerService {
    private final String id;

    public LedgerService() {
        this.id = "LedgerService";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "LedgerService:" + id;
    }
}
