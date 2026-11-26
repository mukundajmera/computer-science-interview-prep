import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class Partition {
    private final int id;
    private final List<Message> messages;
    private final ReadWriteLock lock;

    public Partition(int id) {
        this.id = id;
        this.messages = new ArrayList<>();
        this.lock = new ReentrantReadWriteLock();
    }

    public int getId() { return id; }

    public void append(Message message) {
        lock.writeLock().lock();
        try {
            messages.add(message);
        } finally {
            lock.writeLock().unlock();
        }
    }

    public Message read(int offset) {
        lock.readLock().lock();
        try {
            if (offset >= 0 && offset < messages.size()) {
                return messages.get(offset);
            }
            return null;
        } finally {
            lock.readLock().unlock();
        }
    }

    public int size() {
        lock.readLock().lock();
        try {
            return messages.size();
        } finally {
            lock.readLock().unlock();
        }
    }
}
