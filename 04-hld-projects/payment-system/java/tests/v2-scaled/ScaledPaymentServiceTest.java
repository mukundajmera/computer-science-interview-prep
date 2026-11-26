import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class ScaledPaymentServiceTest {

    @Test
    public void testWebhookDeduplication() {
        ScaledPaymentService service = new ScaledPaymentService();
        ScaledPaymentService.PaymentIntent intent = service.createIntent("intent_1", 100);

        ScaledPaymentService.WebhookEvent event = new ScaledPaymentService.WebhookEvent(
            "ev_1", "intent_1", ScaledPaymentService.WebhookType.AUTHORIZED, "hash", System.currentTimeMillis()
        );

        assertTrue(service.handleWebhook(event));
        assertEquals(ScaledPaymentService.PaymentState.AUTHORIZED, intent.state);

        assertFalse(service.handleWebhook(event));
        assertEquals(ScaledPaymentService.PaymentState.AUTHORIZED, intent.state);
    }

    @Test
    public void testOutOfOrderWebhook() {
        ScaledPaymentService service = new ScaledPaymentService();
        ScaledPaymentService.PaymentIntent intent = service.createIntent("intent_2", 200);

        ScaledPaymentService.WebhookEvent evCaptured = new ScaledPaymentService.WebhookEvent(
            "ev_cap", "intent_2", ScaledPaymentService.WebhookType.CAPTURED, "hash", System.currentTimeMillis()
        );
        ScaledPaymentService.WebhookEvent evAuthorized = new ScaledPaymentService.WebhookEvent(
            "ev_auth", "intent_2", ScaledPaymentService.WebhookType.AUTHORIZED, "hash", System.currentTimeMillis()
        );

        service.handleWebhook(evCaptured);
        assertEquals(ScaledPaymentService.PaymentState.CAPTURED, intent.state);

        service.handleWebhook(evAuthorized);
        assertEquals(ScaledPaymentService.PaymentState.CAPTURED, intent.state);
    }

    @Test
    public void testDlqExponentialBackoff() throws InterruptedException {
        ScaledPaymentService service = new ScaledPaymentService();

        boolean res = service.reconcileSettlementJob("ref_123", 500, 0);
        assertFalse(res);

        assertEquals(1, service.getDlq().size());
        ScaledPaymentService.RetryJob job = service.getDlq().get(0);
        assertEquals(1, job.failCount);

        service.processDlq();
        assertEquals(1, service.getDlq().size());

        // Emulate time pass
        job.nextRetryAt = System.currentTimeMillis() - 1000;
        service.processDlq();

        assertEquals(1, service.getDlq().size());
        assertEquals(2, service.getDlq().get(0).failCount);
    }

    @Test
    public void testSettlementReconciliation() {
        ScaledPaymentService service = new ScaledPaymentService();
        ScaledPaymentService.PaymentIntent intent = service.createIntent("intent_3", 300);
        intent.gatewayRef = "ref_456";
        intent.state = ScaledPaymentService.PaymentState.AUTHORIZED;

        boolean res = service.reconcileSettlementJob("ref_456", 300, 0);
        assertTrue(res);
        assertEquals(ScaledPaymentService.PaymentState.CAPTURED, intent.state);
    }
}
