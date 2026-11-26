/**
 * PaymentGateway for payment-system (v1-basic).
 */
public class PaymentGateway {
    private final String id;

    public PaymentGateway() {
        this.id = "PaymentGateway";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "PaymentGateway:" + id;
    }
}
