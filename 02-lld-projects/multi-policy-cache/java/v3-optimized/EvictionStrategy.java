package v3_optimized;
public interface EvictionStrategy<K, V> {
    void onAccess(CacheEntry<K, V> entry);
    void onInsert(CacheEntry<K, V> entry);
    void onRemove(CacheEntry<K, V> entry);
    CacheEntry<K, V> evict();
    void clear();
}
