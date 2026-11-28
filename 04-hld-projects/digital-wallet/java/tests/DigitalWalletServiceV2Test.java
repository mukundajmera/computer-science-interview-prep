import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class DigitalWalletServiceV2Test {

    private DoubleEntryLedgerV2 ledger;
    private TccTransactionCoordinatorV2 coordinator;
    private DigitalWalletServiceV2 service;

    @BeforeEach
    public void setup() {
        ledger = new DoubleEntryLedgerV2();
        coordinator = new TccTransactionCoordinatorV2();
        service = new DigitalWalletServiceV2(ledger, coordinator);
    }

    private void fundAccounts() {
        service.createAccount("A", "USD", new BigDecimal("1000"));
        service.createAccount("B", "USD", new BigDecimal("500"));
    }

    // --- Parity tests: v2 must keep every v1 guarantee ---

    @Test
    public void testTransferSuccess() {
        fundAccounts();
        TccTransactionCoordinatorV2.Status status = service.transfer("A", "B", new BigDecimal("100"), "USD", "tx1");
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status);
        assertEquals(new BigDecimal("900"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("600"), service.getAccount("B").balance);
    }

    @Test
    public void testIdempotentRetryReturnsIdenticalStatus() {
        fundAccounts();
        TccTransactionCoordinatorV2.Status status1 = service.transfer("A", "B", new BigDecimal("100"), "USD", "tx1");
        TccTransactionCoordinatorV2.Status status2 = service.transfer("A", "B", new BigDecimal("100"), "USD", "tx1");
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status1);
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status2);
        assertEquals(new BigDecimal("900"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("600"), service.getAccount("B").balance);
    }

    @Test
    public void testInsufficientFundsTriggersCancelCompensation() {
        fundAccounts();
        TccTransactionCoordinatorV2.Status status = service.transfer("A", "B", new BigDecimal("10000"), "USD", "tx2");
        assertEquals(TccTransactionCoordinatorV2.Status.FAILED, status);
        assertEquals(new BigDecimal("1000"), service.getAccount("A").balance);
    }

    @Test
    public void testOutOfOrderCancelFlag() {
        fundAccounts();
        service.simulateOutOfOrderCancel("tx3");
        TccTransactionCoordinatorV2.Status status = service.transfer("A", "B", new BigDecimal("100"), "USD", "tx3");
        assertEquals(TccTransactionCoordinatorV2.Status.FAILED, status);
        assertEquals(new BigDecimal("1000"), service.getAccount("A").balance);
    }

    @Test
    public void testEventReplay() {
        fundAccounts();
        service.transfer("A", "B", new BigDecimal("100"), "USD", "tx4");
        service.getAccount("A").balance = BigDecimal.ZERO; // Simulate data corruption/loss
        service.replayEventSourcingHistory();
        assertEquals(new BigDecimal("900"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("600"), service.getAccount("B").balance);
    }

    // --- v2 item 1: transfer input validation ---

    @Test
    public void testNegativeAmountRejected() {
        fundAccounts();
        assertThrows(IllegalArgumentException.class,
            () -> service.transfer("A", "B", new BigDecimal("-100"), "USD", "tx-neg"));
        assertEquals(new BigDecimal("1000"), service.getAccount("A").balance);
        assertEquals(new BigDecimal("500"), service.getAccount("B").balance);
        assertEquals(4, ledger.getJournal().size()); // only the account funding entries
    }

    @Test
    public void testZeroAmountRejected() {
        fundAccounts();
        assertThrows(IllegalArgumentException.class,
            () -> service.transfer("A", "B", BigDecimal.ZERO, "USD", "tx-zero"));
    }

    @Test
    public void testSameAccountRejected() {
        fundAccounts();
        assertThrows(IllegalArgumentException.class,
            () -> service.transfer("A", "A", new BigDecimal("100"), "USD", "tx-same"));
    }

    @Test
    public void testMissingAccountRejected() {
        fundAccounts();
        assertThrows(IllegalArgumentException.class,
            () -> service.transfer("A", "ZZZ", new BigDecimal("100"), "USD", "tx-missing"));
    }

    @Test
    public void testCurrencyMismatchRejected() {
        fundAccounts();
        service.createAccount("C", "EUR", new BigDecimal("100"));
        assertThrows(IllegalArgumentException.class,
            () -> service.transfer("A", "C", new BigDecimal("50"), "USD", "tx-fx"));
    }

    // --- v2 item 2: symmetrical TRY phase with failure injection ---

    @Test
    public void testDestinationTryFailureCancelsSafely() {
        fundAccounts();
        List<String> calls = new ArrayList<>();
        TccTransactionCoordinatorV2.Status status = service.transfer("A", "B", new BigDecimal("100"), "USD", "tx-dest-fail",
            (dest, amount, currency) -> {
                calls.add(dest.accountId);
                throw new RuntimeException("destination shard unreachable");
            });
        assertEquals(TccTransactionCoordinatorV2.Status.FAILED, status);
        assertEquals(List.of("B"), calls);
        assertEquals(new BigDecimal("1000"), service.getAccount("A").balance);
        assertEquals(BigDecimal.ZERO, service.getAccount("A").heldBalance);
        assertEquals(new BigDecimal("500"), service.getAccount("B").balance);
        // No ledger entries beyond account funding: no money moved at all.
        assertEquals(4, ledger.getJournal().size());
    }

    @Test
    public void testDestinationTryHookCalledBeforeConfirm() {
        fundAccounts();
        List<String> phasesSeen = new ArrayList<>();
        TccTransactionCoordinatorV2.Status status = service.transfer("A", "B", new BigDecimal("100"), "USD", "tx-order",
            (dest, amount, currency) -> {
                phasesSeen.add(coordinator.getState(
                    service.idempotentTransactionId("tx-order")).phase.name());
                return true;
            });
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status);
        assertEquals(List.of("TRY"), phasesSeen);
    }

    @Test
    public void testFailedTransferHoldFullyReleased() {
        fundAccounts();
        TccTransactionCoordinatorV2.Status status = service.transfer("A", "B", new BigDecimal("10000"), "USD", "tx-hold");
        assertEquals(TccTransactionCoordinatorV2.Status.FAILED, status);
        assertEquals(BigDecimal.ZERO, service.getAccount("A").heldBalance);
    }

    // --- v2 item 3: expiring idempotency store ---

    private static class FakeClock implements java.util.function.LongSupplier {
        long now = 1_000_000L;
        public long getAsLong() { return now; }
        void advance(long millis) { now += millis; }
    }

    @Test
    public void testDuplicateWithinTtlReturnsCached() {
        FakeClock clock = new FakeClock();
        DigitalWalletServiceV2 svc = new DigitalWalletServiceV2(new DoubleEntryLedgerV2(), new TccTransactionCoordinatorV2(), 60_000L, clock);
        svc.createAccount("A", "USD", new BigDecimal("1000"));
        svc.createAccount("B", "USD", new BigDecimal("500"));
        TccTransactionCoordinatorV2.Status status1 = svc.transfer("A", "B", new BigDecimal("100"), "USD", "tx-ttl");
        clock.advance(30_000L);
        TccTransactionCoordinatorV2.Status status2 = svc.transfer("A", "B", new BigDecimal("100"), "USD", "tx-ttl");
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status1);
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status2);
        // Within the TTL the duplicate is rejected: money moved exactly once.
        assertEquals(new BigDecimal("900"), svc.getAccount("A").balance);
    }

    @Test
    public void testIdempotencyKeyExpiresAfterTtl() {
        FakeClock clock = new FakeClock();
        DigitalWalletServiceV2 svc = new DigitalWalletServiceV2(new DoubleEntryLedgerV2(), new TccTransactionCoordinatorV2(), 60_000L, clock);
        svc.createAccount("A", "USD", new BigDecimal("1000"));
        svc.createAccount("B", "USD", new BigDecimal("500"));
        TccTransactionCoordinatorV2.Status status1 = svc.transfer("A", "B", new BigDecimal("100"), "USD", "tx-ttl2");
        clock.advance(61_000L);
        TccTransactionCoordinatorV2.Status status2 = svc.transfer("A", "B", new BigDecimal("100"), "USD", "tx-ttl2");
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status1);
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status2);
        // After expiry the key can be reused: a genuine retry executes again.
        assertEquals(new BigDecimal("800"), svc.getAccount("A").balance);
        assertEquals(new BigDecimal("700"), svc.getAccount("B").balance);
    }

    @Test
    public void testExpiredEntriesPurgedFromStore() {
        FakeClock clock = new FakeClock();
        DigitalWalletServiceV2 svc = new DigitalWalletServiceV2(new DoubleEntryLedgerV2(), new TccTransactionCoordinatorV2(), 60_000L, clock);
        svc.createAccount("A", "USD", new BigDecimal("1000"));
        svc.createAccount("B", "USD", new BigDecimal("500"));
        svc.transfer("A", "B", new BigDecimal("50"), "USD", "tx-a");
        assertEquals(1, svc.idempotencyStoreSize());
        clock.advance(120_000L);
        svc.transfer("A", "B", new BigDecimal("50"), "USD", "tx-b"); // triggers purge
        assertEquals(1, svc.idempotencyStoreSize()); // tx-a purged, tx-b recorded
    }

    @Test
    public void testDefaultStoreHasNoExpiry() {
        fundAccounts();
        service.transfer("A", "B", new BigDecimal("100"), "USD", "tx-no-ttl");
        TccTransactionCoordinatorV2.Status status = service.transfer("A", "B", new BigDecimal("100"), "USD", "tx-no-ttl");
        assertEquals(TccTransactionCoordinatorV2.Status.SUCCESS, status);
        assertEquals(new BigDecimal("900"), service.getAccount("A").balance);
    }
}
