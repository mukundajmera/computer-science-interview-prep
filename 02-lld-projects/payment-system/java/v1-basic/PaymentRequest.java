/**
 * PaymentRequest for payment-system (v1-basic).
 */
public class PaymentRequest {
    private final String id;

    public PaymentRequest() {
        this.id = "PaymentRequest";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "PaymentRequest:" + id;
    }
}
