/**
 * Money for payment-system (v1-basic).
 */
public class Money {
    private final String id;

    public Money() {
        this.id = "Money";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "Money:" + id;
    }
}
