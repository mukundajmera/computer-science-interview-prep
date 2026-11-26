/**
 * RiskRule for payment-system (v2-extended).
 */
public class RiskRule {
    private final String id;

    public RiskRule() {
        this.id = "RiskRule";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "RiskRule:" + id;
    }
}
// Substantive change for review
