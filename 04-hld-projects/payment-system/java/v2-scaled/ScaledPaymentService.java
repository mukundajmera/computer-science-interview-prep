import java.util.HashMap;
import java.util.Map;
import java.util.HashSet;
import java.util.Set;
import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;

public class ScaledPaymentService {

    public enum WebhookType {
        AUTHORIZED,
        CAPTURED,
        FAILED,
        REFUNDED
    }

    public static class WebhookEvent {
        public String eventId;
        public String intentId;
        public WebhookType eventType;
        public String payloadHash;
        public long timestamp;

        public WebhookEvent(String eventId, String intentId, WebhookType eventType, String payloadHash, long timestamp) {
            this.eventId = eventId;
            this.intentId = intentId;
            this.eventType = eventType;
            this.payloadHash = payloadHash;
            this.timestamp = timestamp;
        }
    }

    public enum PaymentState {
        CREATED(0),
        PROCESSING(1),
        AUTHORIZED(2),
        CAPTURED(3),
        REFUNDED(4),
        FAILED(5);

        private final int priority;
        PaymentState(int priority) {
            this.priority = priority;
        }
        public int getPriority() {
            return this.priority;
        }
    }

    public static class PaymentIntent {
        public String id;
        public int amount;
        public PaymentState state;
        public String gatewayRef;

        public PaymentIntent(String id, int amount, PaymentState state) {
            this.id = id;
            this.amount = amount;
            this.state = state;
        }
    }

    public static class RetryJob {
        public String gatewayRef;
        public int expectedAmount;
        public int failCount;
        public long nextRetryAt;

        public RetryJob(String gatewayRef, int expectedAmount, int failCount, long nextRetryAt) {
            this.gatewayRef = gatewayRef;
            this.expectedAmount = expectedAmount;
            this.failCount = failCount;
            this.nextRetryAt = nextRetryAt;
        }
    }

    private Map<String, PaymentIntent> intents = new HashMap<>();
    private Set<String> processedWebhooks = new HashSet<>();
    private List<RetryJob> deadLetterQueue = new ArrayList<>();
    private Map<String, WebhookType> outOfOrderStates = new HashMap<>();

    public PaymentIntent createIntent(String intentId, int amount) {
        if (intents.containsKey(intentId)) {
            throw new IllegalArgumentException("Intent already exists");
        }
        PaymentIntent intent = new PaymentIntent(intentId, amount, PaymentState.CREATED);
        intents.put(intentId, intent);
        return intent;
    }

    public boolean handleWebhook(WebhookEvent event) {
        if (processedWebhooks.contains(event.eventId)) {
            return false;
        }

        processedWebhooks.add(event.eventId);

        PaymentIntent intent = intents.get(event.intentId);
        if (intent == null) {
            outOfOrderStates.put(event.intentId, event.eventType);
            return true;
        }

        applyEventType(intent, event.eventType);
        return true;
    }

    private void applyEventType(PaymentIntent intent, WebhookType eventType) {
        PaymentState targetState;
        switch (eventType) {
            case AUTHORIZED: targetState = PaymentState.AUTHORIZED; break;
            case CAPTURED: targetState = PaymentState.CAPTURED; break;
            case REFUNDED: targetState = PaymentState.REFUNDED; break;
            case FAILED: targetState = PaymentState.FAILED; break;
            default: return;
        }

        if (targetState.getPriority() > intent.state.getPriority()) {
            intent.state = targetState;
        }
    }

    public boolean reconcileSettlementJob(String gatewayRef, int expectedAmount, int failCount) {
        PaymentIntent targetIntent = null;
        for (PaymentIntent intent : intents.values()) {
            if (gatewayRef.equals(intent.gatewayRef)) {
                targetIntent = intent;
                break;
            }
        }

        if (targetIntent == null || targetIntent.amount != expectedAmount) {
            long backoffSec = (long) Math.pow(2, failCount);
            deadLetterQueue.add(new RetryJob(
                gatewayRef,
                expectedAmount,
                failCount + 1,
                System.currentTimeMillis() + (backoffSec * 1000)
            ));
            return false;
        }

        if (targetIntent.state != PaymentState.CAPTURED) {
            targetIntent.state = PaymentState.CAPTURED;
        }

        return true;
    }

    public void processDlq() {
        long now = System.currentTimeMillis();
        Iterator<RetryJob> it = deadLetterQueue.iterator();
        List<RetryJob> toProcess = new ArrayList<>();

        while (it.hasNext()) {
            RetryJob job = it.next();
            if (job.nextRetryAt <= now) {
                toProcess.add(job);
                it.remove();
            }
        }

        for (RetryJob job : toProcess) {
            reconcileSettlementJob(job.gatewayRef, job.expectedAmount, job.failCount);
        }
    }

    public List<RetryJob> getDlq() {
        return deadLetterQueue;
    }
}
