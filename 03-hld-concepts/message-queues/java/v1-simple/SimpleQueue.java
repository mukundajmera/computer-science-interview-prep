import java.util.LinkedList;
import java.util.Queue;

/**
 * A bounded blocking queue implementation using wait() and notifyAll().
 * This provides back-pressure by blocking publishers when the queue is full.
 */
public class SimpleQueue<T> {
    private final Queue<T> queue;
    private final int maxSize;

    public SimpleQueue(int maxSize) {
        this.queue = new LinkedList<>();
        this.maxSize = maxSize;
    }

    public synchronized boolean enqueue(T message, long timeoutMillis) throws InterruptedException {
        long endTime = System.currentTimeMillis() + timeoutMillis;
        while (queue.size() >= maxSize) {
            long remaining = endTime - System.currentTimeMillis();
            if (remaining <= 0) {
                return false;
            }
            wait(remaining);
        }
        queue.offer(message);
        notifyAll();
        return true;
    }

    public synchronized boolean enqueue(T message) throws InterruptedException {
        while (queue.size() >= maxSize) {
            wait();
        }
        queue.offer(message);
        notifyAll();
        return true;
    }

    public synchronized T dequeue(long timeoutMillis) throws InterruptedException {
        long endTime = System.currentTimeMillis() + timeoutMillis;
        while (queue.isEmpty()) {
            long remaining = endTime - System.currentTimeMillis();
            if (remaining <= 0) {
                return null;
            }
            wait(remaining);
        }
        T message = queue.poll();
        notifyAll();
        return message;
    }

    public synchronized T dequeue() throws InterruptedException {
        while (queue.isEmpty()) {
            wait();
        }
        T message = queue.poll();
        notifyAll();
        return message;
    }

    public synchronized int size() {
        return queue.size();
    }

    public synchronized boolean isEmpty() {
        return queue.isEmpty();
    }

    public synchronized boolean isFull() {
        return queue.size() >= maxSize;
    }

    public synchronized void clear() {
        queue.clear();
        notifyAll();
    }
}
