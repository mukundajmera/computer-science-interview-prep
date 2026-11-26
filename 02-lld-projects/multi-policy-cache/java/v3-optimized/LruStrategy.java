package v3_optimized;
public class LruStrategy<K, V> implements EvictionStrategy<K, V> {
    private final CacheEntry<K, V> head;
    private final CacheEntry<K, V> tail;

    public LruStrategy() {
        head = new CacheEntry<>(null, null, -1);
        tail = new CacheEntry<>(null, null, -1);
        head.next = tail;
        tail.prev = head;
    }

    private void removeNode(CacheEntry<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void addToHead(CacheEntry<K, V> node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    @Override
    public void onAccess(CacheEntry<K, V> entry) {
        removeNode(entry);
        addToHead(entry);
    }

    @Override
    public void onInsert(CacheEntry<K, V> entry) {
        addToHead(entry);
    }

    @Override
    public void onRemove(CacheEntry<K, V> entry) {
        removeNode(entry);
    }

    @Override
    public CacheEntry<K, V> evict() {
        if (tail.prev == head) return null;
        CacheEntry<K, V> toEvict = tail.prev;
        removeNode(toEvict);
        return toEvict;
    }

    @Override
    public void clear() {
        head.next = tail;
        tail.prev = head;
    }
}
