package v2_extended;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class MultiPolicyCache<K, V> {
    private final int capacity;
    private EvictionPolicy currentPolicy;
    private EvictionStrategy<K, V> strategy;
    private final Map<K, CacheEntry<K, V>> map;
    private final ReentrantReadWriteLock lock;
    private final Thread cleanupThread;
    private volatile boolean running = true;

    public MultiPolicyCache(int capacity, EvictionPolicy policy) {
        this.capacity = capacity;
        this.currentPolicy = policy;
        this.map = new ConcurrentHashMap<>();
        this.lock = new ReentrantReadWriteLock();
        this.strategy = createStrategy(policy);

        this.cleanupThread = new Thread(() -> {
            while (running) {
                try {
                    Thread.sleep(1000);
                    activeExpiration();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        });
        this.cleanupThread.setDaemon(true);
        this.cleanupThread.start();
    }

    private EvictionStrategy<K, V> createStrategy(EvictionPolicy policy) {
        switch (policy) {
            case LRU: return new LruStrategy<>();
            case LFU: return new LfuStrategy<>();
            case FIFO: return new FifoStrategy<>();
            default: throw new IllegalArgumentException("Unknown policy");
        }
    }

    private void activeExpiration() {
        lock.writeLock().lock();
        try {
            List<K> toRemove = new ArrayList<>();
            for (CacheEntry<K, V> entry : map.values()) {
                if (entry.isExpired()) {
                    toRemove.add(entry.key);
                }
            }
            for (K key : toRemove) {
                CacheEntry<K, V> entry = map.remove(key);
                if (entry != null) {
                    strategy.onRemove(entry);
                }
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void shutdown() {
        running = false;
        cleanupThread.interrupt();
    }

    public void put(K key, V value) {
        put(key, value, -1);
    }

    public void put(K key, V value, long ttlMs) {
        lock.writeLock().lock();
        try {
            if (map.containsKey(key)) {
                CacheEntry<K, V> entry = map.get(key);
                entry.value = value;
                entry.expireAt = ttlMs > 0 ? System.currentTimeMillis() + ttlMs : -1;
                entry.lastAccessedAt = System.currentTimeMillis();
                entry.frequency++;
                strategy.onAccess(entry);
            } else {
                if (map.size() >= capacity) {
                    CacheEntry<K, V> evicted = strategy.evict();
                    if (evicted != null) {
                        map.remove(evicted.key);
                    }
                }
                CacheEntry<K, V> entry = new CacheEntry<>(key, value, ttlMs);
                map.put(key, entry);
                strategy.onInsert(entry);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public V get(K key) {
        lock.writeLock().lock();
        try {
            CacheEntry<K, V> entry = map.get(key);
            if (entry == null) return null;
            if (entry.isExpired()) {
                map.remove(key);
                strategy.onRemove(entry);
                return null;
            }
            entry.lastAccessedAt = System.currentTimeMillis();
            entry.frequency++;
            strategy.onAccess(entry);
            return entry.value;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void remove(K key) {
        lock.writeLock().lock();
        try {
            CacheEntry<K, V> entry = map.remove(key);
            if (entry != null) {
                strategy.onRemove(entry);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void changePolicy(EvictionPolicy newPolicy) {
        lock.writeLock().lock();
        try {
            if (currentPolicy == newPolicy) return;
            currentPolicy = newPolicy;
            EvictionStrategy<K, V> newStrategy = createStrategy(newPolicy);
            
            List<CacheEntry<K, V>> entries = new ArrayList<>(map.values());
            if (newPolicy == EvictionPolicy.LRU) {
                entries.sort((a, b) -> Long.compare(a.lastAccessedAt, b.lastAccessedAt));
            } else if (newPolicy == EvictionPolicy.FIFO) {
                entries.sort((a, b) -> Long.compare(a.createdAt, b.createdAt));
            } else if (newPolicy == EvictionPolicy.LFU) {
                entries.sort((a, b) -> Long.compare(a.lastAccessedAt, b.lastAccessedAt));
            }
            
            map.clear();
            for (CacheEntry<K, V> entry : entries) {
                if (!entry.isExpired()) {
                    newStrategy.onInsert(entry);
                    map.put(entry.key, entry);
                }
            }
            this.strategy = newStrategy;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public int size() {
        lock.readLock().lock();
        try {
            return map.size();
        } finally {
            lock.readLock().unlock();
        }
    }
}
