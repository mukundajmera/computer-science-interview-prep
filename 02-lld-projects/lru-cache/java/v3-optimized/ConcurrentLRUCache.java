package v3_optimized;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.locks.ReentrantLock;

/**
 * LRU Cache - V3 Optimized
 * 
 * Thread-safe LRU cache using Segmented Lock Striping.
 * High concurrency is achieved by sharding the cache into independent segments,
 * reducing lock contention across multiple threads.
 */
public class ConcurrentLRUCache<K, V> {
    private final int capacity;
    private final int numSegments;
    private final Segment<K, V>[] segments;

    @SuppressWarnings("unchecked")
    public ConcurrentLRUCache(int capacity, int numSegments) {
        if (capacity < 1) {
            throw new IllegalArgumentException("Capacity must be at least 1");
        }
        if (numSegments < 1) {
            throw new IllegalArgumentException("Number of segments must be at least 1");
        }
        this.capacity = capacity;
        this.numSegments = numSegments;

        int segmentCapacity = (capacity + numSegments - 1) / numSegments;
        this.segments = new Segment[numSegments];
        for (int i = 0; i < numSegments; i++) {
            this.segments[i] = new Segment<>(segmentCapacity);
        }
    }

    public ConcurrentLRUCache(int capacity) {
        this(capacity, 16); // Default 16 segments
    }

    private Segment<K, V> getSegment(K key) {
        int hash = key.hashCode();
        // Handle Integer.MIN_VALUE since Math.abs(Integer.MIN_VALUE) == Integer.MIN_VALUE
        if (hash == Integer.MIN_VALUE) {
            hash = 0;
        }
        int index = Math.abs(hash) % numSegments;
        return segments[index];
    }

    /**
     * Get value by key. Thread-safe.
     */
    public V get(K key) {
        if (key == null) {
            throw new IllegalArgumentException("Key cannot be null");
        }
        return getSegment(key).get(key);
    }

    /**
     * Insert or update a key-value pair. Thread-safe.
     */
    public void put(K key, V value) {
        if (key == null) {
            throw new IllegalArgumentException("Key cannot be null");
        }
        getSegment(key).put(key, value);
    }

    /**
     * Remove an entry by key. Thread-safe.
     */
    public V remove(K key) {
        if (key == null) {
            throw new IllegalArgumentException("Key cannot be null");
        }
        return getSegment(key).remove(key);
    }

    /**
     * Check if key exists. Thread-safe.
     */
    public boolean containsKey(K key) {
        if (key == null) {
            throw new IllegalArgumentException("Key cannot be null");
        }
        return getSegment(key).containsKey(key);
    }

    /**
     * Get current size. Thread-safe.
     */
    public int size() {
        int totalSize = 0;
        for (Segment<K, V> segment : segments) {
            totalSize += segment.size();
        }
        return totalSize;
    }

    /**
     * Get maximum capacity.
     */
    public int getCapacity() {
        return capacity;
    }

    /**
     * Remove all entries. Thread-safe.
     */
    public void clear() {
        for (Segment<K, V> segment : segments) {
            segment.clear();
        }
    }

    // Statistics methods (aggregated from segments)
    
    public long getHits() {
        long totalHits = 0;
        for (Segment<K, V> segment : segments) {
            totalHits += segment.getHits();
        }
        return totalHits;
    }

    public long getMisses() {
        long totalMisses = 0;
        for (Segment<K, V> segment : segments) {
            totalMisses += segment.getMisses();
        }
        return totalMisses;
    }

    public long getEvictions() {
        long totalEvictions = 0;
        for (Segment<K, V> segment : segments) {
            totalEvictions += segment.getEvictions();
        }
        return totalEvictions;
    }

    public double getHitRatio() {
        long h = getHits();
        long m = getMisses();
        long total = h + m;
        return total > 0 ? (double) h / total : 0.0;
    }

    public void resetStatistics() {
        for (Segment<K, V> segment : segments) {
            segment.resetStatistics();
        }
    }

    @Override
    public String toString() {
        return String.format("ConcurrentLRUCache{capacity=%d, size=%d, hits=%d, misses=%d, hitRatio=%.2f%%}",
                capacity, size(), getHits(), getMisses(), getHitRatio() * 100);
    }

    /**
     * Inner Segment class acting as an individual LRU cache.
     */
    private static class Segment<K, V> {
        private final int capacity;
        private final Map<K, CacheNodeV3<K, V>> cache;
        private final DoublyLinkedListV3<K, V> list;
        private final ReentrantLock lock;

        private long hits;
        private long misses;
        private long evictions;

        public Segment(int capacity) {
            this.capacity = capacity;
            this.cache = new HashMap<>();
            this.list = new DoublyLinkedListV3<>();
            this.lock = new ReentrantLock();
            this.hits = 0;
            this.misses = 0;
            this.evictions = 0;
        }

        public V get(K key) {
            lock.lock();
            try {
                CacheNodeV3<K, V> node = cache.get(key);
                if (node == null) {
                    misses++;
                    return null;
                }
                list.moveToFront(node);
                hits++;
                return node.getValue();
            } finally {
                lock.unlock();
            }
        }

        public void put(K key, V value) {
            lock.lock();
            try {
                CacheNodeV3<K, V> existingNode = cache.get(key);

                if (existingNode != null) {
                    existingNode.setValue(value);
                    list.moveToFront(existingNode);
                } else {
                    if (cache.size() >= capacity) {
                        CacheNodeV3<K, V> lru = list.removeLast();
                        if (lru != null) {
                            cache.remove(lru.getKey());
                            evictions++;
                        }
                    }

                    CacheNodeV3<K, V> newNode = new CacheNodeV3<>(key, value);
                    cache.put(key, newNode);
                    list.addToFront(newNode);
                }
            } finally {
                lock.unlock();
            }
        }

        public V remove(K key) {
            lock.lock();
            try {
                CacheNodeV3<K, V> node = cache.remove(key);
                if (node == null) {
                    return null;
                }
                list.remove(node);
                return node.getValue();
            } finally {
                lock.unlock();
            }
        }

        public boolean containsKey(K key) {
            lock.lock();
            try {
                return cache.containsKey(key);
            } finally {
                lock.unlock();
            }
        }

        public int size() {
            lock.lock();
            try {
                return cache.size();
            } finally {
                lock.unlock();
            }
        }

        public void clear() {
            lock.lock();
            try {
                cache.clear();
                while (!list.isEmpty()) {
                    list.removeLast();
                }
            } finally {
                lock.unlock();
            }
        }

        public long getHits() {
            lock.lock();
            try {
                return hits;
            } finally {
                lock.unlock();
            }
        }

        public long getMisses() {
            lock.lock();
            try {
                return misses;
            } finally {
                lock.unlock();
            }
        }

        public long getEvictions() {
            lock.lock();
            try {
                return evictions;
            } finally {
                lock.unlock();
            }
        }

        public void resetStatistics() {
            lock.lock();
            try {
                hits = 0;
                misses = 0;
                evictions = 0;
            } finally {
                lock.unlock();
            }
        }
    }
}

/**
 * Cache node for doubly linked list.
 */
class CacheNodeV3<K, V> {
    private final K key;
    private volatile V value;  // volatile for visibility across threads
    CacheNodeV3<K, V> prev;
    CacheNodeV3<K, V> next;

    public CacheNodeV3(K key, V value) {
        this.key = key;
        this.value = value;
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

    @Override
    public String toString() {
        return String.format("(%s=%s)", key, value);
    }
}

/**
 * Doubly linked list for maintaining access order.
 */
class DoublyLinkedListV3<K, V> {
    private final CacheNodeV3<K, V> head;
    private final CacheNodeV3<K, V> tail;
    private int size;

    public DoublyLinkedListV3() {
        head = new CacheNodeV3<>(null, null);
        tail = new CacheNodeV3<>(null, null);
        head.next = tail;
        tail.prev = head;
        size = 0;
    }

    public void addToFront(CacheNodeV3<K, V> node) {
        node.prev = head;
        node.next = head.next;
        head.next.prev = node;
        head.next = node;
        size++;
    }

    public void remove(CacheNodeV3<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
        size--;
    }

    public void moveToFront(CacheNodeV3<K, V> node) {
        remove(node);
        addToFront(node);
    }

    public CacheNodeV3<K, V> removeLast() {
        if (isEmpty()) {
            return null;
        }
        CacheNodeV3<K, V> last = tail.prev;
        if (last != head) {
            remove(last);
            return last;
        }
        return null;
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public int size() {
        return size;
    }
}
