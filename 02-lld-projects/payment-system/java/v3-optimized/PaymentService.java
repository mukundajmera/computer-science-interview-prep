import java.util.Map;
import java.util.HashMap;
import java.util.Collections;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * PaymentService for payment-system (v3-optimized).
 */
public class PaymentService {
    private final String id;
    
    private final CircuitBreakerGatewayClient gateway;
    private final Map<String, CacheEntry> idempotencyStore;
    private final Map<String, Transaction> transactions;
    private final AtomicInteger txCounter;
    
    public enum TransactionState {
        INITIATED,
        GATEWAY_PENDING,
        COMPLETED,
        DECLINED,
        FAILED
    }

    public static class PaymentRequest {
        public String idempotencyKey;
        public int amount;
        public String currency;
        public String token;

        public PaymentRequest(String idempotencyKey, int amount, String currency, String token) {
            this.idempotencyKey = idempotencyKey;
            this.amount = amount;
            this.currency = currency;
            this.token = token;
        }
    }

    public static class Transaction {
        public String id;
        public String idempotencyKey;
        public int amount;
        public TransactionState state;
        public String gatewayReferenceId;

        public Transaction(String id, String idempotencyKey, int amount, TransactionState state) {
            this.id = id;
            this.idempotencyKey = idempotencyKey;
            this.amount = amount;
            this.state = state;
        }
    }

    public static class PaymentResponse {
        public String status;
        public String transactionId;

        public PaymentResponse(String status, String transactionId) {
            this.status = status;
            this.transactionId = transactionId;
        }
        
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            PaymentResponse that = (PaymentResponse) o;
            if (status != null ? !status.equals(that.status) : that.status != null) return false;
            return transactionId != null ? transactionId.equals(that.transactionId) : that.transactionId == null;
        }
    }

    private static class CacheEntry {
        String payloadHash;
        PaymentResponse response;

        CacheEntry(String payloadHash) {
            this.payloadHash = payloadHash;
        }
    }

    public PaymentService() {
        this.id = "PaymentService";
        this.gateway = new CircuitBreakerGatewayClient();
        this.idempotencyStore = Collections.synchronizedMap(new HashMap<>());
        this.transactions = Collections.synchronizedMap(new HashMap<>());
        this.txCounter = new AtomicInteger(0);
    }

    public PaymentResponse processPayment(PaymentRequest req) {
        String payloadHash = req.amount + "-" + req.currency + "-" + req.token;
        
        synchronized (idempotencyStore) {
            CacheEntry entry = idempotencyStore.get(req.idempotencyKey);
            if (entry != null) {
                if (!entry.payloadHash.equals(payloadHash)) {
                    throw new IllegalArgumentException("Repeated idempotency key with changed payload");
                }
                if (entry.response != null) {
                    return entry.response;
                } else {
                    // In flight
                    return new PaymentResponse("IN_PROGRESS", "Request currently processing");
                }
            } else {
                idempotencyStore.put(req.idempotencyKey, new CacheEntry(payloadHash));
            }
        }

        String txId = "tx_" + txCounter.incrementAndGet();
        Transaction tx = new Transaction(txId, req.idempotencyKey, req.amount, TransactionState.INITIATED);
        transactions.put(txId, tx);

        synchronized (tx) {
            if (tx.state == TransactionState.INITIATED) {
                tx.state = TransactionState.GATEWAY_PENDING;
            }
        }

        PaymentResponse response = null;
        try {
            CircuitBreakerGatewayClient.GatewayResponse gwResp = gateway.charge(req.amount, req.token);
            synchronized (tx) {
                if (tx.state != TransactionState.COMPLETED && 
                    tx.state != TransactionState.DECLINED && 
                    tx.state != TransactionState.FAILED) {
                    if ("SUCCESS".equals(gwResp.status)) {
                        tx.state = TransactionState.COMPLETED;
                        tx.gatewayReferenceId = gwResp.referenceId;
                        response = new PaymentResponse("SUCCESS", txId);
                    } else {
                        tx.state = TransactionState.DECLINED;
                        response = new PaymentResponse("DECLINED", txId);
                    }
                } else {
                    response = new PaymentResponse(tx.state.name(), txId);
                }
            }
        } catch (TimeoutException e) {
            response = new PaymentResponse("PENDING", txId);
        } catch (Exception e) {
            synchronized (tx) {
                if (tx.state != TransactionState.COMPLETED && 
                    tx.state != TransactionState.DECLINED && 
                    tx.state != TransactionState.FAILED) {
                    tx.state = TransactionState.FAILED;
                }
            }
            response = new PaymentResponse("FAILED", txId);
        }

        CacheEntry entry = idempotencyStore.get(req.idempotencyKey);
        if (entry != null) {
            entry.response = response;
        }

        return response;
    }

    public void handleWebhook(String txId, TransactionState newState) {
        Transaction tx = transactions.get(txId);
        if (tx == null) return;

        synchronized (tx) {
            if (tx.state == TransactionState.COMPLETED || 
                tx.state == TransactionState.DECLINED || 
                tx.state == TransactionState.FAILED) {
                return;
            }
            tx.state = newState;
        }
    }
    
    public Transaction getTransaction(String txId) {
        return transactions.get(txId);
    }
    
    public int getTransactionCount() {
        return transactions.size();
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "PaymentService:" + id;
    }
}
