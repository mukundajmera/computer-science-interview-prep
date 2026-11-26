package v3_production;
import java.util.concurrent.*;
import java.util.concurrent.locks.*;
import java.util.function.Function;

/**
 * V3: Production-Ready Write-Through Cache
 * 
 * A thread-safe cache implementation with production-level features:
 * - Write-through to backing store
 * - Cache-aside read pattern
 * - Lock striping for better concurrency
 * - Cache stampede prevention
 * - Comprehensive statistics
 * - Async refresh support
 * 
 * This demonstrates patterns used in production systems like
 * Guava Cache, Caffeine, and distributed cache clients.
 */
public class WriteThruCache<K, V> {
    
    private final ConcurrentHashMap<K, CacheEntry<V>> cache;
    private final int capacity;
    private final long defaultTtlMillis;
    private final DataSource<K, V> dataSource;
    private final ScheduledExecutorService scheduler;
    
    // Lock striping for cache stampede prevention
    private final int numStripes = 16;
    private final ReentrantLock[] locks;
    
    // Statistics
    private final CacheStats stats = new CacheStats();
    
    /**
     * Interface for the backing data store.
     */
    public interface DataSource<K, V> {
        V get(K key);
        void put(K key, V value);
        void delete(K key);
    }
    
    /**
     * Cache entry with metadata.
     */
    private static class CacheEntry<V> {
        volatile V value;
        volatile long expirationTime;
        volatile long lastAccessTime;
        volatile boolean refreshing;
        
        CacheEntry(V value, long ttlMillis) {
            this.value = value;
            this.expirationTime = System.currentTimeMillis() + ttlMillis;
            this.lastAccessTime = System.currentTimeMillis();
            this.refreshing = false;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }
        
        void touch() {
            lastAccessTime = System.currentTimeMillis();
        }
        
        void refresh(V newValue, long ttlMillis) {
            this.value = newValue;
            this.expirationTime = System.currentTimeMillis() + ttlMillis;
            this.refreshing = false;
        }
    }
    
    /**
     * Statistics tracking.
     */
    public static class CacheStats {
        private final java.util.concurrent.atomic.LongAdder hits = new java.util.concurrent.atomic.LongAdder();
        private final java.util.concurrent.atomic.LongAdder misses = new java.util.concurrent.atomic.LongAdder();
        private final java.util.concurrent.atomic.LongAdder loads = new java.util.concurrent.atomic.LongAdder();
        private final java.util.concurrent.atomic.LongAdder evictions = new java.util.concurrent.atomic.LongAdder();
        private final java.util.concurrent.atomic.LongAdder writeThrus = new java.util.concurrent.atomic.LongAdder();
        
        void recordHit() { hits.increment(); }
        void recordMiss() { misses.increment(); }
        void recordLoad() { loads.increment(); }
        void recordEviction() { evictions.increment(); }
        void recordWriteThru() { writeThrus.increment(); }
        
        public long hits() { return hits.sum(); }
        public long misses() { return misses.sum(); }
        public long loads() { return loads.sum(); }
        public long evictions() { return evictions.sum(); }
        public long writeThrus() { return writeThrus.sum(); }
        
        public double hitRate() {
            long total = hits() + misses();
            return total == 0 ? 0.0 : (hits() * 100.0) / total;
        }
        
        @Override
        public String toString() {
            return String.format(
                "CacheStats{hits=%d, misses=%d, hitRate=%.2f%%, " +
                "loads=%d, evictions=%d, writeThrus=%d}",
                hits(), misses(), hitRate(), loads(), evictions(), writeThrus()
            );
        }
    }
    
    /**
     * Creates a write-through cache.
     * 
     * @param capacity Maximum number of entries
     * @param defaultTtlSeconds Default TTL in seconds
     * @param dataSource Backing data store
     */
    public WriteThruCache(int capacity, int defaultTtlSeconds, DataSource<K, V> dataSource) {
        this.capacity = capacity;
        this.defaultTtlMillis = defaultTtlSeconds * 1000L;
        this.dataSource = dataSource;
        this.cache = new ConcurrentHashMap<>(capacity);
        this.scheduler = Executors.newScheduledThreadPool(2, r -> {
            Thread t = new Thread(r, "cache-maintenance");
            t.setDaemon(true);
            return t;
        });
        
        // Initialize lock stripes
        this.locks = new ReentrantLock[numStripes];
        for (int i = 0; i < numStripes; i++) {
            locks[i] = new ReentrantLock();
        }
        
        // Schedule periodic cleanup
        scheduler.scheduleAtFixedRate(this::cleanup, 60, 60, TimeUnit.SECONDS);
    }
    
    /**
     * Gets stripe lock for a key to prevent cache stampede.
     */
    private ReentrantLock getLock(K key) {
        int hash = key.hashCode();
        int stripe = (hash & 0x7FFFFFFF) % numStripes;
        return locks[stripe];
    }
    
    /**
     * Gets a value, loading from data source on miss.
     */
    public V get(K key) {
        CacheEntry<V> entry = cache.get(key);
        
        if (entry != null && !entry.isExpired()) {
            entry.touch();
            stats.recordHit();
            return entry.value;
        }
        
        // Cache miss or expired - need to load
        return loadValue(key);
    }
    
    /**
     * Loads value with cache stampede prevention.
     * Only one thread loads; others wait.
     */
    private V loadValue(K key) {
        ReentrantLock lock = getLock(key);
        lock.lock();
        try {
            // Double-check after acquiring lock
            CacheEntry<V> entry = cache.get(key);
            if (entry != null && !entry.isExpired()) {
                stats.recordHit();
                return entry.value;
            }
            
            // Load from data source
            stats.recordMiss();
            V value = dataSource.get(key);
            
            if (value != null) {
                stats.recordLoad();
                putInternal(key, value, defaultTtlMillis, false);
            }
            
            return value;
        } finally {
            lock.unlock();
        }
    }
    
    /**
     * Puts a value with write-through to data source.
     */
    public void put(K key, V value) {
        put(key, value, defaultTtlMillis);
    }
    
    /**
     * Puts a value with custom TTL and write-through.
     */
    public void put(K key, V value, long ttlMillis) {
        putInternal(key, value, ttlMillis, true);
    }
    
    private void putInternal(K key, V value, long ttlMillis, boolean writeThrough) {
        // Enforce capacity
        if (cache.size() >= capacity) {
            evictLRU();
        }
        
        // Write to cache
        cache.put(key, new CacheEntry<>(value, ttlMillis));
        
        // Write-through to data source
        if (writeThrough && dataSource != null) {
            try {
                dataSource.put(key, value);
                stats.recordWriteThru();
            } catch (Exception e) {
                // Log error but don't fail - cache is source of truth temporarily
                System.err.println("Write-through failed for key: " + key);
            }
        }
    }
    
    /**
     * Removes entry from cache and data source.
     */
    public void remove(K key) {
        cache.remove(key);
        if (dataSource != null) {
            try {
                dataSource.delete(key);
            } catch (Exception e) {
                System.err.println("Delete failed for key: " + key);
            }
        }
    }
    
    /**
     * Invalidates cache entry without touching data source.
     */
    public void invalidate(K key) {
        cache.remove(key);
    }
    
    /**
     * Refreshes a key asynchronously before it expires.
     */
    public void scheduleRefresh(K key, long refreshBeforeExpiryMillis) {
        CacheEntry<V> entry = cache.get(key);
        if (entry == null) return;
        
        long refreshTime = entry.expirationTime - refreshBeforeExpiryMillis;
        long delay = Math.max(0, refreshTime - System.currentTimeMillis());
        
        scheduler.schedule(() -> refreshKey(key), delay, TimeUnit.MILLISECONDS);
    }
    
    private void refreshKey(K key) {
        CacheEntry<V> entry = cache.get(key);
        if (entry == null || entry.refreshing) return;
        
        entry.refreshing = true;
        try {
            V newValue = dataSource.get(key);
            if (newValue != null) {
                entry.refresh(newValue, defaultTtlMillis);
            }
        } catch (Exception e) {
            entry.refreshing = false;
        }
    }
    
    /**
     * Simple LRU eviction - removes oldest accessed entry.
     */
    private void evictLRU() {
        K oldestKey = null;
        long oldestTime = Long.MAX_VALUE;
        
        for (var entry : cache.entrySet()) {
            if (entry.getValue().lastAccessTime < oldestTime) {
                oldestTime = entry.getValue().lastAccessTime;
                oldestKey = entry.getKey();
            }
        }
        
        if (oldestKey != null) {
            cache.remove(oldestKey);
            stats.recordEviction();
        }
    }
    
    /**
     * Removes expired entries.
     */
    public void cleanup() {
        cache.entrySet().removeIf(e -> e.getValue().isExpired());
    }
    
    /**
     * Warms cache with specified keys.
     */
    public void warmUp(Iterable<K> keys) {
        for (K key : keys) {
            get(key);  // Loads from data source if not cached
        }
    }
    
    public int size() {
        return cache.size();
    }
    
    public CacheStats stats() {
        return stats;
    }
    
    public void shutdown() {
        scheduler.shutdown();
    }
}
