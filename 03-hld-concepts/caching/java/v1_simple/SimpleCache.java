package v1_simple;
import java.util.HashMap;
import java.util.Map;

/**
 * V1: Simple Cache Implementation
 * 
 * A basic in-memory cache with TTL (Time-To-Live) support.
 * This demonstrates the core concept of caching: storing data
 * for fast retrieval with automatic expiration.
 * 
 * Features:
 * - HashMap-based storage
 * - TTL-based expiration
 * - Thread-safe operations not included (single-threaded use)
 * 
 * Limitations:
 * - No size limit (can grow unbounded)
 * - No eviction policy
 * - Expired entries cleaned only on access
 */
public class SimpleCache<K, V> {
    
    private final Map<K, CacheEntry<V>> cache;
    private final long defaultTtlMillis;
    
    /**
     * Entry wrapper that stores value with expiration time.
     */
    private static class CacheEntry<V> {
        final V value;
        final long expirationTime;
        
        CacheEntry(V value, long expirationTime) {
            this.value = value;
            this.expirationTime = expirationTime;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }
    }
    
    /**
     * Creates a cache with specified default TTL.
     * 
     * @param defaultTtlSeconds Default time-to-live in seconds
     */
    public SimpleCache(int defaultTtlSeconds) {
        this.cache = new HashMap<>();
        this.defaultTtlMillis = defaultTtlSeconds * 1000L;
    }
    
    /**
     * Stores a value with the default TTL.
     */
    public void put(K key, V value) {
        put(key, value, defaultTtlMillis);
    }
    
    /**
     * Stores a value with a custom TTL.
     * 
     * @param key   Cache key
     * @param value Value to store
     * @param ttlMillis Time-to-live in milliseconds
     */
    public void put(K key, V value, long ttlMillis) {
        long expirationTime = System.currentTimeMillis() + ttlMillis;
        cache.put(key, new CacheEntry<>(value, expirationTime));
    }
    
    /**
     * Retrieves a value from cache.
     * Returns null if key doesn't exist or is expired.
     */
    public V get(K key) {
        CacheEntry<V> entry = cache.get(key);
        
        if (entry == null) {
            return null;
        }
        
        // Check if entry has expired
        if (entry.isExpired()) {
            cache.remove(key);
            return null;
        }
        
        return entry.value;
    }
    
    /**
     * Removes an entry from cache.
     */
    public void remove(K key) {
        cache.remove(key);
    }
    
    /**
     * Clears all entries from cache.
     */
    public void clear() {
        cache.clear();
    }
    
    /**
     * Returns the number of entries (including potentially expired ones).
     */
    public int size() {
        return cache.size();
    }
    
    /**
     * Checks if a key exists and is not expired.
     */
    public boolean containsKey(K key) {
        return get(key) != null;
    }
    
    /**
     * Removes all expired entries.
     * Call periodically to free memory.
     */
    public void cleanup() {
        cache.entrySet().removeIf(entry -> entry.getValue().isExpired());
    }
}
