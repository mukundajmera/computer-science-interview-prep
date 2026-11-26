# Strong Answer: Multi Policy Cache

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Multi Policy Cache, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

- **Normal use-cases:** Valid keys and values are inserted, retrieved, or deleted. Hitting a key updates its metadata according to the active policy.
- **Empty/invalid input:** Cache operations must handle null keys gracefully by either rejecting them or hashing them safely to a designated segment.
- **Duplicate operations:** Re-inserting an existing key correctly updates its value, extends its TTL (if provided), and re-evaluates the active eviction strategy's metadata.
- **Capacity boundary:** Hitting the maximum capacity triggers immediate eviction according to the active strategy *before* completing the insertion of the new element. If capacity is 0, the cache might either reject the insertion or instantly evict.
- **Failure rollback:** If a transaction fails mid-update, the system must gracefully revert its state changes to prevent partial or corrupted node metadata.

## 2. API Contract & Implementation Snippets (15 mins)
**Say:** "Let's review the exact API contracts and how these critical scenarios are handled in code, maintaining full parity across Java and Python implementations."

### Public APIs
The cache exposes the following public APIs:
- `put(key, value, ttl_ms)`: Inserts or updates a key-value pair, with an optional TTL.
- `get(key)`: Retrieves the value for a given key.
- `remove(key)`: Removes a key from the cache.
- `change_policy(new_policy)`: Dynamically changes the eviction policy.
- `size()`: Returns the total number of items currently in the cache.
- `shutdown()`: Stops background tasks like active expiration threads.

### Normal Use-Case & Duplicate Operations
When `put()` is called, if the key already exists (duplicate operation), we update the value and TTL, boost frequency, and re-trigger access tracking. Otherwise, it's a normal insert.

**Java Snippet (`MultiPolicyCache.java` / `CacheSegment`):**
```java
                if (map.containsKey(key)) {
                    CacheEntry<K, V> entry = map.get(key);
                    entry.value = value;
                    entry.expireAt = ttlMs > 0 ? System.currentTimeMillis() + ttlMs : -1;
                    entry.lastAccessedAt = System.currentTimeMillis();
                    entry.frequency++;
                    strategy.onAccess(entry);
                } else {
                    // Normal insert logic
                }
```

**Python Snippet (`multi_policy_cache.py` / `CacheSegment`):**
```python
            if key in self.cache_map:
                entry = self.cache_map[key]
                entry.value = value
                entry.expire_at = now + ttl_ms if ttl_ms > 0 else -1
                entry.last_accessed_at = now
                entry.frequency += 1
                self.strategy.on_access(entry)
            else:
                # Normal insert logic
```

### Capacity Boundary & Empty Input
If the cache reaches capacity (capacity boundary), eviction occurs synchronously. For empty or null input handling, keys hash appropriately to find the target segment (e.g. 0 for null in Java) or gracefully rejected.

**Java Snippet (`MultiPolicyCache.java` / `CacheSegment`):**
```java
                    if (map.size() >= capacity && capacity > 0) {
                        CacheEntry<K, V> evicted = strategy.evict();
                        if (evicted != null) {
                            map.remove(evicted.key);
                            stats.evictions++;
                            entry = evicted;
```
```java
    private CacheSegment<K, V> getSegment(K key) {
        int hash = key == null ? 0 : key.hashCode();
        return segments[Math.abs(hash % numSegments)];
    }
```

**Python Snippet (`multi_policy_cache.py` / `CacheSegment`):**
```python
                if len(self.cache_map) >= self.capacity and self.capacity > 0:
                    evicted = self.strategy.evict()
                    if evicted is not None:
                        del self.cache_map[evicted.key]
                        self.stats.evictions += 1
                        entry = evicted
```
```python
    def _get_segment(self, key: Any) -> CacheSegment:
        return self.segments[hash(key) % self.num_segments]
```

### Failure Rollback
When manipulating linked list nodes for LFU metadata, if adding to a new frequency bucket fails (e.g. OOM or thread interrupt before assignment), the implementation leaves the entry detached rather than leaving a corrupted pointer. The underlying map must not point to a broken node. This failure rollback ensures the cache remains in a valid state.

**Java Snippet (`LfuStrategy.java`):**
```java
        FreqNode nextFreqNode = currentFreqNode.next;
        if (nextFreqNode.freq != nextFreq) {
            nextFreqNode = addFreqNodeAfter(nextFreq, currentFreqNode);
        }
        nextFreqNode.addEntry(entry);
        entry.frequency = nextFreq;
```

**Python Snippet (`multi_policy_cache.py`):**
```python
        next_freq_node = current_freq_node.next
        if next_freq_node.freq != next_freq:
            next_freq_node = self._add_freq_node_after(next_freq, current_freq_node)
            
        next_freq_node.add_entry(entry)
```

## 3. Version Deltas and Focus (5 mins)
**Say:** "As the implementation evolves through versions, feature deltas emerge:
- **v1-basic** & **v2-extended**: These versions use a single core map. v1 has the basic thread safety (using locks in `MultiPolicyCache` in Java). v2 refines the operations (like ensuring `entry.frequency++` during `put` logic for existing entries).
- **v3-optimized**: Segments the cache into multiple `CacheSegment`s (sharding) to reduce lock contention, tracking `CacheStats` and introduces object pooling."

Focused tests target this optimized `v3` version logic rather than silently importing `v1`.

**Java Snippet (`MultiPolicyCacheV3Test.java`):**
```java
package v3_optimized;
import org.junit.jupiter.api.Test;
// ...
public class MultiPolicyCacheV3Test {
    @Test
    public void testV3TtlActiveBackgroundExpiry() throws InterruptedException {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(100, EvictionPolicy.LRU, 4);
        // ...
    }
}
```

**Python Snippet (`test_v3_optimized.py`):**
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))
from multi_policy_cache import MultiPolicyCache, EvictionPolicy

def test_v3_ttl_active_background_expiry():
    cache = MultiPolicyCache(capacity=100, policy=EvictionPolicy.LRU, num_segments=4)
    # ...
```

## 4. Design Pattern Justifications (5 mins)
**Say:** "To keep the system modular, I've applied the Strategy Pattern."
The Strategy Pattern acts as the contract for various algorithms, separating the cache storage mechanism from the eviction logic. 

## 5. Concurrency Defense & Thread-Safety Details (10 mins)
**Say:** "Given that this system will be accessed by multiple threads concurrently, ensuring thread safety without creating bottlenecks is a priority."
In **v3**, we mitigate lock contention by sharding. Hashing the key dictates the segment, so distinct keys can be updated fully concurrently. Active expiration samples segments randomly rather than holding a global lock.

## 6. Production Trade-offs (2 mins)
**Say:** "Maintaining multiple eviction policies and metadata consumes extra memory per cache entry. This overhead must be mathematically justified by a significant hit-rate improvement over a simpler LRU."
