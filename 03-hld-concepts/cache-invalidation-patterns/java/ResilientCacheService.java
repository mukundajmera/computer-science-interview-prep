package cacheinvalidationpatterns;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Function;

public class ResilientCacheService<K, V> {
    private final Map<K, CacheEntry<V>> cache = new ConcurrentHashMap<>();
    private final Map<K, ReentrantLock> locks = new ConcurrentHashMap<>();
    private final Function<K, Boolean> bloomFilter;
    
    private final long baseTtlMillis;
    private final long jitterMillis;
    private final long nullTtlMillis;

    public ResilientCacheService(Function<K, Boolean> bloomFilter, long baseTtlMillis, long jitterMillis, long nullTtlMillis) {
        this.bloomFilter = bloomFilter;
        this.baseTtlMillis = baseTtlMillis;
        this.jitterMillis = jitterMillis;
        this.nullTtlMillis = nullTtlMillis;
    }

    public static class CacheEntry<V> {
        public final V value;
        public final long expireAt;
        public final boolean isNullObject;

        public CacheEntry(V value, long expireAt, boolean isNullObject) {
            this.value = value;
            this.expireAt = expireAt;
            this.isNullObject = isNullObject;
        }
    }

    public V get(K key, Function<K, V> dbLoader) {
        // 1. Bloom Filter Check (Cache Penetration Mitigation)
        if (!bloomFilter.apply(key)) {
            return null; // Key definitely does not exist
        }

        CacheEntry<V> entry = cache.get(key);
        
        // Logical Expiration Check
        if (entry != null && System.currentTimeMillis() < entry.expireAt) {
            return entry.isNullObject ? null : entry.value;
        }

        // Cache Miss or Expired (Thundering Herd Mitigation via Singleflight/Mutex)
        ReentrantLock lock = locks.computeIfAbsent(key, k -> new ReentrantLock());
        lock.lock();
        try {
            // Double-checked locking
            entry = cache.get(key);
            if (entry != null && System.currentTimeMillis() < entry.expireAt) {
                return entry.isNullObject ? null : entry.value;
            }

            // Load from DB
            V dbValue = dbLoader.apply(key);

            // Null Object Caching (Cache Penetration Mitigation)
            if (dbValue == null) {
                long expireAt = System.currentTimeMillis() + nullTtlMillis;
                cache.put(key, new CacheEntry<>(null, expireAt, true));
                return null;
            }

            // Jittered TTL (Cache Avalanche Mitigation)
            long ttl = baseTtlMillis + (jitterMillis > 0 ? ThreadLocalRandom.current().nextLong(jitterMillis) : 0);
            long expireAt = System.currentTimeMillis() + ttl;
            cache.put(key, new CacheEntry<>(dbValue, expireAt, false));
            
            return dbValue;
        } finally {
            lock.unlock();
            // Cleanup lock if not used anymore (simplified for this example)
            locks.remove(key, lock); 
        }
    }
    
    // Package-private for testing
    CacheEntry<V> getRawEntry(K key) {
        return cache.get(key);
    }
}
