/**
 * WebhookHandler for payment-system (v2-extended).
 */
public class WebhookHandler {
    private final String id;
    private final PaymentOrchestrator orchestrator;

    public WebhookHandler(PaymentOrchestrator orchestrator) {
        this.id = "WebhookHandler";
        this.orchestrator = orchestrator;
    }

    public void handleWebhook(String transactionId, PaymentOrchestrator.TransactionState newState) {
        orchestrator.reconcileTransaction(transactionId, newState);
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "WebhookHandler:" + id;
    }
}
