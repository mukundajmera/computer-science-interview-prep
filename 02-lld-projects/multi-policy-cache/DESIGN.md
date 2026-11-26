# In-Memory Multi-Policy Cache - Design

## Architecture & Components

### `MultiPolicyCache` (Main Coordinator)
- **State:** `capacity`, `currentPolicy`, `map` (Key-Value Store), `strategy` (Eviction Strategy), `lock` (Read/Write Lock).
- **Responsibilities:** Manages entry insertion, retrieval, and deletion. Routes cache events to the active eviction strategy. Spawns the active TTL expiration background thread.

### `CacheEntry`
- Contains:
  - Payload: `key`, `value`
  - Metadata: `expireAt`, `frequency`, `createdAt`, `lastAccessedAt`
  - Structural links: `prev`, `next` (for LRU/FIFO lists), `freqNode` (for LFU).

### `EvictionStrategy` (Interface)
- **Methods:**
  - `onAccess(entry)`: Update position on read/update.
  - `onInsert(entry)`: Track newly added item.
  - `onRemove(entry)`: Remove item tracking.
  - `evict()`: Returns the entry to be evicted based on the policy.
  - `clear()`: Resets the strategy.

### Concrete Strategies
- **`LruStrategy`:** Maintains a `head` and `tail` sentinel nodes. `onAccess` and `onInsert` move entries to the front. `evict` removes the node preceding `tail`.
- **`FifoStrategy`:** Similar to LRU, but `onAccess` is a no-op. Only `onInsert` adds to the front.
- **`LfuStrategy`:** Uses `FreqNode` components. A map of integers to `FreqNode` ensures O(1) jump to the next frequency. Eviction drops the tail item from the lowest `FreqNode` linked list.

## Thread Safety Model
- `ReentrantReadWriteLock` ensures that `get` operations that do not mutate cache structure can proceed concurrently (if lock upgrade is not needed, but typically cache accesses update metadata and require a write lock).
- To preserve strict LRU/LFU order safely, `get` requests mutate metadata and therefore acquire the write lock. (Alternatively, access queues can be batched).
- The background TTL cleanup thread runs asynchronously but synchronizes against the same locks during eviction.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Approach](APPROACH.md)
- [Code Walkthrough](CODE-WALKTHROUGH.md)
- [Pitfalls](PITFALLS.md)
- [Interview Scoring Rubric](RUBRIC.md)
- [Follow-up Questions](FOLLOW-UPS.md)
