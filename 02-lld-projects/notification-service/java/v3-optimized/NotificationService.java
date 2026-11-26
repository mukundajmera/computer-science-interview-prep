import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.List;
import java.util.Collections;
import java.util.Set;

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

    public NotificationService(Dispatcher dispatcher, int capacity, int maxRetries) {
        this.dispatcher = dispatcher;
        this.capacity = capacity;
        this.intents = new ConcurrentHashMap<>();
        this.currentSize = new AtomicInteger(0);
        this.unsubscribedUsers = Collections.newSetFromMap(new ConcurrentHashMap<>());
        this.maxRetries = maxRetries;
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

        IntentState[] result = new IntentState[1];
        intents.compute(idempotencyKey, (k, v) -> {
            if (v != null) {
                result[0] = IntentState.CONFLICT;
                return v;
            }
            result[0] = IntentState.PENDING;
            return IntentState.PENDING;
        });

        if (result[0] == IntentState.CONFLICT) {
            return IntentState.CONFLICT;
        }

        synchronized (this) {
            if (currentSize.get() >= capacity) {
                intents.put(idempotencyKey, IntentState.FAILED);
                return IntentState.FAILED;
            }
            currentSize.incrementAndGet();
            dispatcher.enqueue(new Notification(recipient, idempotencyKey + "|" + message, channel, priority));
        }

        return IntentState.PENDING;
    }

    public void dispatch(String event, String recipient, String message, int priority) {
        if (unsubscribedUsers.contains(recipient)) {
            return;
        }
        List<String> prefChannels = dispatcher.getUserPreferences().getPreferredChannels(recipient, event);
        if (prefChannels != null) {
            for (String channel : prefChannels) {
                submitIntent(event, recipient, channel, message, priority);
            }
        }
    }

    public void processCallback(String idempotencyKey, boolean success) {
        intents.compute(idempotencyKey, (k, state) -> {
            if (state == IntentState.COMPLETED || state == IntentState.FAILED) {
                return state;
            }
            return success ? IntentState.COMPLETED : IntentState.FAILED;
        });
    }

    public IntentState getIntentState(String idempotencyKey) {
        return intents.get(idempotencyKey);
    }

    public void wrapChannel(String channelType, Channel originalChannel) {
        dispatcher.setChannel(channelType, new Channel() {
            @Override
            public boolean send(Notification notification) {
                String msg = notification.getMessage();
                int idx = msg.indexOf('|');
                String idempotencyKey = idx >= 0 ? msg.substring(0, idx) : msg;
                
                intents.computeIfPresent(idempotencyKey, (k, v) -> {
                    if (v == IntentState.PENDING) return IntentState.IN_PROGRESS;
                    return v;
                });
                
                boolean success = false;
                try {
                    success = originalChannel.send(notification);
                } catch (Exception e) {
                    success = false;
                }
                
                if (success) {
                    processCallback(idempotencyKey, true);
                    currentSize.decrementAndGet();
                } else {
                    if (notification.getAttempts() >= maxRetries) {
                        processCallback(idempotencyKey, false);
                        currentSize.decrementAndGet();
                    }
                }
                
                return success;
            }
        });
    }
}
