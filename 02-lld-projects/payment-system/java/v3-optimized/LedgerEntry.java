/**
 * LedgerEntry for payment-system (v3-optimized).
 */
public class LedgerEntry {
    private final String id;

    public LedgerEntry() {
        this.id = "LedgerEntry";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "LedgerEntry:" + id;
    }
}
