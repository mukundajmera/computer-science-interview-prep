import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class PaymentSystemV3Test {
    private PaymentService service;

    @BeforeEach
    void setUp() {
        service = new PaymentService();
    }

    @Test
    void testIdempotencyKeyRepeat() {
        PaymentService.PaymentRequest req = new PaymentService.PaymentRequest("uuid-123", 1000, "USD", "tok_1");
        PaymentService.PaymentResponse resp1 = service.processPayment(req);
        assertEquals("SUCCESS", resp1.status);

        PaymentService.PaymentResponse resp2 = service.processPayment(req);
        assertEquals(resp1, resp2);
        
        assertEquals(1, service.getTransactionCount());
    }

    @Test
    void testIdempotencyKeyPayloadMismatch() {
        PaymentService.PaymentRequest req1 = new PaymentService.PaymentRequest("uuid-456", 1000, "USD", "tok_1");
        service.processPayment(req1);

        PaymentService.PaymentRequest req2 = new PaymentService.PaymentRequest("uuid-456", 2000, "USD", "tok_1");
        assertThrows(IllegalArgumentException.class, () -> {
            service.processPayment(req2);
        });
    }

    @Test
    void testGatewayTimeoutAndWebhookReconciliation() {
        PaymentService.PaymentRequest req = new PaymentService.PaymentRequest("uuid-789", 3000, "USD", "tok_2");
        PaymentService.PaymentResponse resp = service.processPayment(req);
        assertEquals("PENDING", resp.status);

        String txId = resp.transactionId;
        assertEquals(PaymentService.TransactionState.GATEWAY_PENDING, service.getTransaction(txId).state);

        service.handleWebhook(txId, PaymentService.TransactionState.COMPLETED);
        assertEquals(PaymentService.TransactionState.COMPLETED, service.getTransaction(txId).state);

        service.handleWebhook(txId, PaymentService.TransactionState.DECLINED);
        assertEquals(PaymentService.TransactionState.COMPLETED, service.getTransaction(txId).state);
    }

    @Test
    void testGatewayDeclined() {
        PaymentService.PaymentRequest req = new PaymentService.PaymentRequest("uuid-999", 2000, "USD", "tok_3");
        PaymentService.PaymentResponse resp = service.processPayment(req);
        assertEquals("DECLINED", resp.status);

        String txId = resp.transactionId;
        assertEquals(PaymentService.TransactionState.DECLINED, service.getTransaction(txId).state);
    }

    @Test
    void testRollbackFixture() {
        PaymentService.PaymentRequest req = new PaymentService.PaymentRequest("uuid-rollback", 4000, "USD", "tok_rollback");
        PaymentService.PaymentResponse resp = service.processPayment(req);
        assertEquals("FAILED", resp.status);

        String txId = resp.transactionId;
        assertEquals(PaymentService.TransactionState.FAILED, service.getTransaction(txId).state);

        service.handleWebhook(txId, PaymentService.TransactionState.COMPLETED);
        assertEquals(PaymentService.TransactionState.FAILED, service.getTransaction(txId).state);
    }

    @Test
    void testOutOfOrderWebhookDelivery() {
        PaymentService.PaymentRequest req = new PaymentService.PaymentRequest("uuid-ooo", 3000, "USD", "tok_ooo");
        PaymentService.PaymentResponse resp = service.processPayment(req);
        assertEquals("PENDING", resp.status);
        String txId = resp.transactionId;

        service.handleWebhook(txId, PaymentService.TransactionState.COMPLETED);
        assertEquals(PaymentService.TransactionState.COMPLETED, service.getTransaction(txId).state);

        service.handleWebhook(txId, PaymentService.TransactionState.DECLINED);
        assertEquals(PaymentService.TransactionState.COMPLETED, service.getTransaction(txId).state);
    }
}
