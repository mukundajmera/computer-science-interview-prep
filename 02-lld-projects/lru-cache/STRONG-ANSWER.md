# Strong Answer: Lru Cache

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the LRU Cache, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

**Clarifications to seek:**
- **Capacity:** What is the expected capacity? (Must be at least 1).
- **Types:** What types of keys and values need to be supported? (Generic `K`, `V`).
- **Thread Safety:** Is thread-safety required? (Yes, highly concurrent for v3).
- **Edge cases:** Do we need to support null keys/values? (No, throw `IllegalArgumentException`).

## 2. Entity Modeling & APIs (10 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."
- `LRUCache<K, V>`: The main public interface for the cache with `get(key)`, `put(key, value)`, `remove(key)`, `containsKey(key)`, `size()`, and `clear()`.
- `CacheNode<K, V>`: Holds the key, volatile value, and `prev`/`next` pointers for the doubly linked list.
- `DoublyLinkedList<K, V>`: Handles the structural ordering of the cache using dummy `head` and `tail` sentinel nodes to avoid null checks.
- `ConcurrentLRUCache<K, V>`: Uses a collection of `Segment<K, V>` (lock striping) to achieve high concurrency.

## 3. Data Structure Rationale & Correctness (10 mins)
**Say:** "Choosing the right data structures is critical for meeting our latency and throughput requirements."
- I use a `HashMap` mapping keys to `CacheNode`s for **O(1)** lookups.
- This is paired with a custom `DoublyLinkedList` to maintain access order.
- This combination guarantees **O(1)** time complexity for `get`, `put`, and `remove` operations. Space complexity is **O(N)** where N is the capacity.
- Overwrites must update the value and move the node to the front, preserving the map/list cardinality and capacity bounds. Evictions must cleanly remove the tail node and remove its key from the map.

## 4. Design Pattern Justifications (5 mins)
**Say:** "To keep the system modular and maintainable, I've applied specific design patterns."
- The **Strategy Pattern** allows us to plug in different eviction algorithms (like LFU or FIFO) in the future without modifying core logic, through an `EvictionPolicy` interface.
- Sentinel nodes (dummy head and tail) in the linked list eliminate conditional branching for empty list states.

## 5. Concurrency Defense & Thread-Safety Details (10 mins)
**Say:** "Given that this system will be accessed by multiple threads concurrently, ensuring thread safety without creating bottlenecks is a priority."
- A naive approach uses a single global lock (or `ReadWriteLock`), but `get` operations still mutate the linked list order, making it a write operation.
- **Lock Striping:** To defend against concurrency issues and prevent deadlocks, I divide the cache into independent segments, each with its own map, list, and `ReentrantLock`.
- When a thread accesses a key, we hash the key and mod by the number of segments to route it to the specific segment. This reduces lock contention and improves throughput significantly.

## 6. Failure Handling & Concrete Concurrency Discussion (5 mins)
**Say:** "Systems fail and concurrent environments introduce subtle bugs, so we need to handle these gracefully."
- **Strict LRU vs Lock Striping Trade-off:** By using independent segments, the global LRU property is lost. We only maintain strict LRU *within each segment*. A globally least recently used item might not be evicted if its segment is not full. This is a standard trade-off for high concurrency (as seen in Guava Cache or ConcurrentHashMap).
- **Concurrency Correctness:** Under heavy concurrent load, if we didn't use `ReentrantLock` per segment, a race condition could occur where two threads try to promote different nodes to the front simultaneously, breaking the pointers in the `DoublyLinkedList` and causing data loss or infinite loops. Barrier-started concurrent tests confirm that our segmented lock approach preserves structural integrity.
