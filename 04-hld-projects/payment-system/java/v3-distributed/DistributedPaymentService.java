import java.util.concurrent.locks.ReentrantLock;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.nio.charset.StandardCharsets;

public class DistributedPaymentService {

    public enum PaymentState {
        CREATED, PROCESSING, PROCESSING_UNKNOWN, AUTHORIZED, CAPTURED, REFUND_PENDING, REFUNDED, PARTIALLY_REFUNDED, FAILED, VOIDED
    }

    public enum TransactionStatus {
        PENDING, IN_FLIGHT, SUCCESS, FAILED, UNKNOWN
    }

    public enum TransactionType {
        AUTHORIZE, CAPTURE, REFUND, VOID, TRANSFER
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

    public static class PaymentTransaction {
        public String transactionId;
        public String intentId;
        public TransactionType type;
        public long amount;
        public TransactionStatus status;
        public Instant createdAt;
    }

    public static class IdempotencyRecord {
        public String idempotencyKey;
        public String payloadHash;
        public String state; // IN_PROGRESS, SUCCEEDED
        public String lockOwner;
        public Instant leaseExpiresAt;
        public Object response;
    }

    public static class OutboxMessage {
        public String id;
        public String intentId;
        public String eventType;
        public String status;
        public Instant createdAt;
    }

    public static class SagaContext {
        public String sagaId;
        public List<String> stepsCompleted = new ArrayList<>();
        public boolean compensated = false;
    }

    private final Map<String, PaymentIntent> intents = new ConcurrentHashMap<>();
    private final Map<String, IdempotencyRecord> idempotencyRecords = new ConcurrentHashMap<>();
    private final List<PaymentTransaction> transactions = new CopyOnWriteArrayList<>();
    private final List<OutboxMessage> outbox = new CopyOnWriteArrayList<>();

    private boolean isPartitionTolerantDegraded = false;
    private final String regionId;

    // Simulate multi-region consensus via a mock lock manager
    private final Map<String, ReentrantLock> distributedLocks = new ConcurrentHashMap<>();

    public DistributedPaymentService(String regionId) {
        this.regionId = regionId;
    }

    public void setDegradedMode(boolean degraded) {
        this.isPartitionTolerantDegraded = degraded;
    }

    private String hashPayload(Object payload) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] encodedhash = digest.digest(payload.toString().getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder(2 * encodedhash.length);
            for (byte b : encodedhash) {
                String hex = Integer.toHexString(0xff & b);
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

    // Distributed lock simulation
    private void acquireLock(String key) {
        distributedLocks.computeIfAbsent(key, k -> new ReentrantLock()).lock();
    }

    private void releaseLock(String key) {
        ReentrantLock lock = distributedLocks.get(key);
        if (lock != null && lock.isHeldByCurrentThread()) {
            lock.unlock();
        }
    }

    public Object createOrConfirmIntent(String idempotencyKey, String merchantId, String customerId, long amountMinor, String currency) {
        String payload = merchantId + customerId + amountMinor + currency;
        String payloadHash = hashPayload(payload);
        String lockKey = "idem_" + idempotencyKey;

        acquireLock(lockKey);
        try {
            Instant now = Instant.now();
            IdempotencyRecord record = idempotencyRecords.get(idempotencyKey);

            if (record != null) {
                if (!record.payloadHash.equals(payloadHash)) {
                    throw new IllegalStateException("duplicate_idempotency_key");
                }
                if ("SUCCEEDED".equals(record.state)) {
                    return record.response;
                }
                if ("IN_PROGRESS".equals(record.state) && record.leaseExpiresAt.isAfter(now)) {
                    // 202 Accepted simulation
                    return "202_ACCEPTED";
                }
                // Lease expired, take over
            } else {
                record = new IdempotencyRecord();
                record.idempotencyKey = idempotencyKey;
                record.payloadHash = payloadHash;
            }

            record.state = "IN_PROGRESS";
            record.lockOwner = regionId + "_" + UUID.randomUUID().toString();
            record.leaseExpiresAt = now.plusSeconds(30);
            idempotencyRecords.put(idempotencyKey, record);

            // Create intent
            PaymentIntent intent = new PaymentIntent();
            intent.id = "pi_" + UUID.randomUUID().toString();
            intent.merchantId = merchantId;
            intent.customerId = customerId;
            intent.amountMinor = amountMinor;
            intent.currency = currency;
            intent.state = PaymentState.CREATED;
            intent.createdAt = Instant.now();

            intents.put(intent.id, intent);

            // Confirm authorization flow
            intent.state = PaymentState.PROCESSING;

            PaymentTransaction txn = new PaymentTransaction();
            txn.transactionId = "txn_" + UUID.randomUUID().toString();
            txn.intentId = intent.id;
            txn.type = TransactionType.AUTHORIZE;
            txn.amount = amountMinor;
            txn.status = TransactionStatus.IN_FLIGHT;
            txn.createdAt = Instant.now();
            transactions.add(txn);

            if (isPartitionTolerantDegraded) {
                // Fallback to async auth
                intent.state = PaymentState.PROCESSING;
                txn.status = TransactionStatus.UNKNOWN;

                OutboxMessage msg = new OutboxMessage();
                msg.id = UUID.randomUUID().toString();
                msg.intentId = intent.id;
                msg.eventType = "ASYNC_AUTH_POLL";
                msg.status = "PENDING";
                msg.createdAt = Instant.now();
                outbox.add(msg);

                record.state = "SUCCEEDED";
                record.response = intent;
                return intent;
            } else {
                // Synchronous provider call success
                intent.state = PaymentState.AUTHORIZED;
                txn.status = TransactionStatus.SUCCESS;

                record.state = "SUCCEEDED";
                record.response = intent;
                return intent;
            }
        } finally {
            releaseLock(lockKey);
        }
    }

    public PaymentTransaction capture(String intentId) {
        acquireLock("intent_" + intentId);
        try {
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
            txn.status = TransactionStatus.SUCCESS;
            txn.createdAt = Instant.now();
            transactions.add(txn);

            return txn;
        } finally {
            releaseLock("intent_" + intentId);
        }
    }

    // Simulate webhook handling for delayed auth
    public void handleProviderWebhook(String intentId, String status) {
        acquireLock("intent_" + intentId);
        try {
            PaymentIntent intent = intents.get(intentId);
            if (intent != null && intent.state == PaymentState.PROCESSING) {
                if ("SUCCESS".equals(status)) {
                    intent.state = PaymentState.AUTHORIZED;
                    updateTransactionStatus(intentId, TransactionType.AUTHORIZE, TransactionStatus.SUCCESS);
                } else if ("FAILED".equals(status)) {
                    intent.state = PaymentState.FAILED;
                    updateTransactionStatus(intentId, TransactionType.AUTHORIZE, TransactionStatus.FAILED);
                }
            }
        } finally {
            releaseLock("intent_" + intentId);
        }
    }

    private void updateTransactionStatus(String intentId, TransactionType type, TransactionStatus status) {
        for (PaymentTransaction txn : transactions) {
            if (txn.intentId.equals(intentId) && txn.type == type) {
                txn.status = status;
                break;
            }
        }
    }

    // Distributed Saga for multi-account transfers
    public SagaContext executeTransferSaga(String fromAccount, String toAccount, long amount) {
        SagaContext saga = new SagaContext();
        saga.sagaId = UUID.randomUUID().toString();

        boolean debitSuccess = false;
        boolean creditSuccess = false;

        try {
            // Step 1: Debit from account (Simulated)
            debitSuccess = simulateServiceCall(fromAccount, -amount);
            if (debitSuccess) {
                saga.stepsCompleted.add("DEBIT");
            } else {
                throw new RuntimeException("Debit failed");
            }

            // Step 2: Credit to account (Simulated)
            creditSuccess = simulateServiceCall(toAccount, amount);
            if (creditSuccess) {
                saga.stepsCompleted.add("CREDIT");
            } else {
                throw new RuntimeException("Credit failed");
            }

            return saga;
        } catch (Exception e) {
            // Compensating transaction
            if (debitSuccess && !creditSuccess) {
                simulateServiceCall(fromAccount, amount); // refund
                saga.compensated = true;
            }
            throw new RuntimeException("Saga aborted and compensated", e);
        }
    }

    private boolean simulateServiceCall(String account, long amount) {
        // Mock success, except when account contains "fail"
        return !account.contains("fail");
    }

    public PaymentIntent getIntent(String intentId) {
        return intents.get(intentId);
    }
}
