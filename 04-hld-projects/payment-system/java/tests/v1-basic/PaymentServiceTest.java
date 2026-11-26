import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

class PaymentServiceTest {

    private PaymentService paymentService;

    @BeforeEach
    void setUp() {
        paymentService = new PaymentService();
    }

    @Test
    void testCreatePaymentIntentIdempotency() {
        String idempotencyKey = "key-123";
        PaymentService.PaymentIntent intent1 = paymentService.createPaymentIntent(idempotencyKey, "m_1", "c_1", 1000, "USD");
        assertNotNull(intent1);
        assertEquals(PaymentService.PaymentState.CREATED, intent1.state);

        PaymentService.PaymentIntent intent2 = paymentService.createPaymentIntent(idempotencyKey, "m_1", "c_1", 1000, "USD");
        assertEquals(intent1.id, intent2.id); // Same intent returned

        assertThrows(IllegalStateException.class, () -> {
            paymentService.createPaymentIntent(idempotencyKey, "m_2", "c_2", 2000, "EUR");
        });
    }

    @Test
    void testStateTransitions() {
        PaymentService.PaymentIntent intent = paymentService.createPaymentIntent("key-1", "m_1", "c_1", 1000, "USD");

        PaymentService.PaymentTransaction authTxn = paymentService.authorize(intent.id);
        assertEquals(PaymentService.TransactionType.AUTHORIZE, authTxn.type);
        assertEquals(PaymentService.PaymentState.AUTHORIZED, paymentService.getIntent(intent.id).state);

        PaymentService.PaymentTransaction captureTxn = paymentService.capture(intent.id);
        assertEquals(PaymentService.TransactionType.CAPTURE, captureTxn.type);
        assertEquals(PaymentService.PaymentState.CAPTURED, paymentService.getIntent(intent.id).state);
    }

    @Test
    void testRefundLogic() {
        PaymentService.PaymentIntent intent = paymentService.createPaymentIntent("key-1", "m_1", "c_1", 1000, "USD");
        paymentService.authorize(intent.id);
        paymentService.capture(intent.id);

        paymentService.refund(intent.id, 400);
        assertEquals(PaymentService.PaymentState.PARTIALLY_REFUNDED, paymentService.getIntent(intent.id).state);

        paymentService.refund(intent.id, 600);
        assertEquals(PaymentService.PaymentState.REFUNDED, paymentService.getIntent(intent.id).state);

        assertThrows(IllegalStateException.class, () -> {
            paymentService.refund(intent.id, 100);
        });
    }

    @Test
    void testLedgerBalancing() {
        PaymentService.PaymentIntent intent = paymentService.createPaymentIntent("key-1", "m_1", "c_1", 1000, "USD");
        paymentService.authorize(intent.id);
        paymentService.capture(intent.id);

        List<PaymentService.LedgerEntry> ledger = paymentService.getLedger();

        // Capture creates 2 entries (debit customer, credit merchant)
        assertEquals(2, ledger.size());

        long sum = 0;
        for (PaymentService.LedgerEntry entry : ledger) {
            sum += entry.amount;
        }
        assertEquals(0, sum); // Double entry bookkeeping sum should be zero

        paymentService.refund(intent.id, 500);
        ledger = paymentService.getLedger();

        // Refund creates 2 more entries (debit merchant, credit customer)
        assertEquals(4, ledger.size());

        sum = 0;
        for (PaymentService.LedgerEntry entry : ledger) {
            sum += entry.amount;
        }
        assertEquals(0, sum); // Still balances to zero
    }

    @Test
    void testVoidPayment() {
        PaymentService.PaymentIntent intent = paymentService.createPaymentIntent("key-1", "m_1", "c_1", 1000, "USD");
        paymentService.authorize(intent.id);
        paymentService.voidPayment(intent.id);

        assertEquals(PaymentService.PaymentState.VOIDED, paymentService.getIntent(intent.id).state);

        assertThrows(IllegalStateException.class, () -> {
            paymentService.capture(intent.id);
        });
    }
}
