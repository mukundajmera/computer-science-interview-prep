/**
 * PaymentService for payment-system (v1-basic).
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
// v1-basic intent core baseline
