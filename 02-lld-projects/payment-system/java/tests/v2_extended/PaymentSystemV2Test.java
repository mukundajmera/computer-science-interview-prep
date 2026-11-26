import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class PaymentSystemV2Test {

    private PaymentOrchestrator orchestrator;
    private WebhookHandler webhookHandler;

    @BeforeEach
    void setUp() {
        orchestrator = new PaymentOrchestrator();
        webhookHandler = new WebhookHandler(orchestrator);
    }

    @Test
    void testIdempotencyKeyRepeat() {
        PaymentOrchestrator.PaymentRequest req = new PaymentOrchestrator.PaymentRequest("uuid-123", 1000, "USD", "tok_1");
        PaymentOrchestrator.PaymentResponse resp1 = orchestrator.processPayment(req);
        assertEquals("SUCCESS", resp1.status);

        PaymentOrchestrator.PaymentResponse resp2 = orchestrator.processPayment(req);
        assertEquals(resp1, resp2);
        
        assertEquals(1, orchestrator.getTransactionCount());
    }

    @Test
    void testIdempotencyKeyPayloadMismatch() {
        PaymentOrchestrator.PaymentRequest req1 = new PaymentOrchestrator.PaymentRequest("uuid-456", 1000, "USD", "tok_1");
        orchestrator.processPayment(req1);

        PaymentOrchestrator.PaymentRequest req2 = new PaymentOrchestrator.PaymentRequest("uuid-456", 2000, "USD", "tok_1");
        assertThrows(IllegalArgumentException.class, () -> {
            orchestrator.processPayment(req2);
        });
    }

    @Test
    void testGatewayTimeoutAndWebhookReconciliation() {
        PaymentOrchestrator.PaymentRequest req = new PaymentOrchestrator.PaymentRequest("uuid-789", 3000, "USD", "tok_2");
        PaymentOrchestrator.PaymentResponse resp = orchestrator.processPayment(req);
        assertEquals("PENDING", resp.status);

        String txId = resp.transactionId;
        assertEquals(PaymentOrchestrator.TransactionState.GATEWAY_PENDING, orchestrator.getTransaction(txId).state);

        webhookHandler.handleWebhook(txId, PaymentOrchestrator.TransactionState.COMPLETED);
        assertEquals(PaymentOrchestrator.TransactionState.COMPLETED, orchestrator.getTransaction(txId).state);

        webhookHandler.handleWebhook(txId, PaymentOrchestrator.TransactionState.DECLINED);
        assertEquals(PaymentOrchestrator.TransactionState.COMPLETED, orchestrator.getTransaction(txId).state);
    }

    @Test
    void testGatewayDeclined() {
        PaymentOrchestrator.PaymentRequest req = new PaymentOrchestrator.PaymentRequest("uuid-999", 2000, "USD", "tok_3");
        PaymentOrchestrator.PaymentResponse resp = orchestrator.processPayment(req);
        assertEquals("DECLINED", resp.status);

        String txId = resp.transactionId;
        assertEquals(PaymentOrchestrator.TransactionState.DECLINED, orchestrator.getTransaction(txId).state);
    }

    @Test
    void testOutOfOrderWebhookDelivery() {
        // Trigger a pending timeout state first so we get the txId
        PaymentOrchestrator.PaymentRequest req = new PaymentOrchestrator.PaymentRequest("uuid-out-of-order", 3000, "USD", "tok_ooo");
        PaymentOrchestrator.PaymentResponse resp = orchestrator.processPayment(req);
        assertEquals("PENDING", resp.status);
        String txId = resp.transactionId;

        // Reconcile to COMPLETED
        webhookHandler.handleWebhook(txId, PaymentOrchestrator.TransactionState.COMPLETED);
        assertEquals(PaymentOrchestrator.TransactionState.COMPLETED, orchestrator.getTransaction(txId).state);

        // Another gateway attempt using a different ID with a delayed completion, simulated by just manually calling a declined mock webhook
        // (This tests the transaction state immutability from webhookHandler)
        webhookHandler.handleWebhook(txId, PaymentOrchestrator.TransactionState.DECLINED);
        assertEquals(PaymentOrchestrator.TransactionState.COMPLETED, orchestrator.getTransaction(txId).state);
    }
}
