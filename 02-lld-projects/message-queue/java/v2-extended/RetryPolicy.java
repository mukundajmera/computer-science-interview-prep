
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

public class RetryPolicy {
    private final int maxRetries;
    private final long backoffMillis;
    private final Queue<Message> deadLetterQueue;

    public RetryPolicy(int maxRetries, long backoffMillis) {
        this.maxRetries = maxRetries;
        this.backoffMillis = backoffMillis;
        this.deadLetterQueue = new ConcurrentLinkedQueue<>();
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
                        Thread.sleep(backoffMillis);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
        }
        deadLetterQueue.offer(message);
        return false;
    }

    public Queue<Message> getDeadLetterQueue() {
        return deadLetterQueue;
    }
}
