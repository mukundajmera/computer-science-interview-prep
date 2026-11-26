import java.util.*;
import java.util.concurrent.PriorityBlockingQueue;

class DelayedNotification implements Comparable<DelayedNotification> {
    public long retryTime;
    public Notification notification;
    
    public DelayedNotification(long retryTime, Notification notification) {
        this.retryTime = retryTime;
        this.notification = notification;
    }
    
    @Override
    public int compareTo(DelayedNotification other) {
        return Long.compare(this.retryTime, other.retryTime);
    }
}

public class Dispatcher {
    private Map<String, Channel> channels;
    private PriorityBlockingQueue<Notification> queue;
    private PriorityBlockingQueue<DelayedNotification> retryQueue;
    private RateLimiter rateLimiter;
    private UserPreferenceMatrix userPreferences;
    private int maxRetries;

    public Dispatcher(int rateLimit, int maxRetries) {
        channels = new HashMap<>();
        channels.put("EMAIL", new EmailChannel());
        channels.put("SMS", new SMSChannel());
        channels.put("PUSH", new PushChannel());
        channels.put("SLACK", new SlackChannel());
        
        queue = new PriorityBlockingQueue<>();
        retryQueue = new PriorityBlockingQueue<>();
        rateLimiter = new RateLimiter(rateLimit);
        userPreferences = new UserPreferenceMatrix();
        this.maxRetries = maxRetries;
    }
    
    public UserPreferenceMatrix getUserPreferences() {
        return userPreferences;
    }

    public boolean dispatchBasedOnPreference(String userId, String message, String notificationType, int priority) {
        List<String> prefChannels = userPreferences.getPreferredChannels(userId, notificationType);
        boolean enqueued = false;
        for (String channel : prefChannels) {
            queue.offer(new Notification(userId, message, channel, priority));
            enqueued = true;
        }
        return enqueued;
    }

    public void enqueue(Notification notification) {
        queue.offer(notification);
    }
    
    public void setChannel(String name, Channel channel) {
        channels.put(name, channel);
    }
    
    private void handleRetry(Notification notification) {
        notification.incrementAttempts();
        if (notification.getAttempts() <= maxRetries) {
            // Exponential backoff: base (1s) * 2^attempts (in milliseconds for simplicity here)
            long delayMs = (long)(1000 * Math.pow(2, notification.getAttempts()));
            notification.setNextRetryTime(System.currentTimeMillis() + delayMs);
            retryQueue.offer(new DelayedNotification(notification.getNextRetryTime(), notification));
        }
    }

    public boolean processOne() {
        long now = System.currentTimeMillis();
        
        synchronized(this) {
            while (!retryQueue.isEmpty()) {
                DelayedNotification dn = retryQueue.peek();
                if (dn != null && dn.retryTime <= now) {
                    retryQueue.poll();
                    queue.offer(dn.notification);
                } else {
                    break;
                }
            }
        }
        
        Notification notification = queue.poll();
        if (notification != null) {
            if (rateLimiter.acquire(notification.getChannelType())) {
                Channel channel = channels.get(notification.getChannelType());
                if (channel != null) {
                    boolean success = channel.send(notification);
                    if (!success) {
                        handleRetry(notification);
                    }
                    return success;
                }
            } else {
                handleRetry(notification);
            }
        }
        return false;
    }
    
    public boolean isQueueEmpty() {
        return queue.isEmpty();
    }
    
    public Notification peekQueue() {
        return queue.peek();
    }
    
    public Notification pollQueue() {
        return queue.poll();
    }
}
