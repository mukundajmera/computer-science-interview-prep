package v1_basic;
public class CacheEntry<K, V> {
    K key;
    V value;
    long expireAt;
    int frequency;
    long createdAt;
    long lastAccessedAt;

    CacheEntry<K, V> prev;
    CacheEntry<K, V> next;
    Object freqNode;

    public CacheEntry(K key, V value, long ttlMs) {
        this.key = key;
        this.value = value;
        this.expireAt = ttlMs > 0 ? System.currentTimeMillis() + ttlMs : -1;
        this.frequency = 1;
        this.createdAt = System.currentTimeMillis();
        this.lastAccessedAt = this.createdAt;
    }

    public boolean isExpired() {
        return expireAt > 0 && System.currentTimeMillis() > expireAt;
    }
}
