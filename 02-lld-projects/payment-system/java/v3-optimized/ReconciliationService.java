/**
 * ReconciliationService for payment-system (v3-optimized).
 */
public class ReconciliationService {
    private final String id;

    public ReconciliationService() {
        this.id = "ReconciliationService";
    }
    
    public void resolveTimeout(PaymentService paymentService, String transactionId, PaymentService.TransactionState finalStatus) {
        paymentService.handleWebhook(transactionId, finalStatus);
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "ReconciliationService:" + id;
    }
}
