# Database Internals Answers

### Question 1

1. **B** - ACID guarantees strong consistency and immediate durability, while BASE favors availability and eventual consistency.

**Explanation:** ACID (Atomicity, Consistency, Isolation, Durability) focuses on strong consistency and reliable transaction processing, typical of relational databases. BASE (Basically Available, Soft state, Eventual consistency) focuses on high availability and partition tolerance, accepting that data might be temporarily inconsistent but will eventually converge. BASE is typical of NoSQL distributed systems.

**Distractor breakdowns:**
- **A) ACID requires all data to be stored in memory...**: False. ACID databases rely on durable disk storage for persistence, not just memory.
- **C) ACID is designed for NoSQL...**: Reversed. ACID is standard for traditional relational systems, whereas BASE emerged with NoSQL systems for scale.
- **D) ACID allows for partial transaction failures...**: Reversed. ACID strictly enforces Atomicity (all-or-nothing), preventing partial transaction states.

### Question 2

2. **D** - Atomicity

**Explanation:** Atomicity ensures that a transaction is 'all-or-nothing'. If any part of the transaction fails, the entire transaction fails, and the database state is left unchanged. Consistency ensures the database transitions from one valid state to another. Isolation ensures concurrent transactions don't interfere with each other. Durability ensures committed changes survive failures.

**Distractor breakdowns:**
- **A) Durability**: Ensures committed data is permanently saved, not that the transaction executes indivisibly.
- **B) Isolation**: Governs how concurrent transactions interact and see each other's changes, not execution indivisibility.
- **C) Consistency**: Ensures transitions meet constraints and triggers, not the all-or-nothing execution logic itself.

### Question 3

3. **C** - Any transaction that the database has acknowledged as 'committed' will remain permanently saved and intact when the system recovers.

**Explanation:** Durability guarantees that once a transaction has been committed, its effects are permanent and will survive subsequent system failures (like crashes or power outages). This is typically achieved by ensuring the Write-Ahead Log (WAL) is physically flushed to non-volatile storage (disk) before acknowledging the commit to the client.

**Distractor breakdowns:**
- **A) The database will automatically switch to a backup battery...**: While batteries (like BBU on RAID cards) exist, Durability is a software property guaranteeing data safety upon recovery, not hardware failover.
- **B) All active, uncommitted transactions will automatically resume...**: Uncommitted transactions are rolled back upon recovery, not resumed.
- **D) The database will never become corrupted...**: Durability handles transaction permanence against crashes; it cannot prevent all forms of physical disk corruption.

### Question 4

4. **A** - A transaction reads uncommitted changes made by another concurrent transaction, which might subsequently be rolled back.

**Explanation:** A Dirty Read occurs when a transaction reads data that has been written by another transaction that has not yet committed. If the writing transaction later rolls back, the reading transaction has based its logic on data that technically never existed in the permanent database state. This anomaly is permitted under 'Read Uncommitted' isolation but prevented by 'Read Committed' and higher levels.

**Distractor breakdowns:**
- **B) A transaction reads a row marked for deletion...**: MVCC systems gracefully handle logically deleted rows; this is not a Dirty Read anomaly.
- **C) A transaction executes a SELECT statement without holding a lock...**: Lock-free reads are standard in MVCC and do not constitute a Dirty Read unless uncommitted data is read.
- **D) A transaction reads data from a cache that has not been flushed...**: Reading from a buffer pool before it flushes is standard database operation, not a Dirty Read.

### Question 5

5. **A** - Dirty Reads

**Explanation:** 'Read Committed' is an isolation level that guarantees a transaction only sees data that has been committed by other transactions, thus preventing Dirty Reads. However, it does not prevent Non-Repeatable Reads (where reading the same row twice might yield different results if another transaction commits an update in between) or Phantom Reads.

**Distractor breakdowns:**
- **B) Write Skew**: Requires Serializable isolation to fully prevent; Read Committed does not prevent it.
- **C) Non-Repeatable Reads**: Prevented by the stronger 'Repeatable Read' isolation level, not Read Committed.
- **D) Phantom Reads**: Prevented by 'Serializable' (or Repeatable Read with next-key locks in some systems), not Read Committed.

### Question 6

6. **C** - A transaction executes a range query twice and sees newly inserted or deleted rows in the second result set.

**Explanation:** A Phantom Read occurs when a transaction reads a set of rows satisfying a condition, and a second concurrent transaction inserts, updates, or deletes a row that matches the condition. When the first transaction repeats the query, it sees a 'phantom' row that wasn't there before (or a row is missing). This happens under Repeatable Read in some SQL standards, but is prevented by Serializable.

**Distractor breakdowns:**
- **A) Two concurrent transactions update the same row...**: This is a Lost Update, not a Phantom Read.
- **B) A transaction reads uncommitted changes...**: This is a Dirty Read, not a Phantom Read.
- **D) A transaction reads a row... reads it again with a new value**: This is a Non-Repeatable Read. Phantom reads specifically refer to range queries and row insertions/deletions affecting the set.

### Question 7

7. **B** - Serializable

**Explanation:** Serializable is the highest isolation level. It guarantees that the outcome of executing multiple transactions concurrently is exactly the same as if they were executed serially (one after another) in some order. It prevents all concurrency anomalies, including dirty reads, non-repeatable reads, phantom reads, and write skew.

**Distractor breakdowns:**
- **A) Repeatable Read**: Prevents non-repeatable reads but often still allows phantom reads or write skew.
- **C) Read Uncommitted**: The lowest isolation level, allowing dirty reads and offering minimal protection.
- **D) Snapshot Isolation**: Stronger than Repeatable Read but can still suffer from write skew in some scenarios.

### Question 8

8. **D** - A clustered index determines the physical order of data rows on disk, while a non-clustered index stores a logical ordering that points to the physical rows.

**Explanation:** A Clustered Index dictates the actual physical storage order of the rows in the table; therefore, a table can only have one clustered index (usually the primary key). The leaf nodes of a clustered index contain the actual row data. A Non-Clustered Index contains a sorted list of keys and pointers back to the actual data rows in the clustered index or heap.

**Distractor breakdowns:**
- **A) A clustered index stores data across multiple servers...**: Sharding/partitioning handles cross-server distribution; clustering defines local physical disk order.
- **B) A clustered index is always a Hash Index...**: Most clustered indexes use B+ Trees for range query efficiency.
- **C) A clustered index is used for numerical data...**: Indexes can be built on various data types, regardless of clustering.

### Question 9

9. **B** - Only in the leaf nodes, which are linked together for efficient range queries.

**Explanation:** A key characteristic of a B+ Tree (as opposed to a standard B-Tree) is that all data records or pointers to data records are stored exclusively in the leaf nodes. The internal nodes serve only as routing indexes. The leaf nodes are typically linked in a doubly-linked list, which makes sequential range queries highly efficient.

**Distractor breakdowns:**
- **A) In a separate Write-Ahead Log...**: The WAL ensures durability, it is not the B+ Tree storage structure itself.
- **C) In both the internal nodes and the leaf nodes...**: This describes a standard B-Tree. A B+ Tree specifically restricts data to leaf nodes.
- **D) Only in the root node...**: The root node is small and used for routing, not for storing the entire dataset.

### Question 10

10. **B** - By writing all modifications to a sequential log on disk before applying them to the actual database files.

**Explanation:** A Write-Ahead Log (WAL) ensures durability (the 'D' in ACID) by guaranteeing that the record of a change is flushed to a sequential disk log before the actual database pages are updated in place. If the system crashes, the database can recover by replaying the WAL. 

**Distractor breakdowns:**
- **A) By continuously backing up the entire database...**: Real-time backup replication is a high-availability strategy, while WAL is the low-level primitive for durability.
- **C) By enforcing strict schema validation...**: Schema validation ensures Consistency, not Durability.
- **D) By caching writes in memory and writing them to disk only during system shutdown**: This violates Durability; changes must be logged to disk at commit time, not delayed until shutdown.

### Question 11

11. **A** - Because it allows the query engine to read and decode only the specific columns needed for the query, saving I/O.

**Explanation:** Analytical queries (OLAP) often aggregate data over millions of rows but only access a few columns. Columnar storage groups data by column rather than by row. This allows the query engine to skip reading irrelevant columns from disk, vastly reducing I/O. Furthermore, data in a single column is of the same type, allowing for highly efficient compression.

**Distractor breakdowns:**
- **B) Because it completely eliminates the need for database indexing**: Columnar databases still use indexes, zone maps, or bloom filters to optimize access.
- **C) Because it makes inserting single new records significantly faster**: Columnar storage is generally slower for single-row inserts (OLTP) because the row must be split across multiple column files.
- **D) Because it naturally prevents SQL injection attacks**: Storage layout has no relation to SQL injection prevention, which is handled at the query parsing layer.

### Question 12

12. **C** - The database must read entire rows from disk into memory, including many irrelevant columns, causing high I/O bandwidth waste.

**Explanation:** In a row-oriented storage layout, all attributes of a single record are stored contiguously on disk. To calculate a sum on a single column ('salary'), the storage engine must fetch the entire row (which might contain dozens of other columns) from disk into memory, only to discard most of the data. This wastes significant disk bandwidth.

**Distractor breakdowns:**
- **A) Row-oriented databases inherently store numerical data as text...**: Modern databases store numerics in binary formats regardless of row/column orientation.
- **B) The database cannot use indexes for aggregate functions like SUM()**: Indexes can sometimes cover aggregates, but full table scans are common for analytics, highlighting row-oriented I/O waste.
- **D) The query engine must lock the entire table...**: MVCC avoids table locking for reads, making this incorrect.

### Question 13

13. **A** - It allows readers to not block writers, and writers to not block readers, by maintaining multiple versions of data.

**Explanation:** MVCC is a concurrency control method where the database keeps multiple versions of a row. When a transaction reads data, it sees a snapshot of the database at a specific point in time. This means read operations don't need to acquire locks that block write operations, and write operations don't block read operations, significantly improving concurrent performance.

**Distractor breakdowns:**
- **B) It compresses historical data...**: MVCC preserves older row versions for running transactions, but it does not inherently compress them for storage efficiency.
- **C) It synchronizes clocks across distributed database nodes...**: Distributed clock synchronization (like TrueTime) is separate from local MVCC mechanisms.
- **D) It automatically partitions a large database table...**: This describes sharding, not concurrency control.

### Question 14

14. **C** - By comparing the row's version timestamps (or transaction IDs) with the reading transaction's own start timestamp.

**Explanation:** MVCC assigns transaction IDs or timestamps to transactions and to the row versions they create. A transaction is only allowed to see row versions created by transactions that committed *before* the reading transaction started. It ignores row versions created by transactions that are still active or that started after it. This timestamp/TxID checking eliminates the need for read locks.

**Distractor breakdowns:**
- **A) By querying a centralized lock manager...**: MVCC is designed precisely to avoid asking a lock manager for read permissions.
- **B) By acquiring a shared read lock on the row...**: Lock-based concurrency blocks writers; MVCC uses versions to avoid this.
- **D) By always reading the most recently written version in the Write-Ahead Log**: Reads typically hit memory buffers or data pages, not the append-only WAL.

### Question 15

15. **A** - B+ Trees update data in-place via disk pages, whereas LSM Trees use sequential append-only writes.

**Explanation:** B+ Trees modify data in-place on fixed-size disk pages, which involves random I/O. LSM Trees avoid random I/O by appending data sequentially to logs/memtables, which are later flushed and compacted on disk. This makes LSM Trees superior for write-heavy workloads, while B+ Trees are generally better for read-heavy workloads due to predictable search times.

**Distractor breakdowns:**
- **B) B+ Trees store all data in memory...**: False. Both structures manage data on disk and utilize memory caches.
- **C) B+ Trees only support integer keys...**: False. Both structures support arbitrary comparable key types.
- **D) B+ Trees are optimized for write-heavy workloads...**: Reversed. LSM Trees are optimized for writes (sequential), while B+ Trees are optimized for reads.

### Question 16

16. **A** - It acts as an in-memory buffer that absorbs incoming writes, keeping them sorted before they are flushed to disk as SSTables.

**Explanation:** In an LSM-Tree, writes are first appended to a durable WAL and then inserted into an in-memory structure called the MemTable. The MemTable keeps the keys sorted (often using a balanced tree like a Red-Black tree or Skip List). Once the MemTable reaches a certain size, it is flushed sequentially to disk as an immutable Sorted String Table (SSTable).

**Distractor breakdowns:**
- **B) It is a distributed lock manager...**: The MemTable is a local storage component, not a distributed coordination service.
- **C) It is an implementation of the Write-Ahead Log...**: The WAL is a separate append-only structure for durability; the MemTable organizes data for eventual flushing.
- **D) It is a read-only cache...**: The MemTable primarily absorbs writes; it is actively modified, not read-only.

### Question 17

17. **B** - By writing a special 'tombstone' marker to the log, which masks the old value during reads until compaction physically removes it.

**Explanation:** Because LSM-Trees strictly use sequential appends for performance, they cannot modify or delete data in-place on disk. Instead, a deletion is treated as a write operation that appends a special marker called a 'tombstone'. When a read occurs, the tombstone indicates the key is deleted. Later, during the background compaction process, the tombstone and the original data are merged and physically removed from the disk.

**Distractor breakdowns:**
- **A) By immediately seeking to the location... and overwriting it...**: This in-place update defeats the entire sequential-write purpose of an LSM-Tree.
- **C) LSM-Trees do not support deletions...**: False. LSM-Trees fully support mutable operations via append-only logs and compactions.
- **D) By maintaining a separate in-memory hash table of deleted keys...**: Tombstones are written to the main MemTable and flushed to SSTables, not kept in an isolated in-memory hash table.

### Question 18

18. **C** - To merge multiple small, immutable SSTables into larger ones, removing deleted or overwritten keys to reclaim space and improve read performance.

**Explanation:** Over time, an LSM-Tree generates many SSTables, which slows down reads (as many files must be checked) and wastes disk space (due to duplicate keys or tombstones). Compaction is a background process that reads multiple SSTables, merges them, discards obsolete/deleted keys, and writes out a new, larger, optimized SSTable. It is crucial for maintaining LSM-Tree performance.

**Distractor breakdowns:**
- **A) To compress the Write-Ahead Log...**: The WAL is truncated after MemTables flush, not continuously compressed by compaction.
- **B) To aggregate rows into a columnar format...**: While column-families exist, compaction merges sorted runs, not merely converting row to columnar formats.
- **D) To rebalance a B+ Tree...**: Compaction is an LSM-Tree concept; B+ Trees manage occupancy via page splits and merges during inserts/deletes.

### Question 19

19. **D** - If no new updates are made to a given data item, eventually all accesses to that item will return the last updated value.

**Explanation:** Eventual consistency is a theoretical guarantee that, provided no new updates are made to an object, all replicas will eventually converge to the same value. It allows for temporary inconsistencies (e.g., a read might return stale data immediately after a write) in exchange for higher availability and partition tolerance.

**Distractor breakdowns:**
- **A) It requires a distributed two-phase commit (2PC)...**: Eventual consistency avoids heavy coordination protocols like 2PC to ensure high availability.
- **B) It is identical to the Serializable isolation level...**: Serializable is the strictest consistency level, completely opposite to eventual consistency.
- **C) It guarantees that all nodes will commit a transaction at exactly the same microsecond**: Clock-synchronized commits are related to strict consistency (e.g., Google Spanner), not eventual consistency.

### Question 20

20. **B** - It is written during the UNDO phase of crash recovery to record that a specific update has been successfully reversed, preventing the same operation from being undone twice if the system crashes again.

**Explanation:** In the ARIES recovery algorithm, when a transaction is rolled back (either normally or during crash recovery's UNDO phase), the system writes a Compensation Log Record (CLR) to the Write-Ahead Log. This CLR represents the action of undoing a previous operation. Because CLRs themselves are never undone (they point to the log record *before* the one that was undone), they ensure that the UNDO process is idempotent. If the system crashes in the middle of rolling back a transaction, upon restart, ARIES will REDO the CLR (meaning it will re-apply the rollback action that was already done) and then continue rolling back any remaining operations. This prevents an operation from being undone multiple times.

**Distractor breakdowns:**
- **A) It is written during normal execution to compress...**: Log compression/compaction is not the role of a CLR. CLRs are specifically for logging the reversal of actions.
- **C) It is written during the REDO phase to compensate for...**: The REDO phase re-applies logs to rebuild the state; it does not write CLRs to fix corrupted blocks. CLRs are generated during the UNDO phase (or normal rollback).
- **D) It is an administrative log entry used strictly...**: CLRs are fundamental to the mechanical correctness and idempotence of the recovery algorithm, not just for administrative auditing.

