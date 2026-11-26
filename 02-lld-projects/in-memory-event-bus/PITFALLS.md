# In-Memory Event Bus - Pitfalls

- **Non-Thread-Safe Collections**: Using standard non-thread-safe collections (e.g., `ArrayList` in Java, `list` in Python) without explicit locking for partition appends.
- **Coarse-Grained Locking**: Locking the entire `EventBus` for every read/write instead of locking at the `Partition` level, severely degrading throughput.
- **Non-Atomic Offset Commits**: Failing to use atomic updates (e.g., `ConcurrentHashMap.merge` in Java) for offsets, leading to lost offset updates and message replays during concurrent polling.
- **Deadlocks in Retry Logic**: Acquiring nested locks inconsistently when moving events between partitions and retry queues/DLQ.
