/**
 * PaymentMethod for payment-system (v1-basic).
 */
public class PaymentMethod {
    private final String id;

    public PaymentMethod() {
        this.id = "PaymentMethod";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "PaymentMethod:" + id;
    }
}
