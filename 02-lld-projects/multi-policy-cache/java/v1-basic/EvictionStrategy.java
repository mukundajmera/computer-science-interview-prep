package v1_basic;
public interface EvictionStrategy<K, V> {
    void onAccess(CacheEntry<K, V> entry);
    void onInsert(CacheEntry<K, V> entry);
    void onRemove(CacheEntry<K, V> entry);
    CacheEntry<K, V> evict();
    void clear();
}
