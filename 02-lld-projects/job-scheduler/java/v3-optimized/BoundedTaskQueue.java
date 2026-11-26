import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Bounded producer-consumer queue used by scheduler workers.
 */
public class BoundedTaskQueue<T> {
    private final int capacity;
    private final Deque<T> items;
    private final ReentrantLock lock;
    private final Condition notEmpty;
    private final Condition notFull;

    public BoundedTaskQueue(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("capacity must be > 0");
        }
        this.capacity = capacity;
        this.items = new ArrayDeque<T>(capacity);
        this.lock = new ReentrantLock();
        this.notEmpty = lock.newCondition();
        this.notFull = lock.newCondition();
    }

    public boolean offer(T task, long timeoutMs) throws InterruptedException {
        long nanos = TimeUnit.MILLISECONDS.toNanos(Math.max(timeoutMs, 0L));
        lock.lockInterruptibly();
        try {
            while (items.size() >= capacity) {
                if (nanos <= 0L) {
                    return false;
                }
                nanos = notFull.awaitNanos(nanos);
            }
            items.addLast(task);
            notEmpty.signal();
            return true;
        } finally {
            lock.unlock();
        }
    }

    public Optional<T> poll(long timeoutMs) throws InterruptedException {
        long nanos = TimeUnit.MILLISECONDS.toNanos(Math.max(timeoutMs, 0L));
        lock.lockInterruptibly();
        try {
            while (items.isEmpty()) {
                if (nanos <= 0L) {
                    return Optional.empty();
                }
                nanos = notEmpty.awaitNanos(nanos);
            }
            T task = items.removeFirst();
            notFull.signal();
            return Optional.of(task);
        } finally {
            lock.unlock();
        }
    }

    public int size() {
        lock.lock();
        try {
            return items.size();
        } finally {
            lock.unlock();
        }
    }

    public int capacity() {
        return capacity;
    }
}
