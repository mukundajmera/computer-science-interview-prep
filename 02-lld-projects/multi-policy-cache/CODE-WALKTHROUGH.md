# In-Memory Multi-Policy Cache - Code Walkthrough

This walkthrough explains how the runtime strategy swap and LFU O(1) structures are implemented.

## LFU Implementation (O(1))
The LFU strategy is often difficult to achieve in O(1). We use a combination of:
1. `freqHead` and `freqTail` linked list of frequency buckets (`FreqNode`).
2. A dictionary/map mapping `frequency (int) -> FreqNode`.
3. Each `FreqNode` itself is a doubly linked list of `CacheEntry` objects.

When an item is accessed (`onAccess`):
1. We retrieve the entry's current `FreqNode`.
2. We find or create the `FreqNode` for `frequency + 1`.
3. We move the `CacheEntry` from the old list to the new list.
4. If the old `FreqNode` is empty, we remove it to save memory and maintain strict ordering.

## Strategy Swap Mechanism
The `changePolicy` method handles dynamic transitions.
```java
public void changePolicy(EvictionPolicy newPolicy) {
    lock.writeLock().lock();
    try {
        if (currentPolicy == newPolicy) return;
        EvictionStrategy<K, V> newStrategy = createStrategy(newPolicy);
        
        // Extract unexpired entries
        List<CacheEntry<K, V>> entries = new ArrayList<>(map.values());
        
        // Re-order based on the target strategy's temporal expectations
        if (newPolicy == EvictionPolicy.LRU) {
            entries.sort((a, b) -> Long.compare(a.lastAccessedAt, b.lastAccessedAt));
        } // ... sorting for FIFO/LFU
        
        // Clear the old tracking and ingest linearly into the new strategy
        map.clear();
        for (CacheEntry<K, V> entry : entries) {
            if (!entry.isExpired()) {
                newStrategy.onInsert(entry);
                map.put(entry.key, entry);
            }
        }
        this.strategy = newStrategy;
        this.currentPolicy = newPolicy;
    } finally {
        lock.writeLock().unlock();
    }
}
```
By sorting chronologically before ingestion, `onInsert` places the oldest accesses at the eviction tail and the newest at the safe head, seamlessly recreating the state as if the new policy had been running since the start.

## TTL Expiration Thread
A daemon thread operates in the background:
```python
def _active_expiration(self):
    while self.running:
        time.sleep(1)
        with self.lock:
            to_remove = [k for k, v in self.cache_map.items() if v.is_expired()]
            for key in to_remove:
                entry = self.cache_map.pop(key, None)
                if entry:
                    self.strategy.on_remove(entry)
```
This safely piggybacks on the existing locks to avoid concurrency crashes.
