import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.PriorityBlockingQueue;

public class Dispatcher {
    private Map<String, Channel> channels;
    private PriorityBlockingQueue<Notification> queue;
    private RateLimiter rateLimiter;

    public Dispatcher(int rateLimit) {
        channels = new HashMap<>();
        channels.put("EMAIL", new EmailChannel());
        channels.put("SMS", new SMSChannel());
        queue = new PriorityBlockingQueue<>();
        rateLimiter = new RateLimiter(rateLimit);
    }

    public void enqueue(Notification notification) {
        queue.offer(notification);
    }

    public boolean processOne() {
        Notification notification = queue.poll();
        if (notification != null) {
            if (rateLimiter.acquire(notification.getChannelType())) {
                Channel channel = channels.get(notification.getChannelType());
                if (channel != null) {
                    return channel.send(notification);
                }
            } else {
                queue.offer(notification);
            }
        }
        return false;
    }
    
    public Notification peekQueue() {
        return queue.peek();
    }
    
    public void setChannel(String type, Channel channel) {
        channels.put(type, channel);
    }
    
    public Channel getChannel(String type) {
        return channels.get(type);
    }
}
