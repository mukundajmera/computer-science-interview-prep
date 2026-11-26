import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Optional;
import java.time.Instant;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.nio.charset.StandardCharsets;

public class PaymentService {

    public enum PaymentState {
        CREATED, PROCESSING, AUTHORIZED, CAPTURED, REFUND_PENDING, REFUNDED, PARTIALLY_REFUNDED, FAILED, VOIDED
    }

    public enum TransactionType {
        AUTHORIZE, CAPTURE, REFUND, VOID
    }

    public static class PaymentIntent {
        public String id;
        public String merchantId;
        public String customerId;
        public long amountMinor;
        public String currency;
        public PaymentState state;
        public Instant createdAt;
        public long capturedAmount = 0;
        public long refundedAmount = 0;
    }

    public static class IdempotencyRecord {
        public String idempotencyKey;
        public String payloadHash;
        public Object response;
    }

    public static class PaymentTransaction {
        public String transactionId;
        public String intentId;
        public TransactionType type;
        public long amount;
        public Instant createdAt;
    }

    public static class LedgerEntry {
        public String id;
        public String transactionId;
        public String accountId;
        public long amount; // positive for credit, negative for debit
        public Instant createdAt;
    }

    private Map<String, PaymentIntent> intents = new HashMap<>();
    private Map<String, IdempotencyRecord> idempotencyRecords = new HashMap<>();
    private List<PaymentTransaction> transactions = new ArrayList<>();
    private List<LedgerEntry> ledger = new ArrayList<>();

    private String hashPayload(Object payload) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] encodedhash = digest.digest(payload.toString().getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder(2 * encodedhash.length);
            for (int i = 0; i < encodedhash.length; i++) {
                String hex = Integer.toHexString(0xff & encodedhash[i]);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    private void recordLedger(String transactionId, String fromAccount, String toAccount, long amount) {
        LedgerEntry debit = new LedgerEntry();
        debit.id = UUID.randomUUID().toString();
        debit.transactionId = transactionId;
        debit.accountId = fromAccount;
        debit.amount = -amount;
        debit.createdAt = Instant.now();

        LedgerEntry credit = new LedgerEntry();
        credit.id = UUID.randomUUID().toString();
        credit.transactionId = transactionId;
        credit.accountId = toAccount;
        credit.amount = amount;
        credit.createdAt = Instant.now();

        ledger.add(debit);
        ledger.add(credit);
    }

    public synchronized PaymentIntent createPaymentIntent(String idempotencyKey, String merchantId, String customerId, long amountMinor, String currency) {
        String payload = merchantId + customerId + amountMinor + currency;
        String payloadHash = hashPayload(payload);

        if (idempotencyRecords.containsKey(idempotencyKey)) {
            IdempotencyRecord record = idempotencyRecords.get(idempotencyKey);
            if (!record.payloadHash.equals(payloadHash)) {
                throw new IllegalStateException("duplicate_idempotency_key");
            }
            return (PaymentIntent) record.response;
        }

        PaymentIntent intent = new PaymentIntent();
        intent.id = "pi_" + UUID.randomUUID().toString();
        intent.merchantId = merchantId;
        intent.customerId = customerId;
        intent.amountMinor = amountMinor;
        intent.currency = currency;
        intent.state = PaymentState.CREATED;
        intent.createdAt = Instant.now();

        intents.put(intent.id, intent);

        IdempotencyRecord record = new IdempotencyRecord();
        record.idempotencyKey = idempotencyKey;
        record.payloadHash = payloadHash;
        record.response = intent;
        idempotencyRecords.put(idempotencyKey, record);

        return intent;
    }

    public synchronized PaymentTransaction authorize(String intentId) {
        PaymentIntent intent = intents.get(intentId);
        if (intent == null) throw new IllegalArgumentException("Intent not found");
        if (intent.state != PaymentState.CREATED) {
            throw new IllegalStateException("invalid_state_transition");
        }

        intent.state = PaymentState.AUTHORIZED;

        PaymentTransaction txn = new PaymentTransaction();
        txn.transactionId = "txn_" + UUID.randomUUID().toString();
        txn.intentId = intentId;
        txn.type = TransactionType.AUTHORIZE;
        txn.amount = intent.amountMinor;
        txn.createdAt = Instant.now();
        transactions.add(txn);

        return txn;
    }

    public synchronized PaymentTransaction capture(String intentId) {
        PaymentIntent intent = intents.get(intentId);
        if (intent == null) throw new IllegalArgumentException("Intent not found");
        if (intent.state != PaymentState.AUTHORIZED) {
            throw new IllegalStateException("invalid_state_transition");
        }

        intent.state = PaymentState.CAPTURED;
        intent.capturedAmount = intent.amountMinor;

        PaymentTransaction txn = new PaymentTransaction();
        txn.transactionId = "txn_" + UUID.randomUUID().toString();
        txn.intentId = intentId;
        txn.type = TransactionType.CAPTURE;
        txn.amount = intent.amountMinor;
        txn.createdAt = Instant.now();
        transactions.add(txn);

        recordLedger(txn.transactionId, intent.customerId, intent.merchantId, intent.amountMinor);

        return txn;
    }

    public synchronized PaymentTransaction refund(String intentId, long amount) {
        PaymentIntent intent = intents.get(intentId);
        if (intent == null) throw new IllegalArgumentException("Intent not found");
        if (intent.state != PaymentState.CAPTURED && intent.state != PaymentState.PARTIALLY_REFUNDED) {
            throw new IllegalStateException("invalid_state_transition");
        }
        if (intent.refundedAmount + amount > intent.capturedAmount) {
            throw new IllegalArgumentException("Refund amount exceeds captured amount");
        }

        intent.state = PaymentState.REFUND_PENDING;
        // Simulating immediate success for basic v1
        intent.refundedAmount += amount;
        if (intent.refundedAmount == intent.capturedAmount) {
            intent.state = PaymentState.REFUNDED;
        } else {
            intent.state = PaymentState.PARTIALLY_REFUNDED;
        }

        PaymentTransaction txn = new PaymentTransaction();
        txn.transactionId = "txn_" + UUID.randomUUID().toString();
        txn.intentId = intentId;
        txn.type = TransactionType.REFUND;
        txn.amount = amount;
        txn.createdAt = Instant.now();
        transactions.add(txn);

        recordLedger(txn.transactionId, intent.merchantId, intent.customerId, amount);

        return txn;
    }

    public synchronized PaymentTransaction voidPayment(String intentId) {
        PaymentIntent intent = intents.get(intentId);
        if (intent == null) throw new IllegalArgumentException("Intent not found");
        if (intent.state != PaymentState.AUTHORIZED) {
            throw new IllegalStateException("invalid_state_transition");
        }

        intent.state = PaymentState.VOIDED;

        PaymentTransaction txn = new PaymentTransaction();
        txn.transactionId = "txn_" + UUID.randomUUID().toString();
        txn.intentId = intentId;
        txn.type = TransactionType.VOID;
        txn.amount = intent.amountMinor;
        txn.createdAt = Instant.now();
        transactions.add(txn);

        return txn;
    }

    public PaymentIntent getIntent(String intentId) {
        return intents.get(intentId);
    }

    public List<PaymentTransaction> getTransactions(String intentId) {
        List<PaymentTransaction> result = new ArrayList<>();
        for (PaymentTransaction txn : transactions) {
            if (txn.intentId.equals(intentId)) {
                result.add(txn);
            }
        }
        return result;
    }

    public List<LedgerEntry> getLedger() {
        return Collections.unmodifiableList(ledger);
    }
}
