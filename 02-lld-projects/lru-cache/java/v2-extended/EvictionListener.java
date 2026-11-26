package v2_extended;

/**
 * LRU Cache - V2 Extended
 * 
 * Listener interface for cache eviction events.
 */
public interface EvictionListener<K, V> {
    
    /**
     * Cause of eviction.
     */
    enum EvictionCause {
        CAPACITY,    // Evicted due to capacity limit
        EXPIRED,     // Evicted due to TTL expiration
        EXPLICIT,    // Explicitly removed by user
        REPLACED     // Value replaced with new value
    }

    /**
     * Called when an entry is evicted from the cache.
     * 
     * @param key The evicted key
     * @param value The evicted value
     * @param cause The reason for eviction
     */
    void onEviction(K key, V value, EvictionCause cause);
}
