# Storage Engine Internals - B-Tree vs LSM-Tree

Storage engines form the underlying data management component of a database, responsible for how data is structured, written to disk, and retrieved. The core architectural decision most modern databases face is choosing between in-place updates and append-only write patterns, which typically manifest as B+ Trees and Log-Structured Merge Trees (LSM-Trees), respectively.

## Core Paradigms

### In-Place Updates (B+ Tree)
B+ Trees represent the classical approach to database storage. Data is stored in pages (typically 4KB to 16KB) on disk. When a record is updated or inserted, the database locates the specific page containing the record, updates it in memory, and overwrites the existing page on disk. This approach minimizes read amplification since data remains strictly organized and localized, making read operations highly predictable and efficient. However, in-place updates require random disk I/O, which is expensive (especially on hard disk drives) and can lead to write amplification due to page splits, logging, and fragmentation.

### Append-Only Log-Structured Merge Tree (LSM-Tree)
LSM-Trees optimize for high write throughput by embracing an append-only architecture. Instead of modifying existing data on disk, all incoming writes (inserts, updates, and deletes) are sequentially appended to an in-memory structure (MemTable) and a Write-Ahead Log (WAL). Once the MemTable fills up, it is flushed to disk as an immutable Sorted String Table (SSTable). Since data is never modified in place, write operations bypass random disk I/O, converting random writes into sequential writes. This significantly increases write throughput but introduces a background compaction process to merge SSTables, delete obsolete data, and optimize reads.

## RUM Conjecture

The RUM Conjecture asserts that a storage engine can only optimize for two of the following three overheads at the expense of the third:

1. **Read Amplification (R):** The amount of data read from disk relative to the actual data requested. High in LSM-Trees (before compaction) due to checking multiple SSTables.
2. **Update/Write Amplification (U):** The amount of data written to disk relative to the actual new data. High in B+ Trees due to page splits and full-page writes; also present in LSM-Trees during compaction.
3. **Memory/Space Amplification (M):** The extra disk space required to store the data (e.g., fragmentation, multiple versions of a key). High in uncompacted LSM-Trees.

B+ Trees generally optimize for Read (R) and Space (M) at the cost of Write (U). LSM-Trees optimize for Write (U) and Space (M) at the cost of Read (R), though different compaction strategies shift the balance.

## LSM-Tree Deep Dive

### Write Path
1. **Write-Ahead Log (WAL):** To ensure durability, incoming writes are first sequentially appended to the WAL on disk. If the database crashes, the WAL is used to reconstruct lost in-memory data.
2. **MemTable:** After writing to the WAL, the data is inserted into an in-memory data structure called a MemTable. This is typically implemented as a SkipList or a Red-Black Tree, which keeps the keys sorted.

### Flush Path
When the MemTable reaches a predefined size threshold (e.g., 64MB), it is "frozen" and a new MemTable is created for incoming writes. The frozen MemTable is then flushed sequentially to disk as an immutable **Sorted Strings Table (SSTable)** at Level 0 (L0). 

### SSTable Anatomy
An SSTable is an immutable, sorted file format containing:
* **Data Blocks:** The actual key-value pairs, typically compressed (e.g., Snappy or LZ4).
* **Sparse Index Table:** An index pointing to the start key of each data block, allowing binary search to quickly locate the correct block without loading the entire file into memory.
* **Bloom Filter:** A probabilistic data structure that quickly answers if a key *might* be in the SSTable or is *definitely not*. The optimal number of hash functions (k) is calculated as `k = (m/n) * ln(2)`, where `m` is the number of bits and `n` is the number of inserted keys.
* **Metadata Block:** Contains statistics like minimum and maximum keys, size, etc.

### Compaction Strategies
Over time, flushing MemTables creates many SSTables with overlapping key ranges, increasing read amplification. Compaction is the background process of merging these SSTables and removing overwritten keys or tombstones.

* **Size-Tiered Compaction (STCS):** Focuses on write performance. When the number of SSTables of a similar size reaches a threshold, they are merged into a single larger SSTable. It provides lower write amplification but suffers from higher space amplification (up to 2x space required during compaction) and higher read amplification. Used in Cassandra.
* **Leveled Compaction (LCS):** Optimizes for read performance and space. Data is organized into strictly sized levels (L1, L2, etc.). Each level is 10x larger than the previous, and SSTables within a level (except L0) have non-overlapping key ranges. It tightly bounds space amplification and improves read latency but increases write amplification as a single SSTable might be rewritten multiple times as it moves down the levels. Used in RocksDB / LevelDB.

### Delete Handling
Since SSTables are immutable, LSM-Trees handle deletes by writing a special marker called a **Tombstone**. The tombstone indicates that the key has been deleted. During reads, if a tombstone is encountered, the engine returns a "not found" result. Tombstones are physically removed from disk only during the compaction process when the engine can guarantee that no older versions of the key exist in lower levels.

## B+ Tree Deep Dive

### Structure and Operations
A B+ Tree is a self-balancing tree data structure that maintains sorted data.
* **Page Layout:** Data is divided into fixed-size pages (typically 4KB to 16KB). 
* **Internal Routing Keys:** Internal (non-leaf) nodes only contain routing keys and pointers to child pages, maximizing the branching factor and minimizing the tree height.
* **Leaf Linked Records:** All actual key-value data is stored in the leaf nodes. The leaf nodes are typically linked together in a doubly-linked list, making range queries highly efficient.
* **Random Disk I/O:** Reading or writing a specific key requires traversing the tree from root to leaf, involving random disk access if the pages are not in memory.
* **Page Splits/Merges:** When a page becomes full, it splits into two pages, and the median key is promoted to the parent. If a page becomes too empty due to deletions, it merges with a sibling page.

### Buffer Pool Manager
Since random disk access is slow, B+ Tree engines heavily rely on an in-memory **Buffer Pool**. The buffer pool caches frequently accessed disk pages. Eviction policies like LRU (Least Recently Used) or 2Q (Two Queue) manage memory limits.

### Crash Recovery
B+ Trees use a Write-Ahead Log (WAL) to ensure durability and atomicity. The **ARIES protocol** (Algorithm for Recovery and Isolation Exploiting Semantics) is standard. It involves three phases during recovery: Analysis, Redo (replay history to recreate the state at the crash), and Undo (rollback incomplete transactions).

## Production Technology Matrix

| Storage Engine | Architecture | Optimized For | Example Use Cases |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | B+ Tree (Heap + Index) | Read-heavy, complex transactions | Relational data, general purpose OLTP |
| **MySQL (InnoDB)**| B+ Tree (Clustered Index) | Read-heavy, point lookups | E-commerce, user accounts, OLTP |
| **Oracle** | B+ Tree | Complex relational queries | Enterprise systems, financial ledgers |
| **Cassandra** | LSM-Tree (Size-Tiered) | Extreme write throughput | Time-series, IoT, logging, metrics |
| **RocksDB/LevelDB** | LSM-Tree (Leveled) | High write throughput, fast key-value | Embedded KV store, stream state (Flink) |
| **CockroachDB** | LSM-Tree (Pebble/RocksDB) | Distributed SQL | Globally distributed transactional data |

## Interview Scoring Rubric

| Dimension | 1 (Weak) | 3 (Solid) | 5 (Strong) |
| :--- | :--- | :--- | :--- |
| **Core Understanding** | Confuses B-Tree vs LSM-Tree concepts. | Accurately describes B+ Tree in-place updates and LSM append-only designs. | Deeply contrasts write/read/space amplification trade-offs via RUM conjecture. |
| **LSM Mechanics** | Vague on SSTables or MemTables. | Explains WAL, MemTable, Flush, and SSTable structure. | Details Bloom filter mathematics, sparse indexing, and tombstone propagation nuances. |
| **Compaction Strategies** | Does not understand compaction. | Explains why compaction is needed and basic merging. | Articulates STCS vs LCS trade-offs on I/O vs space and the concept of compaction storms. |
| **B+ Tree Mechanics** | Cannot explain tree balancing. | Describes page layout, routing vs leaf nodes, and page splits. | Explains buffer pool (LRU/2Q), sequential I/O limits, and ARIES crash recovery. |
| **Tech Selection** | Picks randomly or based on buzzwords. | Maps B-Tree to read-heavy OLTP and LSM to write-heavy workloads. | Maps underlying storage structures to specific access patterns, accounting for hardware (SSD/HDD). |

## Common Interview Pitfalls

1. **Assuming B-Trees are obsolete.** Many candidates assume LSM-Trees are strictly better. *Mitigation:* Emphasize that B+ Trees remain the gold standard for read-heavy OLTP and predictable latency due to bounded read amplification.
2. **Forgetting the WAL in LSM.** Believing that the MemTable alone is sufficient for writes. *Mitigation:* Explicitly state that the WAL is written *before* the MemTable to guarantee durability in case of a crash.
3. **Misunderstanding Delete in LSM.** Assuming an immediate delete modifies the SSTable. *Mitigation:* Clearly define tombstones and explain that physical deletion is deferred to compaction.
4. **Ignoring Bloom Filters.** Overlooking how LSM-Trees mitigate massive read amplification for non-existent keys. *Mitigation:* Explain that Bloom filters prevent unnecessary disk I/O when searching multiple SSTables.
5. **Over-simplifying B-Tree I/O.** Treating B-Trees as purely memory structures. *Mitigation:* Discuss the Buffer Pool manager and how it mitigates random disk I/O overhead.

## Follow-up Questions

1. **How does an LSM-Tree handle a "read stall" or "write stall"?**
2. **What is a "compaction storm" in an LSM-Tree, and how can it impact a production system?**
3. **How does SSD wear-leveling interact with B+ Tree in-place updates vs LSM-Tree compactions?**
4. **How do B+ Trees and LSM-Trees differ when executing range queries?**
5. **If a key is updated very frequently (e.g., a counter), which storage engine is preferred and why?**