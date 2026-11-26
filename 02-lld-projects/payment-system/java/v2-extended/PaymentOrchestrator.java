import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * PaymentOrchestrator for payment-system (v2-extended).
 */
public class PaymentOrchestrator {
    private final String id;
    private final GatewayRouterStrategy gateway;
    private final IdempotencyService idempotency;
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

    public PaymentOrchestrator() {
        this.id = "PaymentOrchestrator";
        this.gateway = new GatewayRouterStrategy();
        this.idempotency = new IdempotencyService();
        this.transactions = new ConcurrentHashMap<>();
        this.txCounter = new AtomicInteger(0);
    }

    public PaymentResponse processPayment(PaymentRequest req) {
        String payloadHash = req.amount + "-" + req.currency + "-" + req.token;
        
        // 1. Idempotency Check
        String cachedResponse = idempotency.checkOrAcquire(req.idempotencyKey, payloadHash);
        if (cachedResponse != null) {
            String[] parts = cachedResponse.split(":");
            return new PaymentResponse(parts[0], parts[1]);
        }

        // 2. Database Initialization
        String txId = "tx_" + txCounter.incrementAndGet();
        Transaction tx = new Transaction(txId, req.idempotencyKey, req.amount, TransactionState.INITIATED);
        transactions.put(txId, tx);

        // 3. Gateway Invocation
        synchronized (tx) {
            if (tx.state == TransactionState.INITIATED) {
                tx.state = TransactionState.GATEWAY_PENDING;
            }
        }

        PaymentResponse response = null;
        try {
            GatewayRouterStrategy.GatewayResponse gwResp = gateway.charge(req.amount, req.token);
            synchronized (tx) {
                if (tx.state == TransactionState.COMPLETED || tx.state == TransactionState.DECLINED || tx.state == TransactionState.FAILED) {
                    response = new PaymentResponse(tx.state.name(), txId);
                } else if ("SUCCESS".equals(gwResp.status)) {
                    tx.state = TransactionState.COMPLETED;
                    tx.gatewayReferenceId = gwResp.referenceId;
                    response = new PaymentResponse("SUCCESS", txId);
                } else {
                    tx.state = TransactionState.DECLINED;
                    response = new PaymentResponse("DECLINED", txId);
                }
            }
        } catch (Exception e) {
            if ("Ambiguous gateway timeout".equals(e.getMessage())) {
                synchronized (tx) {
                    if (tx.state == TransactionState.COMPLETED || tx.state == TransactionState.DECLINED || tx.state == TransactionState.FAILED) {
                        response = new PaymentResponse(tx.state.name(), txId);
                    } else {
                        response = new PaymentResponse("PENDING", txId);
                    }
                }
            } else {
                synchronized (tx) {
                    if (tx.state == TransactionState.COMPLETED || tx.state == TransactionState.DECLINED || tx.state == TransactionState.FAILED) {
                        response = new PaymentResponse(tx.state.name(), txId);
                    } else {
                        tx.state = TransactionState.FAILED;
                        response = new PaymentResponse("FAILED", txId);
                    }
                }
            }
        }

        idempotency.saveResponse(req.idempotencyKey, response.status + ":" + response.transactionId);
        return response;
    }

    public void reconcileTransaction(String txId, TransactionState newState) {
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
        return "PaymentOrchestrator:" + id;
    }
}
