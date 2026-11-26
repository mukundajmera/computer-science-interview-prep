/**
 * PaymentService for payment-system (v2-extended).
 */
public class PaymentService {
    private final String id;

    public PaymentService() {
        this.id = "PaymentService";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "PaymentService:" + id;
    }
}
// Substantive change for review
