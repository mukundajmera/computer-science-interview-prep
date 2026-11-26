/**
 * TokenVault for payment-system (v3-optimized).
 */
public class TokenVault {
    private final String id;

    public TokenVault() {
        this.id = "TokenVault";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "TokenVault:" + id;
    }
}
