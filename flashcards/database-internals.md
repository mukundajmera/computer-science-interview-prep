# Database Internals Flashcards

40 question-only flashcards for database internals.

---

## Storage Engine Fundamentals (8 Cards)

### Card 1
Front: What is the primary role of a Write-Ahead Log (WAL) in database storage engines?

### Card 2
Front: How does in-place updating differ from append-only storage mechanisms?

### Card 3
Front: Why is flushing data to disk sequentially generally preferred over random writes?

### Card 4
Front: What happens during crash recovery when reading the WAL?

### Card 5
Front: How do database engines balance read amplification, write amplification, and space amplification?

### Card 6
Front: What is the purpose of a buffer pool or page cache in a database storage engine?

### Card 7
Front: How does a storage engine guarantee that a transaction is durable once committed?

### Card 8
Front: What are the trade-offs of using direct I/O versus relying on the OS page cache?

## Indexing and B-Trees (8 Cards)

### Card 9
Front: Why are B+Trees the standard data structure for relational database storage?

### Card 10
Front: How does a B+Tree differ from a standard binary search tree for disk-based storage?

### Card 11
Front: What happens when a B+Tree node becomes full and needs to accept a new insert?

### Card 12
Front: Why do B+Trees maintain pointers between leaf nodes?

### Card 13
Front: How does page size affect B+Tree depth and read performance?

### Card 14
Front: What is index fragmentation and how do database engines resolve it?

### Card 15
Front: How do secondary indexes reference the actual data in a heap file or clustered index?

### Card 16
Front: What is a covering index and why does it improve read latency?

## LSM-Trees and Write Paths (8 Cards)

### Card 17
Front: What is an SSTable (Sorted String Table) and what are its key properties?

### Card 18
Front: How does an LSM-Tree process incoming write operations using a MemTable?

### Card 19
Front: Why do LSM-Trees typically offer higher write throughput than B+Trees?

### Card 20
Front: What is the role of a Bloom filter in an LSM-Tree read path?

### Card 21
Front: Why is compaction necessary in an LSM-Tree storage engine?

### Card 22
Front: How does Size-Tiered compaction differ from Leveled compaction?

### Card 23
Front: What is tombstoning and how do LSM-Trees handle deletions?

### Card 24
Front: How does an LSM-Tree execute a point read for a specific key?

## Transactions and Concurrency Control (8 Cards)

### Card 25
Front: What is the difference between optimistic and pessimistic concurrency control?

### Card 26
Front: How does Two-Phase Locking (2PL) prevent serializability anomalies?

### Card 27
Front: What is a deadlock in the context of database transactions and how is it resolved?

### Card 28
Front: How does Multi-Version Concurrency Control (MVCC) allow readers and writers to avoid blocking each other?

### Card 29
Front: In MVCC, how does the database determine which version of a row a transaction is allowed to see?

### Card 30
Front: What is the role of the transaction ID in managing row visibility?

### Card 31
Front: Why do databases using MVCC require a vacuum or garbage collection process?

### Card 32
Front: How does a database implement atomic commits for multi-statement transactions?

## Isolation Levels and Anomalies (8 Cards)

### Card 33
Front: What is a Dirty Read and which isolation level is required to prevent it?

### Card 34
Front: How does a Non-Repeatable Read differ from a Phantom Read?

### Card 35
Front: Which transaction isolation level is generally used to prevent Phantom Reads?

### Card 36
Front: What is the Lost Update anomaly and how can databases prevent it?

### Card 37
Front: How does Snapshot Isolation differ from Strict Serializability?

### Card 38
Front: What is Write Skew and under which isolation levels can it occur?

### Card 39
Front: Why do many popular relational databases default to Read Committed instead of Serializable?

### Card 40
Front: How does a developer use explicit locking (like SELECT FOR UPDATE) to strengthen isolation guarantees?

