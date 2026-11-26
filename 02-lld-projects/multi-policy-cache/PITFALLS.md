# In-Memory Multi-Policy Cache - Common Pitfalls

## 1. O(N) or O(log N) LFU Complexity
- **Signal:** Candidate uses a standard `PriorityQueue` or `TreeMap` sorted by frequency for the LFU strategy.
- **Root Cause:** Lack of familiarity with the optimal O(1) LFU data structure (hashmap of frequency linked lists).
- **Mitigation:** Guide the candidate to consider how to group items with identical frequencies, and how a doubly linked list can handle O(1) inserts/deletes if the nodes are tracked in a hash map.

## 2. Incomplete State Transfer During Policy Swapping
- **Signal:** When switching from LRU to FIFO, the candidate dumps all entries into the new strategy without sorting.
- **Root Cause:** Failing to realize that iteration order over a `HashMap` is pseudo-random. Re-inserting elements randomly breaks the temporal ordering expected by the new policy.
- **Mitigation:** Suggest considering the state metadata (`lastAccessedAt`, `createdAt`) and how it maps to the new target policy prior to re-insertion.

## 3. ConcurrentModificationException during TTL Sweeps
- **Signal:** Background thread iterates over `cache.values()` and directly calls `cache.remove()` without acquiring a lock or using an iterator properly.
- **Root Cause:** Basic Java/Python iteration vs. modification concurrency violation.
- **Mitigation:** Recommend accumulating expired keys in a separate list during iteration, then removing them sequentially, or using thread-safe data structures correctly under a write lock.

## 4. Pointer Manipulation Bugs in Doubly Linked Lists
- **Signal:** Cache entries get lost, or `evict()` throws `NullPointerException`.
- **Root Cause:** Forgetting to update `prev.next` or `next.prev` when inserting or deleting nodes.
- **Mitigation:** Create robust, separate helper methods for `addNode(node)` and `removeNode(node)` and use Sentinel Head/Tail nodes to avoid null checks.
