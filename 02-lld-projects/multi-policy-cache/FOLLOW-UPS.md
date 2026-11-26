# In-Memory Multi-Policy Cache - Follow-Up Questions

## Follow-up questions

1. **Lock Contention:** Your design requires a write lock for every `get` operation to update access metadata (e.g., LRU queue). How would you optimize this under high read throughput?
   *Expected Answer:* Introduce an asynchronous metadata queue (e.g., Disruptor or ConcurrentLinkedQueue). `get` calls would acquire a read lock, return the value, and drop an access event into the queue. A background thread processes the queue to update the LRU pointers in batches.

2. **Distributed Cache Scaling:** If this cache were to be extended across multiple nodes, how would you handle consistency and eviction?
   *Expected Answer:* Discuss Consistent Hashing to distribute keys. For eviction policies globally, each node manages its own local policy. To sync TTL, nodes should send invalidation messages via a publish-subscribe broker (like Redis Pub/Sub or Kafka).

3. **Memory Leaks:** How do you ensure the `FreqNode` objects in the LFU strategy do not leak memory if elements frequently jump to unique high frequencies?
   *Expected Answer:* The design actively checks if a `FreqNode` becomes empty (`head.next == tail`) during item migration and immediately removes it from the `freqMap` and the frequency linked list.

## Variants and extensions
- **Weight-based Eviction:** Instead of a fixed count capacity, limit the cache by total payload byte size.
- **Probabilistic Expiry:** To prevent Cache Stampedes, introduce a probabilistic early-expiration mechanism.
- **Persistent Backing:** Implement a Write-Through or Write-Back mechanism to persist the cache to disk on eviction.
