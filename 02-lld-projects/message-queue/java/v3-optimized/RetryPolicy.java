
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public class RetryPolicy {
    private final int maxRetries;
    private final long initialBackoffMillis;
    private final long maxBackoffMillis;
    private final double multiplier;
    private final List<Message> deadLetterQueue;

    public RetryPolicy(int maxRetries, long initialBackoffMillis, long maxBackoffMillis, double multiplier) {
        this.maxRetries = maxRetries;
        this.initialBackoffMillis = initialBackoffMillis;
        this.maxBackoffMillis = maxBackoffMillis;
        this.multiplier = multiplier;
        this.deadLetterQueue = new CopyOnWriteArrayList<>();
    }

    public boolean execute(Runnable action, Message message) {
        int attempts = 0;
        while (attempts <= maxRetries) {
            try {
                action.run();
                return true;
            } catch (Exception e) {
                attempts++;
                if (attempts <= maxRetries) {
                    try {
                        long backoff = (long) Math.min(initialBackoffMillis * Math.pow(multiplier, attempts - 1), maxBackoffMillis);
                        Thread.sleep(backoff);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
        }
        deadLetterQueue.add(message);
        return false;
    }
    
    public List<Message> getDeadLetterQueue() {
        return new ArrayList<>(deadLetterQueue);
    }
}
