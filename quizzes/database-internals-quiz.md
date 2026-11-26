# Database Internals Quiz

20 questions focused on database internals, progressing from fundamental concepts to applied trade-offs and architecture.

Time: 25 minutes
Difficulty: Medium-Hard

---

## Section 1: Fundamental Concepts

### Question 1
Which of the following best describes the difference between ACID and BASE properties?

A) ACID requires all data to be stored in memory, while BASE allows data to reside on disk.
B) ACID guarantees strong consistency and immediate durability, while BASE favors availability and eventual consistency.
C) ACID is designed for NoSQL databases, while BASE is designed for traditional relational databases.
D) ACID allows for partial transaction failures, while BASE strictly enforces atomic all-or-nothing operations.

### Question 2
Which ACID property ensures that a transaction is treated as a single, indivisible unit of work that either completely succeeds or completely fails?

A) Durability
B) Isolation
C) Consistency
D) Atomicity

### Question 3
What does the 'Durability' property of ACID guarantee in the event of a sudden power loss?

A) The database will automatically switch to a backup battery power supply to finish pending transactions.
B) All active, uncommitted transactions will automatically resume execution from where they left off.
C) Any transaction that the database has acknowledged as 'committed' will remain permanently saved and intact when the system recovers.
D) The database will never become corrupted, regardless of hardware failure.

### Question 4
In the context of database transactions, what is a 'Dirty Read'?

A) A transaction reads uncommitted changes made by another concurrent transaction, which might subsequently be rolled back.
B) A transaction reads a row that has been intentionally marked for deletion but not yet physically removed.
C) A transaction executes a SELECT statement without holding a lock on the table.
D) A transaction reads data from a cache that has not been flushed to disk in over a minute.

### Question 5
Under the 'Read Committed' isolation level, which phenomenon is prevented?

A) Dirty Reads
B) Write Skew
C) Non-Repeatable Reads
D) Phantom Reads

### Question 6
What is the main consequence of a 'Phantom Read' anomaly?

A) Two concurrent transactions update the same row, resulting in one of the updates being silently lost.
B) A transaction reads uncommitted changes from another transaction that is later rolled back.
C) A transaction executes a range query twice and sees newly inserted or deleted rows in the second result set.
D) A transaction reads a row, another transaction updates that row, and the first transaction reads it again with a new value.

### Question 7
Which isolation level requires a transaction to execute as if it were the only transaction running on the system, preventing all concurrency anomalies?

A) Repeatable Read
B) Serializable
C) Read Uncommitted
D) Snapshot Isolation

### Question 8
What is the difference between a Clustered Index and a Non-Clustered Index?

A) A clustered index stores data across multiple servers, while a non-clustered index is confined to a single server.
B) A clustered index is always a Hash Index, while a non-clustered index is always a B+ Tree.
C) A clustered index is used for numerical data, while a non-clustered index is used for string data.
D) A clustered index determines the physical order of data rows on disk, while a non-clustered index stores a logical ordering that points to the physical rows.

### Question 9
In a B+ Tree, where is the actual data (or pointers to the data records) stored?

A) In a separate Write-Ahead Log outside of the tree structure.
B) Only in the leaf nodes, which are linked together for efficient range queries.
C) In both the internal nodes and the leaf nodes to speed up exact-match lookups.
D) Only in the root node, while the rest of the tree acts as an index.

### Question 10
How does a Write-Ahead Log (WAL) ensure durability in database systems?

A) By continuously backing up the entire database to a secondary server in real-time.
B) By writing all modifications to a sequential log on disk before applying them to the actual database files.
C) By enforcing strict schema validation before any data is allowed into the system.
D) By caching writes in memory and writing them to disk only during system shutdown.


---

## Section 2: Intermediate Architecture & Mechanisms

### Question 11
Why might a columnar storage format be preferred over row-oriented storage for analytical queries?

A) Because it allows the query engine to read and decode only the specific columns needed for the query, saving I/O.
B) Because it completely eliminates the need for database indexing.
C) Because it makes inserting single new records significantly faster and more efficient.
D) Because it naturally prevents SQL injection attacks through strict type checking.

### Question 12
In a row-oriented database, why can a query like 'SELECT sum(salary) FROM employees' be inefficient on a very wide table?

A) Row-oriented databases inherently store numerical data as text, requiring expensive parsing.
B) The database cannot use indexes for aggregate functions like SUM().
C) The database must read entire rows from disk into memory, including many irrelevant columns, causing high I/O bandwidth waste.
D) The query engine must lock the entire table, preventing concurrent inserts during the calculation.

### Question 13
What does Multi Version Concurrency Control primarily achieve in a database?

A) It allows readers to not block writers, and writers to not block readers, by maintaining multiple versions of data.
B) It compresses historical data to save disk space and improve sequential read performance.
C) It synchronizes clocks across distributed database nodes to guarantee global transaction ordering.
D) It automatically partitions a large database table into smaller shards across multiple servers.

### Question 14
In a database using MVCC, how does a transaction know which version of a row it is allowed to read?

A) By querying a centralized lock manager for read permissions before every row access.
B) By acquiring a shared read lock on the row, which blocks writers until the read is complete.
C) By comparing the row's version timestamps (or transaction IDs) with the reading transaction's own start timestamp.
D) By always reading the most recently written version in the Write-Ahead Log.

### Question 15
What is the primary structural difference between a B+ Tree and a Log-Structured Merge (LSM) Tree?

A) B+ Trees update data in-place via disk pages, whereas LSM Trees use sequential append-only writes.
B) B+ Trees store all data in memory, whereas LSM Trees rely exclusively on disk.
C) B+ Trees only support integer keys, whereas LSM Trees support string keys.
D) B+ Trees are optimized for write-heavy workloads, whereas LSM Trees are optimized for read-heavy workloads.

### Question 16
What is the primary role of the MemTable in an LSM-Tree architecture?

A) It acts as an in-memory buffer that absorbs incoming writes, keeping them sorted before they are flushed to disk as SSTables.
B) It is a distributed lock manager that coordinates concurrent access to the LSM-Tree across multiple nodes.
C) It is an implementation of the Write-Ahead Log used strictly for crash recovery.
D) It is a read-only cache that holds the most frequently accessed disk blocks to speed up read queries.

### Question 17
How do LSM-Trees handle data deletions?

A) By immediately seeking to the location of the data on disk and overwriting it with zeroes.
B) By writing a special 'tombstone' marker to the log, which masks the old value during reads until compaction physically removes it.
C) LSM-Trees do not support deletions; data is permanent and can only be appended.
D) By maintaining a separate in-memory hash table of deleted keys that is checked before every read.

### Question 18
What is the purpose of database 'Compaction' in an LSM-Tree?

A) To compress the Write-Ahead Log to save disk space after a successful backup.
B) To aggregate rows into a columnar format for analytical processing.
C) To merge multiple small, immutable SSTables into larger ones, removing deleted or overwritten keys to reclaim space and improve read performance.
D) To rebalance a B+ Tree by merging nodes that have fallen below the minimum occupancy threshold.

### Question 19
Which of the following is true regarding Eventual Consistency?

A) It requires a distributed two phase commit protocol for every write.
B) It is identical to the Serializable isolation level but optimized for cloud environments.
C) It ensures that all nodes will commit a transaction at exactly the same microsecond.
D) If no new updates are made to a given data item, eventually all accesses to that item will return the last updated value.


---

## Section 3: Advanced Applied Trade-offs

### Question 20
In the context of database transaction logging (e.g., ARIES recovery algorithm), what is the specific role of the 'Compensation Log Record' (CLR)?

A) It is written during normal execution to compress multiple redundant updates into a single log entry.
B) It is written during the UNDO phase of crash recovery to record that a specific update has been successfully reversed, preventing the same operation from being undone twice if the system crashes again.
C) It is written during the REDO phase to compensate for data blocks that have been lost or corrupted on disk.
D) It is an administrative log entry used strictly to track failed transaction rollbacks for auditing purposes.

