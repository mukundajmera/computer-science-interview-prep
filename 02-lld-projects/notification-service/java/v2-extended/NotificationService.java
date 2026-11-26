import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.Set;
import java.util.Collections;

public class NotificationService {
    public enum IntentState {
        PENDING, IN_PROGRESS, COMPLETED, FAILED, CONFLICT
    }

    private Dispatcher dispatcher;
    private ConcurrentHashMap<String, IntentState> intents;
    private int capacity;
    private AtomicInteger currentSize;
    private Set<String> unsubscribedUsers;
    private int maxRetries;
    private ExecutorService executorService;

    public NotificationService(Dispatcher dispatcher, int capacity, int maxRetries) {
        this.dispatcher = dispatcher;
        this.capacity = capacity;
        this.intents = new ConcurrentHashMap<>();
        this.currentSize = new AtomicInteger(0);
        this.unsubscribedUsers = Collections.newSetFromMap(new ConcurrentHashMap<>());
        this.maxRetries = maxRetries;
        this.executorService = Executors.newCachedThreadPool();
    }

    public void unsubscribe(String userId) {
        unsubscribedUsers.add(userId);
    }

    public String generateIdempotencyKey(String event, String recipient, String channel) {
        return event + ":" + recipient + ":" + channel;
    }

    public IntentState submitIntent(String event, String recipient, String channel, String message, int priority) {
        if (unsubscribedUsers.contains(recipient)) {
            return IntentState.FAILED;
        }

        String idempotencyKey = generateIdempotencyKey(event, recipient, channel);

        IntentState existingState = intents.putIfAbsent(idempotencyKey, IntentState.PENDING);
        if (existingState != null) {
            return IntentState.CONFLICT;
        }

        while (true) {
            int curSize = currentSize.get();
            if (curSize >= capacity) {
                intents.put(idempotencyKey, IntentState.FAILED);
                return IntentState.FAILED;
            }
            if (currentSize.compareAndSet(curSize, curSize + 1)) {
                break;
            }
        }

        Notification notification = new Notification(recipient, idempotencyKey + "|" + message, channel, priority);
        executorService.submit(() -> {
            try {
                processIntent(idempotencyKey, notification);
            } finally {
                currentSize.decrementAndGet();
            }
        });

        return IntentState.PENDING;
    }

    private void processIntent(String idempotencyKey, Notification notification) {
        intents.put(idempotencyKey, IntentState.IN_PROGRESS);
        int attempts = 0;
        boolean success = false;
        
        while (attempts <= maxRetries && !success) {
            attempts++;
            try {
                Channel channel = dispatcher.getChannel(notification.getChannelType());
                if (channel != null) {
                    success = channel.send(notification);
                }
            } catch (Exception e) {
                success = false;
            }
        }
        
        if (success) {
            intents.put(idempotencyKey, IntentState.COMPLETED);
        } else {
            intents.put(idempotencyKey, IntentState.FAILED);
        }
    }

    public IntentState getIntentState(String idempotencyKey) {
        return intents.get(idempotencyKey);
    }

    public void wrapChannel(String channelType, Channel originalChannel) {
        dispatcher.setChannel(channelType, originalChannel);
    }
    
    public void shutdown() {
        if (executorService != null) {
            executorService.shutdown();
        }
    }
}
