# Common Pitfalls and Failure Traces

1. **Lost Updates on Early WAL Deletion**
   - *Trace:* Write `k1=v1` -> WAL updated -> MemTable threshold met -> Flush starts -> **WAL deleted** -> System crashes before SSTable `fsync`.
   - *Result:* `k1=v1` is permanently lost.
   - *Fix:* The WAL file must only be deleted or truncated *after* the new SSTable is fully synced to disk and registered in the reading hierarchy.

2. **Tombstone Resurrection**
   - *Trace:* `k1` written in SSTable 3 (oldest). `k1` deleted (Tombstone) in SSTable 2. Compaction merges SSTables 1 and 2, observes Tombstone, and discards it because the key is "deleted".
   - *Result:* A subsequent read for `k1` misses the compacted table, hits SSTable 3, and returns the old, deleted value.
   - *Fix:* Tombstones can only be discarded if it is guaranteed that no older SSTables contain the key, or during a full-database compaction.

3. **Concurrency Race Conditions (Synchronous Flush)**
   - *Trace:* Thread A triggers a flush and starts writing an SSTable. Thread B performs a write and modifies the same MemTable being flushed.
   - *Result:* Interleaved data or `ConcurrentModificationException`.
   - *Fix:* Use immutable snapshots of the MemTable for flushing, or enforce strict synchronization across file and memory operations.
