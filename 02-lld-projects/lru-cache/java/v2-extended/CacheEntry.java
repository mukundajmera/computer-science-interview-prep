package v2_extended;

/**
 * LRU Cache - V2 Extended
 * 
 * Cache entry with TTL (Time-To-Live) support.
 */
public class CacheEntry<K, V> {
    private final K key;
    private V value;
    private final long createdAt;
    private long expiresAt;
    private int accessCount;
    
    CacheEntry<K, V> prev;
    CacheEntry<K, V> next;

    public CacheEntry(K key, V value) {
        this(key, value, -1);  // No expiration
    }

    public CacheEntry(K key, V value, long ttlMs) {
        this.key = key;
        this.value = value;
        this.createdAt = System.currentTimeMillis();
        this.expiresAt = ttlMs > 0 ? createdAt + ttlMs : -1;
        this.accessCount = 0;
    }

    public K getKey() {
        return key;
    }

    public V getValue() {
        return value;
    }

    public void setValue(V value) {
        this.value = value;
    }

    public long getCreatedAt() {
        return createdAt;
    }

    public long getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(long expiresAt) {
        this.expiresAt = expiresAt;
    }

    public int getAccessCount() {
        return accessCount;
    }

    /**
     * Mark entry as accessed (for statistics).
     */
    public void touch() {
        accessCount++;
    }

    /**
     * Check if entry has expired.
     */
    public boolean isExpired() {
        return expiresAt > 0 && System.currentTimeMillis() > expiresAt;
    }

    /**
     * Get remaining time-to-live in milliseconds.
     */
    public long getRemainingTtlMs() {
        if (expiresAt <= 0) {
            return -1;  // No expiration
        }
        long remaining = expiresAt - System.currentTimeMillis();
        return Math.max(0, remaining);
    }

    @Override
    public String toString() {
        return String.format("(%s=%s)", key, value);
    }
}

/**
 * Doubly linked list for maintaining access order.
 */
class DoublyLinkedList<K, V> {
    private final CacheEntry<K, V> head;
    private final CacheEntry<K, V> tail;
    private int size;

    public DoublyLinkedList() {
        head = new CacheEntry<>(null, null);
        tail = new CacheEntry<>(null, null);
        head.next = tail;
        tail.prev = head;
        size = 0;
    }

    public void addToFront(CacheEntry<K, V> entry) {
        entry.prev = head;
        entry.next = head.next;
        head.next.prev = entry;
        head.next = entry;
        size++;
    }

    public void remove(CacheEntry<K, V> entry) {
        entry.prev.next = entry.next;
        entry.next.prev = entry.prev;
        size--;
    }

    public void moveToFront(CacheEntry<K, V> entry) {
        remove(entry);
        addToFront(entry);
    }

    public CacheEntry<K, V> removeLast() {
        if (isEmpty()) {
            return null;
        }
        CacheEntry<K, V> last = tail.prev;
        remove(last);
        return last;
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public int size() {
        return size;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("[");
        CacheEntry<K, V> current = head.next;
        while (current != tail) {
            sb.append(current);
            if (current.next != tail) {
                sb.append(" -> ");
            }
            current = current.next;
        }
        sb.append("]");
        return sb.toString();
    }
}
