# Storage Engine Internals - Interview Q&A

This document contains 10 rigorous interview questions addressing critical operational and architectural challenges in storage engines, specifically focusing on B-Trees and LSM-Trees.

## 1. What causes a "write stall" in an LSM-Tree, and how can it be mitigated?
**Answer:** A write stall occurs when the database temporarily pauses or slows down accepting new writes from clients. This happens when the rate of incoming writes exceeds the rate at which the background compaction process can merge and flush SSTables to disk.
* **Root Cause:** If L0 (Level 0) SSTables accumulate too fast, read amplification spikes uncontrollably because queries must check many overlapping L0 files. To protect read performance and prevent exhausting disk space or memory (if MemTables cannot flush fast enough), the engine artificially throttles or stalls incoming writes.
* **Mitigation:** 
    * Tuning compaction threads to parallelize merging.
    * Using a different compaction strategy (e.g., switching from Leveled to Size-Tiered if the workload is heavily write-skewed, trading off read performance/space for write throughput).
    * Provisioning faster storage (NVMe SSDs) to speed up I/O.
    * Increasing MemTable sizes to flush larger chunks less frequently.

## 2. Explain the concept of a "compaction storm" and its impact on production systems.
**Answer:** A compaction storm is a severe degradation in database performance caused by an excessive, concurrent surge of background compaction operations.
* **Impact:** Compaction is highly CPU and I/O intensive. During a storm, compaction tasks compete with foreground read/write queries for resources, causing severe spikes in query latency, potential timeouts, and a cascading failure effect if the system is load-balanced (as health checks might fail).
* **Prevention:** Rate-limiting compaction I/O bandwidth so it does not starve client requests. Carefully tuning the size multipliers between levels (in Leveled Compaction) or size thresholds (in Size-Tiered) to smooth out the compaction workload over time rather than triggering massive merges all at once.

## 3. How do B+ Trees and LSM-Trees impact SSD write endurance differently?
**Answer:** Solid State Drives (SSDs) wear out based on the number of Program/Erase (P/E) cycles; this is tied to "Write Amplification."
* **B+ Trees:** Exhibit higher write amplification for small, random updates because modifying a single 100-byte record requires rewriting the entire 4KB-16KB page, plus WAL logging. This can wear out an SSD faster under heavy, random OLTP write workloads.
* **LSM-Trees:** Sequential appends are much friendlier to SSDs initially. However, the background compaction process repeatedly rewrites the same data as it moves down the levels (e.g., L1 to L2 to L3). Depending on the compaction strategy (especially Leveled Compaction), the total disk writes over the lifecycle of a record can be extremely high, causing significant SSD wear. This trade-off must be managed by tuning compaction.

## 4. Why are Bloom Filters critical for LSM-Trees but rarely used in B+ Trees?
**Answer:** Bloom filters act as a rapid "definitely not here" check.
* **LSM-Trees:** Because a single read might have to check the MemTable and dozens of on-disk SSTables (especially in L0 or Size-Tiered), searching all of them is prohibitively expensive. A Bloom filter is kept in memory for each SSTable. If the filter says the key is absent, the engine skips reading that SSTable entirely, drastically reducing Read Amplification.
* **B+ Trees:** Data is stored in exactly one definitive location. A B+ Tree traverses its internal routing nodes (often cached in memory) directly to the specific leaf page. Since it doesn't need to check multiple overlapping files, the probabilistic check of a Bloom filter is unnecessary.

## 5. How is a range query executed in a B+ Tree compared to an LSM-Tree, and which is generally faster?
**Answer:**
* **B+ Tree:** Executes highly efficiently. The engine traverses the tree to find the start key of the range. Since the leaf nodes are linked via a doubly-linked list, the engine simply scans forward across the leaves until the end condition is met.
* **LSM-Tree:** More complex. The engine must instantiate iterators across the MemTable, L0 SSTables, and the relevant ranges of lower-level SSTables. These iterators are then fed into a priority queue (min-heap) to perform an N-way merge sort on the fly, yielding the final ordered sequence.
* **Conclusion:** B+ Trees are fundamentally optimized for range queries and offer superior performance. LSM-Trees can struggle with range queries due to the overhead of merging multiple sorted streams.

## 6. If a specific key is updated continuously (e.g., a view counter), which storage engine architecture is superior?
**Answer:** An in-place update engine (like a B+ Tree, though typically an in-memory store like Redis is preferred for raw counters) is generally better suited for highly concentrated updates on a small set of keys.
* In a B+ Tree, the page containing the counter is locked in the in-memory buffer pool and updated directly. If it's a hot key, the disk write is deferred and amortized.
* In an LSM-Tree, every single update to that counter creates a new entry appended to the WAL and MemTable. This rapidly fills the MemTable, forces frequent flushes, and litters the SSTables with obsolete versions of the same counter. This drastically inflates Space Amplification and triggers unnecessary compactions just to collapse the versions.

## 7. How does the ARIES protocol ensure crash recovery in B+ Trees?
**Answer:** ARIES (Algorithm for Recovery and Isolation Exploiting Semantics) uses a WAL and a three-phase recovery process upon crash:
1. **Analysis Phase:** Scans the WAL forward from the last checkpoint to identify which transactions were active at the time of the crash and which dirty pages were not flushed to disk.
2. **Redo Phase:** Repeats the history by reapplying all operations from the WAL (including those of uncommitted transactions) to bring the database back exactly to the state it was in at the crash moment.
3. **Undo Phase:** Scans backward to roll back any operations of transactions that were incomplete (uncommitted) at the crash, ensuring atomicity.

## 8. Explain how tombstones work in LSM-Trees and the specific edge cases they introduce.
**Answer:** Since SSTables are immutable, a delete operation cannot overwrite the actual data. Instead, it inserts a "tombstone" marker with the key. During a read, if the tombstone is encountered first (because it is newer), it masks any older values, and the engine returns "not found".
* **Edge Case - Zombie Data:** Tombstones can only be physically purged during compaction if the engine proves no older versions of the key exist in deeper levels. If a tombstone is dropped prematurely, an older, previously deleted version of the data might "resurrect" and become visible again.
* **Edge Case - Slow Range Scans:** A massive bulk delete operation writes thousands of tombstones. A subsequent range query must read past all these tombstones to find actual live data, severely degrading performance until a major compaction clears them.

## 9. How do sparse indexes work in SSTables, and why not use dense indexes?
**Answer:**
* **Dense Index:** Contains a pointer for every single key. This consumes massive amounts of memory, defeating the purpose of keeping data on disk.
* **Sparse Index:** An SSTable is divided into fixed-size data blocks (e.g., 4KB). The sparse index only stores the first (minimum) key of each block and the block's disk offset. 
* **Operation:** To find a key, the engine binary searches the small sparse index in memory to find the specific 4KB block that *might* contain the key. It then loads only that block from disk and linearly or binary searches within the block. This strikes a perfect balance between memory overhead and disk I/O efficiency.

## 10. Contrast Size-Tiered Compaction (STCS) with Leveled Compaction (LCS).
**Answer:**
* **Size-Tiered (e.g., Cassandra):** Groups SSTables of similar sizes. When X files of size Y exist, it merges them into one file of size X*Y. 
    * *Pros:* Lower Write Amplification. Great for heavy ingest.
    * *Cons:* High Space Amplification (requires up to 50% free disk space to perform a major compaction). High Read Amplification because a read must check multiple files of varying sizes.
* **Leveled (e.g., RocksDB):** Organizes files into distinct levels (L1, L2...). Each level is 10x larger than the one above it. Files within a level have strictly non-overlapping key ranges.
    * *Pros:* Tightly bounds Space Amplification. Excellent Read Amplification because the non-overlapping ranges mean exactly one file per level needs to be checked.
    * *Cons:* High Write Amplification because moving a file from L1 to L2 requires merging it with all overlapping files in L2, rewriting the data multiple times.