# Optional Staff Follow-Ups

*Note: The following features are unimplemented extensions and are not present in the baseline v1-v3 codebase. They serve as advanced discussion points for Staff-level interviews.*

1. **Read Optimization (Bloom Filters)**
   - *Concept:* Implement a Bloom Filter for each SSTable to quickly probabilistically determine if a key is absent, bypassing expensive disk I/O.
   - *Discussion:* Trade-off between memory usage for the filter and the CPU/IO savings. Handling false positives safely.

2. **Background Compaction**
   - *Concept:* Move synchronous compaction (v3) to a background thread pool.
   - *Discussion:* How to synchronize the atomic swap of the SSTable pointers once the background merge completes, ensuring readers are never blocked and see a consistent view.

3. **Sparse Indexing & Block Cache**
   - *Concept:* Instead of scanning an entire `.sst` file sequentially, maintain a sparse index mapping keys to byte offsets, and cache frequently accessed blocks in memory.
   - *Discussion:* Defending memory bounds and cache invalidation strategies (LRU vs. LFU) under high throughput.

4. **Crash-Safe File Swapping**
   - *Concept:* Write flushes/compactions to a `.sst.tmp` file first.
   - *Discussion:* On success, atomically rename to `.sst`. On crash, delete orphaned `.tmp` files during recovery before replaying the WAL.
