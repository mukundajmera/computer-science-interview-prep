package v3_optimized;

import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.Random;

public class MultiPolicyCache<K, V> {
    
    public static class CacheStats {
        public long hits = 0;
        public long misses = 0;
        public long evictions = 0;
    }

    private static class CacheSegment<K, V> {
        private final int capacity;
        private EvictionPolicy currentPolicy;
        private EvictionStrategy<K, V> strategy;
        private final Map<K, CacheEntry<K, V>> map;
        private final ReentrantReadWriteLock lock;
        private final CacheStats stats;
        private final List<CacheEntry<K, V>> pool;

        public CacheSegment(int capacity, EvictionPolicy policy) {
            this.capacity = capacity;
            this.currentPolicy = policy;
            this.map = new ConcurrentHashMap<>();
            this.lock = new ReentrantReadWriteLock();
            this.stats = new CacheStats();
            this.pool = new ArrayList<>(capacity);
            for(int i = 0; i < capacity; i++) {
                this.pool.add(new CacheEntry<>(null, null, -1));
            }
            this.strategy = createStrategy(policy);
        }

        private EvictionStrategy<K, V> createStrategy(EvictionPolicy policy) {
            switch (policy) {
                case LRU: return new LruStrategy<>();
                case LFU: return new LfuStrategy<>();
                case FIFO: return new FifoStrategy<>();
                default: throw new IllegalArgumentException("Unknown policy");
            }
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
                    CacheEntry<K, V> entry = null;
                    if (map.size() >= capacity && capacity > 0) {
                        CacheEntry<K, V> evicted = strategy.evict();
                        if (evicted != null) {
                            map.remove(evicted.key);
                            stats.evictions++;
                            entry = evicted;
                        }
                    }
                    if (entry == null && !pool.isEmpty()) {
                        entry = pool.remove(pool.size() - 1);
                    } else if (entry == null) {
                        entry = new CacheEntry<>(null, null, -1);
                    }
                    entry.key = key;
                    entry.value = value;
                    entry.expireAt = ttlMs > 0 ? System.currentTimeMillis() + ttlMs : -1;
                    entry.frequency = 1;
                    entry.createdAt = System.currentTimeMillis();
                    entry.lastAccessedAt = entry.createdAt;
                    entry.prev = null;
                    entry.next = null;
                    entry.freqNode = null;
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
                if (entry == null) {
                    stats.misses++;
                    return null;
                }
                if (entry.isExpired()) {
                    map.remove(key);
                    strategy.onRemove(entry);
                    pool.add(entry);
                    stats.misses++;
                    return null;
                }
                entry.lastAccessedAt = System.currentTimeMillis();
                entry.frequency++;
                strategy.onAccess(entry);
                stats.hits++;
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
                    pool.add(entry);
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

        public void activeExpiration() {
            lock.writeLock().lock();
            try {
                if (map.isEmpty()) return;
                int size = map.size();
                int sampleSize = Math.min(20, size);
                Random rand = new Random();
                int startIdx = size > sampleSize ? rand.nextInt(size) : 0;
                long now = System.currentTimeMillis();
                
                List<K> toRemove = new ArrayList<>();
                int idx = 0;
                int count = 0;
                for (Map.Entry<K, CacheEntry<K, V>> entry : map.entrySet()) {
                    if (idx >= startIdx) {
                        if (entry.getValue().expireAt > 0 && now > entry.getValue().expireAt) {
                            toRemove.add(entry.getKey());
                        }
                        count++;
                        if (count >= sampleSize) break;
                    }
                    idx++;
                }
                
                for (K key : toRemove) {
                    CacheEntry<K, V> entry = map.remove(key);
                    if (entry != null) {
                        strategy.onRemove(entry);
                        pool.add(entry);
                    }
                }
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

    private final int capacity;
    private final int numSegments;
    private final CacheSegment<K, V>[] segments;
    private final Thread cleanupThread;
    private volatile boolean running = true;

    @SuppressWarnings("unchecked")
    public MultiPolicyCache(int capacity, EvictionPolicy policy, int numSegments) {
        this.capacity = capacity;
        this.numSegments = numSegments;
        this.segments = new CacheSegment[numSegments];
        int segmentCapacity = Math.max(1, capacity / numSegments);
        
        for (int i = 0; i < numSegments; i++) {
            this.segments[i] = new CacheSegment<>(segmentCapacity, policy);
        }

        this.cleanupThread = new Thread(() -> {
            while (running) {
                try {
                    Thread.sleep(1000);
                    for (CacheSegment<K, V> segment : segments) {
                        if (!running) break;
                        segment.activeExpiration();
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        });
        this.cleanupThread.setDaemon(true);
        this.cleanupThread.start();
    }
    
    public MultiPolicyCache(int capacity, EvictionPolicy policy) {
        this(capacity, policy, 16);
    }

    private CacheSegment<K, V> getSegment(K key) {
        int hash = key == null ? 0 : key.hashCode();
        return segments[Math.abs(hash % numSegments)];
    }

    public void shutdown() {
        running = false;
        cleanupThread.interrupt();
    }

    public void put(K key, V value) {
        put(key, value, -1);
    }

    public void put(K key, V value, long ttlMs) {
        getSegment(key).put(key, value, ttlMs);
    }

    public V get(K key) {
        return getSegment(key).get(key);
    }

    public void remove(K key) {
        getSegment(key).remove(key);
    }

    public void changePolicy(EvictionPolicy newPolicy) {
        for (CacheSegment<K, V> segment : segments) {
            segment.changePolicy(newPolicy);
        }
    }

    public int size() {
        int total = 0;
        for (CacheSegment<K, V> segment : segments) {
            total += segment.size();
        }
        return total;
    }

    public CacheStats getStats() {
        CacheStats totalStats = new CacheStats();
        for (CacheSegment<K, V> segment : segments) {
            segment.lock.readLock().lock();
            try {
                totalStats.hits += segment.stats.hits;
                totalStats.misses += segment.stats.misses;
                totalStats.evictions += segment.stats.evictions;
            } finally {
                segment.lock.readLock().unlock();
            }
        }
        return totalStats;
    }
}
