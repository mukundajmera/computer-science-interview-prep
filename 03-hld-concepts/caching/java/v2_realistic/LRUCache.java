package v2_realistic;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * V2: LRU Cache Implementation
 * 
 * A Least Recently Used (LRU) cache with size limit.
 * When the cache reaches capacity, the least recently
 * accessed entry is automatically evicted.
 * 
 * This implementation uses LinkedHashMap with access-order
 * to efficiently track usage and implement LRU eviction.
 * 
 * Features:
 * - Fixed size capacity
 * - LRU eviction policy
 * - O(1) get and put operations
 * - TTL support per entry
 * 
 * Use Case:
 * - Limited memory environments
 * - When you want to keep "hot" data in cache
 * - Session caching, API response caching
 */
public class LRUCache<K, V> {
    
    private final int capacity;
    private final long defaultTtlMillis;
    private final Map<K, CacheEntry<V>> cache;
    
    // Statistics
    private long hits = 0;
    private long misses = 0;
    private long evictions = 0;
    
    /**
     * Wrapper for cached values with TTL support.
     */
    private static class CacheEntry<V> {
        final V value;
        final long expirationTime;
        
        CacheEntry(V value, long expirationTime) {
            this.value = value;
            this.expirationTime = expirationTime;
        }
        
        boolean isExpired() {
            return expirationTime > 0 && System.currentTimeMillis() > expirationTime;
        }
    }
    
    /**
     * Creates an LRU cache with specified capacity and TTL.
     * 
     * @param capacity Maximum number of entries
     * @param defaultTtlSeconds Default TTL in seconds (0 for no expiration)
     */
    public LRUCache(int capacity, int defaultTtlSeconds) {
        this.capacity = capacity;
        this.defaultTtlMillis = defaultTtlSeconds * 1000L;
        
        // LinkedHashMap with accessOrder=true for LRU behavior
        // The eldest entry (least recently used) is removed when capacity exceeded
        this.cache = new LinkedHashMap<K, CacheEntry<V>>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, CacheEntry<V>> eldest) {
                boolean shouldRemove = size() > LRUCache.this.capacity;
                if (shouldRemove) {
                    evictions++;
                }
                return shouldRemove;
            }
        };
    }
    
    /**
     * Stores a value with default TTL.
     */
    public synchronized void put(K key, V value) {
        put(key, value, defaultTtlMillis);
    }
    
    /**
     * Stores a value with custom TTL.
     * 
     * @param key   Cache key
     * @param value Value to cache
     * @param ttlMillis TTL in milliseconds (0 for no expiration)
     */
    public synchronized void put(K key, V value, long ttlMillis) {
        long expirationTime = ttlMillis > 0 
            ? System.currentTimeMillis() + ttlMillis 
            : 0;
        cache.put(key, new CacheEntry<>(value, expirationTime));
    }
    
    /**
     * Retrieves a value, returning null if not found or expired.
     * Accessing an entry moves it to the "most recently used" position.
     */
    public synchronized V get(K key) {
        CacheEntry<V> entry = cache.get(key);
        
        if (entry == null) {
            misses++;
            return null;
        }
        
        if (entry.isExpired()) {
            cache.remove(key);
            misses++;
            return null;
        }
        
        hits++;
        return entry.value;
    }
    
    /**
     * Gets value if present, otherwise computes and caches it.
     * 
     * @param key   Cache key
     * @param loader Function to compute value on cache miss
     * @return Cached or computed value
     */
    public synchronized V getOrCompute(K key, java.util.function.Supplier<V> loader) {
        V value = get(key);
        if (value != null) {
            return value;
        }
        
        value = loader.get();
        if (value != null) {
            put(key, value);
        }
        return value;
    }
    
    /**
     * Removes an entry from cache.
     */
    public synchronized void remove(K key) {
        cache.remove(key);
    }
    
    /**
     * Clears all entries.
     */
    public synchronized void clear() {
        cache.clear();
        hits = 0;
        misses = 0;
        evictions = 0;
    }
    
    /**
     * Returns current number of entries.
     */
    public synchronized int size() {
        return cache.size();
    }
    
    /**
     * Returns cache hit rate as percentage.
     */
    public synchronized double getHitRate() {
        long total = hits + misses;
        return total == 0 ? 0.0 : (hits * 100.0) / total;
    }
    
    /**
     * Returns cache statistics as formatted string.
     */
    public synchronized String getStats() {
        return String.format(
            "CacheStats{size=%d, capacity=%d, hits=%d, misses=%d, " +
            "hitRate=%.2f%%, evictions=%d}",
            size(), capacity, hits, misses, getHitRate(), evictions
        );
    }
    
    /**
     * Removes all expired entries.
     */
    public synchronized void cleanup() {
        cache.entrySet().removeIf(e -> e.getValue().isExpired());
    }
    
    // Getters for statistics
    public long getHits() { return hits; }
    public long getMisses() { return misses; }
    public long getEvictions() { return evictions; }
    public int getCapacity() { return capacity; }
}
