import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.UUID;
import java.time.Instant;

public class TccTransactionCoordinator {
    public enum Phase { TRY, CONFIRM, CANCEL }
    public enum Status { PENDING, SUCCESS, FAILED }

    public static class TransactionState {
        public final String transactionId;
        public final String fromAccount;
        public final String toAccount;
        public final BigDecimal amount;
        public volatile Phase phase;
        public volatile Status status;
        public volatile boolean outOfOrderFlag;
        public volatile Instant updatedAt;

        public TransactionState(String transactionId, String fromAccount, String toAccount, BigDecimal amount) {
            this.transactionId = transactionId;
            this.fromAccount = fromAccount;
            this.toAccount = toAccount;
            this.amount = amount;
            this.phase = Phase.TRY;
            this.status = Status.PENDING;
            this.outOfOrderFlag = false;
            this.updatedAt = Instant.now();
        }
    }

    private final Map<String, TransactionState> activeTransactions = new ConcurrentHashMap<>();

    public TransactionState initiateTry(String transactionId, String fromAccount, String toAccount, BigDecimal amount) {
        TransactionState state = new TransactionState(transactionId, fromAccount, toAccount, amount);
        activeTransactions.put(transactionId, state);
        return state;
    }

    public synchronized TransactionState confirm(String transactionId) {
        TransactionState state = activeTransactions.get(transactionId);
        if (state == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        if (state.status == Status.FAILED && state.phase == Phase.CANCEL) {
             throw new IllegalStateException("Cannot confirm a cancelled transaction");
        }
        if (state.phase == Phase.CANCEL && state.outOfOrderFlag) {
             // Out of order case: Cancel was received before confirm or retry
             throw new IllegalStateException("Transaction was already marked for cancellation");
        }
        state.phase = Phase.CONFIRM;
        state.status = Status.SUCCESS;
        state.updatedAt = Instant.now();
        return state;
    }

    public synchronized TransactionState cancel(String transactionId) {
        TransactionState state = activeTransactions.get(transactionId);
        if (state == null) {
             // Out of order: Cancel before Try
             state = new TransactionState(transactionId, "unknown", "unknown", BigDecimal.ZERO);
             state.outOfOrderFlag = true;
             state.phase = Phase.CANCEL;
             state.status = Status.FAILED;
             activeTransactions.put(transactionId, state);
             return state;
        }
        if (state.phase == Phase.CONFIRM) {
            throw new IllegalStateException("Cannot cancel an already confirmed transaction");
        }
        state.phase = Phase.CANCEL;
        state.status = Status.FAILED;
        state.updatedAt = Instant.now();
        return state;
    }

    public TransactionState getState(String transactionId) {
        return activeTransactions.get(transactionId);
    }
}
