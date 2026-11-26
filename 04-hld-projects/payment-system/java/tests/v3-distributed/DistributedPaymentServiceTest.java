import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

public class DistributedPaymentServiceTest {

    private DistributedPaymentService service;

    @BeforeEach
    public void setUp() {
        service = new DistributedPaymentService("us-east-1");
    }

    @Test
    public void testSuccessfulAuthorizationAndCapture() {
        String idemKey = UUID.randomUUID().toString();

        Object response = service.createOrConfirmIntent(idemKey, "merch1", "cust1", 1000, "USD");
        assertTrue(response instanceof DistributedPaymentService.PaymentIntent);
        DistributedPaymentService.PaymentIntent intent = (DistributedPaymentService.PaymentIntent) response;

        assertEquals(DistributedPaymentService.PaymentState.AUTHORIZED, intent.state);

        DistributedPaymentService.PaymentTransaction captureTxn = service.capture(intent.id);
        assertNotNull(captureTxn);
        assertEquals(DistributedPaymentService.TransactionType.CAPTURE, captureTxn.type);

        DistributedPaymentService.PaymentIntent updatedIntent = service.getIntent(intent.id);
        assertEquals(DistributedPaymentService.PaymentState.CAPTURED, updatedIntent.state);
    }

    @Test
    public void testIdempotentRetries() {
        String idemKey = UUID.randomUUID().toString();

        Object firstResponse = service.createOrConfirmIntent(idemKey, "merch1", "cust1", 1000, "USD");
        assertTrue(firstResponse instanceof DistributedPaymentService.PaymentIntent);
        DistributedPaymentService.PaymentIntent firstIntent = (DistributedPaymentService.PaymentIntent) firstResponse;

        // Exact same request
        Object secondResponse = service.createOrConfirmIntent(idemKey, "merch1", "cust1", 1000, "USD");
        assertTrue(secondResponse instanceof DistributedPaymentService.PaymentIntent);
        DistributedPaymentService.PaymentIntent secondIntent = (DistributedPaymentService.PaymentIntent) secondResponse;

        assertEquals(firstIntent.id, secondIntent.id);

        // Different payload hash should fail
        assertThrows(IllegalStateException.class, () -> {
            service.createOrConfirmIntent(idemKey, "merch1", "cust1", 2000, "USD");
        });
    }

    @Test
    public void testDegradedModeAsyncAuthorization() {
        service.setDegradedMode(true);
        String idemKey = UUID.randomUUID().toString();

        Object response = service.createOrConfirmIntent(idemKey, "merch1", "cust1", 1000, "USD");
        DistributedPaymentService.PaymentIntent intent = (DistributedPaymentService.PaymentIntent) response;

        // Should be in PROCESSING state due to degraded mode (async)
        assertEquals(DistributedPaymentService.PaymentState.PROCESSING, intent.state);

        // Simulate webhook success
        service.handleProviderWebhook(intent.id, "SUCCESS");

        DistributedPaymentService.PaymentIntent updatedIntent = service.getIntent(intent.id);
        assertEquals(DistributedPaymentService.PaymentState.AUTHORIZED, updatedIntent.state);
    }

    @Test
    public void testDistributedSagaCompensation() {
        // Successful saga
        DistributedPaymentService.SagaContext successSaga = service.executeTransferSaga("acc1", "acc2", 500);
        assertFalse(successSaga.compensated);
        assertEquals(2, successSaga.stepsCompleted.size());

        // Failed saga with compensation (credit fails)
        RuntimeException ex = assertThrows(RuntimeException.class, () -> {
            service.executeTransferSaga("acc1", "fail_acc2", 500);
        });

        assertTrue(ex.getMessage().contains("Saga aborted and compensated"));
    }
}
