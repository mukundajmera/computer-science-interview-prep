# In-Memory Multi-Policy Cache - Approach

## Core Storage
The foundation of the cache is a concurrent hash map acting as the primary key-value store. This map stores `CacheEntry` objects that encapsulate the actual value along with essential metadata: `key`, `value`, `expireAt`, `frequency`, `createdAt`, and `lastAccessedAt`.

## Eviction Strategy Pattern
To support multiple policies, the Strategy design pattern is employed:
- An interface `EvictionStrategy` defines the contract for eviction events: `onAccess`, `onInsert`, `onRemove`, `evict`, and `clear`.
- **LruStrategy:** Uses a doubly linked list. Most recently used items are kept near the head, and least recently used near the tail.
- **FifoStrategy:** Uses a doubly linked list. Newly inserted items are added to the head, and oldest items are removed from the tail. `onAccess` does not alter the queue.
- **LfuStrategy:** Implements O(1) LFU tracking using doubly linked frequency buckets. Each bucket (`FreqNode`) tracks items with a specific access count and maintains its own doubly linked list of `CacheEntry` objects to handle ties (acting as an LRU within that frequency). A `freqMap` maps frequencies to their respective `FreqNode`.

## Concurrency
To ensure thread safety, a `ReentrantReadWriteLock` (Java) or `threading.RLock` (Python) wraps operations. While `ConcurrentHashMap` provides basic atomic operations, locking is necessary to atomically synchronize updates between the cache map and the underlying eviction strategy data structures.

## Runtime Policy Swapping
The `changePolicy` method allows dynamic switching. It:
1. Acquires a lock to halt other operations.
2. Creates the new target `EvictionStrategy`.
3. Extracts all unexpired elements from the cache map.
4. Sorts the elements chronologically based on metadata (`lastAccessedAt` for LRU/LFU, `createdAt` for FIFO) to establish correct initial state ordering.
5. Ingests the sorted elements into the new strategy sequentially to recreate the internal tracking state.
6. Swaps the strategy reference.

## TTL Expiration
- **Passive:** Checked explicitly during `get()`. If the current time exceeds `expireAt`, the item is evicted and `null` is returned.
- **Active:** A daemon background thread wakes up periodically (e.g., every 1 second), scans the map under a write lock (or batching), and evicts items whose TTL has expired.
