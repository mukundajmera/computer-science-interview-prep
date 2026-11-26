import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.junit.jupiter.api.Assertions.*;

public class DigitalWalletServiceTest {

    private DoubleEntryLedger ledger;
    private TccTransactionCoordinator coordinator;
    private DigitalWalletService service;

    @BeforeEach
    public void setup() {
        ledger = new DoubleEntryLedger();
        coordinator = new TccTransactionCoordinator();
        service = new DigitalWalletService(ledger, coordinator);
    }

    @Test
    public void testSuccessfulTransferMaintainsDoubleEntryInvariant() {
        service.createAccount("A", "USD", new BigDecimal("100.00"));
        service.createAccount("B", "USD", new BigDecimal("50.00"));

        TccTransactionCoordinator.Status status = service.transfer("A", "B", new BigDecimal("25.00"), "USD", "tx-1");
        
        assertEquals(TccTransactionCoordinator.Status.SUCCESS, status);
        assertEquals(new BigDecimal("75.00"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("75.00"), service.getAccount("B").balance);
        assertEquals(new BigDecimal("0.00"), service.getAccount("A").heldBalance);
        
        // Validation of Double-Entry Ledger is implicit as exception would be thrown on commit
        assertTrue(ledger.getJournal().size() >= 2);
    }

    @Test
    public void testIdempotentRetryReturnsIdenticalStatus() {
        service.createAccount("A", "USD", new BigDecimal("100.00"));
        service.createAccount("B", "USD", new BigDecimal("50.00"));

        TccTransactionCoordinator.Status status1 = service.transfer("A", "B", new BigDecimal("20.00"), "USD", "tx-2");
        TccTransactionCoordinator.Status status2 = service.transfer("A", "B", new BigDecimal("20.00"), "USD", "tx-2");
        
        assertEquals(TccTransactionCoordinator.Status.SUCCESS, status1);
        assertEquals(TccTransactionCoordinator.Status.SUCCESS, status2);
        assertEquals(new BigDecimal("80.00"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("70.00"), service.getAccount("B").balance);
    }

    @Test
    public void testInsufficientFundsTriggersCancelCompensation() {
        service.createAccount("A", "USD", new BigDecimal("10.00"));
        service.createAccount("B", "USD", new BigDecimal("50.00"));

        TccTransactionCoordinator.Status status = service.transfer("A", "B", new BigDecimal("20.00"), "USD", "tx-3");
        
        assertEquals(TccTransactionCoordinator.Status.FAILED, status);
        assertEquals(new BigDecimal("10.00"), service.getAccount("A").balance); // Unchanged
        assertEquals(new BigDecimal("50.00"), service.getAccount("B").balance); // Unchanged
    }

    @Test
    public void testOutOfOrderCancelHandledSafely() {
        service.createAccount("A", "USD", new BigDecimal("100.00"));
        service.createAccount("B", "USD", new BigDecimal("50.00"));

        // Simulate cancel arriving before the transfer even starts processing its TRY phase
        service.simulateOutOfOrderCancel("tx-4");

        TccTransactionCoordinator.Status status = service.transfer("A", "B", new BigDecimal("30.00"), "USD", "tx-4");
        
        // transfer should fail due to early cancellation
        assertEquals(TccTransactionCoordinator.Status.FAILED, status);
        assertEquals(new BigDecimal("100.00"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("50.00"), service.getAccount("B").balance);
    }

    @Test
    public void testEventSourcingReplayReconstructsExactBalance() {
        service.createAccount("A", "USD", new BigDecimal("100.00"));
        service.createAccount("B", "USD", new BigDecimal("50.00"));

        service.transfer("A", "B", new BigDecimal("40.00"), "USD", "tx-5");
        service.transfer("B", "A", new BigDecimal("10.00"), "USD", "tx-6");

        assertEquals(new BigDecimal("70.00"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("80.00"), service.getAccount("B").balance);

        // Manually mess up balances
        service.getAccount("A").balance = new BigDecimal("999.00");
        service.getAccount("B").balance = new BigDecimal("-50.00");

        service.replayEventSourcingHistory();

        // Should reconstruct to exact correct balance
        assertEquals(new BigDecimal("70.00"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("80.00"), service.getAccount("B").balance);
    }
}
