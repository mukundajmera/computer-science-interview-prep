/**
 * v2-extended digital wallet service.
 *
 * Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
 * 1. Transfer input validation: non-positive amounts, same-account transfers,
 *    missing accounts, and currency mismatches are rejected with
 *    IllegalArgumentException BEFORE any TRY phase begins. v1 accepted a
 *    negative amount, which would have silently created money (source balance
 *    minus a negative number).
 * 2. Symmetrical TRY phase with failure injection (PITFALLS #2): both the
 *    source hold AND a destination TRY hook must succeed before any CONFIRM.
 *    The injectable DestinationTryHook simulates the remote destination
 *    shard; if it fails or times out, the source hold is cancelled and no
 *    credit is ever applied, so a dropped ACK cannot duplicate money.
 * 3. Expiring idempotency store (PITFALLS #3, "expiry or eviction"): entries
 *    carry a timestamp from an injectable clock and expire after a
 *    configurable TTL, mirroring a Redis-backed reject layer; expired keys
 *    are purged so the store stays bounded and keys can be reused safely.
 */

import java.math.BigDecimal;
import java.util.Map;
import java.util.Iterator;
import java.util.concurrent.ConcurrentHashMap;
import java.util.List;
import java.util.Arrays;
import java.util.UUID;
import java.util.function.LongSupplier;

public class DigitalWalletServiceV2 {
    private final DoubleEntryLedgerV2 ledger;
    private final TccTransactionCoordinatorV2 coordinator;

    // Simplistic account store
    public static class Account {
        public final String accountId;
        public final String currency;
        public BigDecimal balance;
        public BigDecimal heldBalance;

        public Account(String accountId, String currency, BigDecimal balance) {
            this.accountId = accountId;
            this.currency = currency;
            this.balance = balance;
            this.heldBalance = BigDecimal.ZERO;
        }
    }

    // key -> (transactionId, recordedAtMillis) so entries can expire (v2 item 3)
    public static class IdempotencyRecord {
        public final String transactionId;
        public final long recordedAtMillis;

        public IdempotencyRecord(String transactionId, long recordedAtMillis) {
            this.transactionId = transactionId;
            this.recordedAtMillis = recordedAtMillis;
        }
    }

    // Simulates the remote destination shard's TRY. Throwing or returning
    // false means the destination cannot accept the credit.
    @FunctionalInterface
    public interface DestinationTryHook {
        boolean tryDestination(Account destination, BigDecimal amount, String currency);
    }

    private static final DestinationTryHook DEFAULT_DESTINATION_TRY =
        (destination, amount, currency) -> destination != null && destination.currency.equals(currency);

    private final Map<String, Account> accounts = new ConcurrentHashMap<>();
    private final Map<String, IdempotencyRecord> idempotencyStore = new ConcurrentHashMap<>();
    private final Long idempotencyTtlMillis;
    private final LongSupplier clockMillis;

    public DigitalWalletServiceV2(DoubleEntryLedgerV2 ledger, TccTransactionCoordinatorV2 coordinator) {
        this(ledger, coordinator, null, System::currentTimeMillis);
    }

    public DigitalWalletServiceV2(DoubleEntryLedgerV2 ledger, TccTransactionCoordinatorV2 coordinator,
                                  Long idempotencyTtlMillis, LongSupplier clockMillis) {
        if (idempotencyTtlMillis != null && idempotencyTtlMillis <= 0) {
            throw new IllegalArgumentException("idempotencyTtlMillis must be positive or null");
        }
        if (clockMillis == null) {
            throw new IllegalArgumentException("clockMillis must not be null");
        }
        this.ledger = ledger;
        this.coordinator = coordinator;
        this.idempotencyTtlMillis = idempotencyTtlMillis;
        this.clockMillis = clockMillis;
    }

    public void createAccount(String accountId, String currency, BigDecimal initialBalance) {
        if (initialBalance.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("initialBalance must be >= 0");
        }
        accounts.put(accountId, new Account(accountId, currency, initialBalance));
        if (initialBalance.compareTo(BigDecimal.ZERO) > 0) {
            String transactionId = UUID.randomUUID().toString();
            DoubleEntryLedgerV2.LedgerEntry credit = new DoubleEntryLedgerV2.LedgerEntry(transactionId, accountId, DoubleEntryLedgerV2.EntryType.CREDIT, initialBalance, currency);
            DoubleEntryLedgerV2.LedgerEntry debit = new DoubleEntryLedgerV2.LedgerEntry(transactionId, "SYSTEM", DoubleEntryLedgerV2.EntryType.DEBIT, initialBalance, currency);
            ledger.commitTransaction(Arrays.asList(credit, debit));
        }
    }

    public Account getAccount(String accountId) {
        return accounts.get(accountId);
    }

    public int idempotencyStoreSize() {
        return idempotencyStore.size();
    }

    public String idempotentTransactionId(String idempotencyKey) {
        IdempotencyRecord record = idempotencyStore.get(idempotencyKey);
        return record != null ? record.transactionId : null;
    }

    private void purgeExpiredIdempotencyKeys() {
        if (idempotencyTtlMillis == null) {
            return;
        }
        long now = clockMillis.getAsLong();
        Iterator<Map.Entry<String, IdempotencyRecord>> it = idempotencyStore.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<String, IdempotencyRecord> entry = it.next();
            if (now - entry.getValue().recordedAtMillis > idempotencyTtlMillis) {
                it.remove();
            }
        }
    }

    public synchronized TccTransactionCoordinatorV2.Status transfer(String fromAccount, String toAccount, BigDecimal amount, String currency, String idempotencyKey) {
        return transfer(fromAccount, toAccount, amount, currency, idempotencyKey, DEFAULT_DESTINATION_TRY);
    }

    public synchronized TccTransactionCoordinatorV2.Status transfer(String fromAccount, String toAccount, BigDecimal amount, String currency, String idempotencyKey, DestinationTryHook destinationTry) {
        purgeExpiredIdempotencyKeys();
        IdempotencyRecord cached = idempotencyStore.get(idempotencyKey);
        if (cached != null) {
            TccTransactionCoordinatorV2.TransactionState state = coordinator.getState(cached.transactionId);
            return state != null ? state.status : TccTransactionCoordinatorV2.Status.PENDING;
        }

        // v2 item 1: validate inputs BEFORE any TRY phase begins.
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("amount must be positive");
        }
        if (fromAccount.equals(toAccount)) {
            throw new IllegalArgumentException("fromAccount and toAccount must differ");
        }
        Account src = accounts.get(fromAccount);
        Account dest = accounts.get(toAccount);
        if (src == null || dest == null) {
            throw new IllegalArgumentException("both accounts must exist");
        }
        if (!src.currency.equals(currency) || !dest.currency.equals(currency)) {
            throw new IllegalArgumentException("currency mismatch between accounts and transfer");
        }

        String transactionId = UUID.randomUUID().toString();
        idempotencyStore.put(idempotencyKey, new IdempotencyRecord(transactionId, clockMillis.getAsLong()));

        if (src.balance.compareTo(amount) < 0) {
            coordinator.initiateTry(transactionId, fromAccount, toAccount, amount);
            coordinator.cancel(transactionId);
            return TccTransactionCoordinatorV2.Status.FAILED;
        }

        // TRY (v2 item 2): source hold AND destination TRY must both succeed
        // before any CONFIRM is sent.
        coordinator.initiateTry(transactionId, fromAccount, toAccount, amount);
        src.balance = src.balance.subtract(amount);
        src.heldBalance = src.heldBalance.add(amount);

        try {
            if (coordinator.getState(transactionId).outOfOrderFlag) {
                throw new IllegalStateException("Out of order cancel flag detected");
            }

            if (!destinationTry.tryDestination(dest, amount, currency)) {
                throw new IllegalStateException("Destination TRY failed or timed out");
            }
            coordinator.markDestinationTryDone(transactionId);

            // CONFIRM: only after BOTH TRY halves succeeded.
            coordinator.confirm(transactionId);
            src.heldBalance = src.heldBalance.subtract(amount);
            dest.balance = dest.balance.add(amount);

            DoubleEntryLedgerV2.LedgerEntry debit = new DoubleEntryLedgerV2.LedgerEntry(transactionId, fromAccount, DoubleEntryLedgerV2.EntryType.DEBIT, amount, currency);
            DoubleEntryLedgerV2.LedgerEntry credit = new DoubleEntryLedgerV2.LedgerEntry(transactionId, toAccount, DoubleEntryLedgerV2.EntryType.CREDIT, amount, currency);
            ledger.commitTransaction(Arrays.asList(debit, credit));

            return TccTransactionCoordinatorV2.Status.SUCCESS;
        } catch (Exception e) {
            // CANCEL: release the source hold; no credit was ever applied, so
            // a failed or timed-out destination TRY cannot create money.
            coordinator.cancel(transactionId);
            src.heldBalance = src.heldBalance.subtract(amount);
            src.balance = src.balance.add(amount);
            return TccTransactionCoordinatorV2.Status.FAILED;
        }
    }

    public synchronized void simulateOutOfOrderCancel(String idempotencyKey) {
        IdempotencyRecord record = idempotencyStore.get(idempotencyKey);
        String txId = record != null ? record.transactionId : null;
        if (txId == null) {
             txId = UUID.randomUUID().toString();
             idempotencyStore.put(idempotencyKey, new IdempotencyRecord(txId, clockMillis.getAsLong()));
        }
        coordinator.cancel(txId);
    }

    // Event sourcing replay
    public synchronized void replayEventSourcingHistory() {
        // Reset balances
        for (Account acc : accounts.values()) {
            acc.balance = BigDecimal.ZERO;
            acc.heldBalance = BigDecimal.ZERO;
        }

        List<DoubleEntryLedgerV2.LedgerEntry> entries = ledger.getJournal();
        for (DoubleEntryLedgerV2.LedgerEntry entry : entries) {
            if ("SYSTEM".equals(entry.accountId)) continue;
            Account acc = accounts.get(entry.accountId);
            if (acc != null) {
                if (entry.entryType == DoubleEntryLedgerV2.EntryType.CREDIT) {
                    acc.balance = acc.balance.add(entry.amount);
                } else if (entry.entryType == DoubleEntryLedgerV2.EntryType.DEBIT) {
                    acc.balance = acc.balance.subtract(entry.amount);
                }
            }
        }
    }
}
