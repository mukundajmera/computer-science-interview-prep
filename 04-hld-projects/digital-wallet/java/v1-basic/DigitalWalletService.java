import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.List;
import java.util.Arrays;
import java.util.UUID;
import java.util.Collections;

public class DigitalWalletService {
    private final DoubleEntryLedger ledger;
    private final TccTransactionCoordinator coordinator;
    
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

    private final Map<String, Account> accounts = new ConcurrentHashMap<>();
    private final Map<String, String> idempotencyStore = new ConcurrentHashMap<>();

    public DigitalWalletService(DoubleEntryLedger ledger, TccTransactionCoordinator coordinator) {
        this.ledger = ledger;
        this.coordinator = coordinator;
    }

    public void createAccount(String accountId, String currency, BigDecimal initialBalance) {
        accounts.put(accountId, new Account(accountId, currency, initialBalance));
        if (initialBalance.compareTo(BigDecimal.ZERO) > 0) {
            String transactionId = UUID.randomUUID().toString();
            DoubleEntryLedger.LedgerEntry credit = new DoubleEntryLedger.LedgerEntry(transactionId, accountId, DoubleEntryLedger.EntryType.CREDIT, initialBalance, currency);
            DoubleEntryLedger.LedgerEntry debit = new DoubleEntryLedger.LedgerEntry(transactionId, "SYSTEM", DoubleEntryLedger.EntryType.DEBIT, initialBalance, currency);
            ledger.commitTransaction(Arrays.asList(credit, debit));
        }
    }

    public Account getAccount(String accountId) {
        return accounts.get(accountId);
    }

    public synchronized TccTransactionCoordinator.Status transfer(String fromAccount, String toAccount, BigDecimal amount, String currency, String idempotencyKey) {
        if (idempotencyStore.containsKey(idempotencyKey)) {
            String txId = idempotencyStore.get(idempotencyKey);
            TccTransactionCoordinator.TransactionState state = coordinator.getState(txId);
            return state != null ? state.status : TccTransactionCoordinator.Status.PENDING;
        }

        String transactionId = UUID.randomUUID().toString();
        idempotencyStore.put(idempotencyKey, transactionId);

        Account src = accounts.get(fromAccount);
        Account dest = accounts.get(toAccount);

        if (src == null || dest == null) {
            coordinator.initiateTry(transactionId, fromAccount, toAccount, amount);
            coordinator.cancel(transactionId);
            return TccTransactionCoordinator.Status.FAILED;
        }

        if (src.balance.compareTo(amount) < 0) {
            coordinator.initiateTry(transactionId, fromAccount, toAccount, amount);
            coordinator.cancel(transactionId);
            return TccTransactionCoordinator.Status.FAILED;
        }

        // TRY
        coordinator.initiateTry(transactionId, fromAccount, toAccount, amount);
        src.balance = src.balance.subtract(amount);
        src.heldBalance = src.heldBalance.add(amount);

        // Process (Simulated Destination logic)
        try {
            // Check out of order flag (simulating a concurrent cancel arriving early)
            if (coordinator.getState(transactionId).outOfOrderFlag) {
                throw new IllegalStateException("Out of order cancel flag detected");
            }

            // CONFIRM
            coordinator.confirm(transactionId);
            src.heldBalance = src.heldBalance.subtract(amount);
            dest.balance = dest.balance.add(amount);

            DoubleEntryLedger.LedgerEntry debit = new DoubleEntryLedger.LedgerEntry(transactionId, fromAccount, DoubleEntryLedger.EntryType.DEBIT, amount, currency);
            DoubleEntryLedger.LedgerEntry credit = new DoubleEntryLedger.LedgerEntry(transactionId, toAccount, DoubleEntryLedger.EntryType.CREDIT, amount, currency);
            ledger.commitTransaction(Arrays.asList(debit, credit));

            return TccTransactionCoordinator.Status.SUCCESS;
        } catch (Exception e) {
            // CANCEL (Compensation)
            coordinator.cancel(transactionId);
            src.heldBalance = src.heldBalance.subtract(amount);
            src.balance = src.balance.add(amount);
            return TccTransactionCoordinator.Status.FAILED;
        }
    }

    public synchronized void simulateOutOfOrderCancel(String idempotencyKey) {
        String txId = idempotencyStore.get(idempotencyKey);
        if (txId == null) {
             txId = UUID.randomUUID().toString();
             idempotencyStore.put(idempotencyKey, txId);
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
        
        List<DoubleEntryLedger.LedgerEntry> entries = ledger.getJournal();
        for (DoubleEntryLedger.LedgerEntry entry : entries) {
            if ("SYSTEM".equals(entry.accountId)) continue;
            Account acc = accounts.get(entry.accountId);
            if (acc != null) {
                if (entry.entryType == DoubleEntryLedger.EntryType.CREDIT) {
                    acc.balance = acc.balance.add(entry.amount);
                } else if (entry.entryType == DoubleEntryLedger.EntryType.DEBIT) {
                    acc.balance = acc.balance.subtract(entry.amount);
                }
            }
        }
    }
}
