import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class NotificationService {
    public enum IntentState {
        PENDING, IN_PROGRESS, COMPLETED, CONFLICT, FAILED
    }

    private final Dispatcher dispatcher;
    private final int capacity;
    private final int maxRetries;
    private final Map<String, IntentState> intentStates = new ConcurrentHashMap<>();
    private final Set<String> unsubscribedUsers = ConcurrentHashMap.newKeySet();
    private final ExecutorService executorService = Executors.newCachedThreadPool();
    private final AtomicInteger queueSize = new AtomicInteger(0);

    public NotificationService(Dispatcher dispatcher, int capacity, int maxRetries) {
        this.dispatcher = dispatcher;
        this.capacity = capacity;
        this.maxRetries = maxRetries;
    }

    public void unsubscribe(String userId) {
        unsubscribedUsers.add(userId);
    }

    public IntentState submitIntent(String event, String userId, String channelType, String message) {
        if (unsubscribedUsers.contains(userId)) {
            return IntentState.FAILED;
        }

        String idempotencyKey = event + ":" + userId + ":" + channelType;
        IntentState existingState = intentStates.putIfAbsent(idempotencyKey, IntentState.PENDING);
        if (existingState != null) {
            return IntentState.CONFLICT;
        }

        while (true) {
            int currentSize = queueSize.get();
            if (currentSize >= capacity) {
                intentStates.put(idempotencyKey, IntentState.FAILED);
                return IntentState.FAILED;
            }
            if (queueSize.compareAndSet(currentSize, currentSize + 1)) {
                break;
            }
        }

        executorService.submit(() -> {
            try {
                processIntent(idempotencyKey, new Notification(userId, message, channelType));
            } finally {
                queueSize.decrementAndGet();
            }
        });
        
        return IntentState.PENDING;
    }

    private void processIntent(String idempotencyKey, Notification notification) {
        intentStates.put(idempotencyKey, IntentState.IN_PROGRESS);
        int attempts = 0;
        boolean success = false;
        while (attempts <= maxRetries && !success) {
            attempts++;
            try {
                success = dispatcher.dispatch(notification);
            } catch (Exception e) {
                success = false;
            }
        }
        
        if (success) {
            intentStates.put(idempotencyKey, IntentState.COMPLETED);
        } else {
            intentStates.put(idempotencyKey, IntentState.FAILED);
        }
    }

    public IntentState getIntentState(String idempotencyKey) {
        return intentStates.get(idempotencyKey);
    }
}
