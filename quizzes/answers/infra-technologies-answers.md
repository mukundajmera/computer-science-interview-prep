# Infrastructure Technologies Quiz - Answer Key

## Answers

1. **D**
2. **D**
3. **C**
4. **C**
5. **B**
6. **A**
7. **C**
8. **A**
9. **A**
10. **A**
11. **A**
12. **B**
13. **C**
14. **C**
15. **B**
16. **D**
17. **A**
18. **C**
19. **B**
20. **A**
21. **D**
22. **A**
23. **D**
24. **B**
25. **B**
26. **C**
27. **B**
28. **B**
29. **D**
30. **D**

---

## Explanations

1. **D** - Explanation: DynamoDB is a NoSQL database that requires you to know your access patterns beforehand to design partition and sort keys effectively. Relational databases allow flexible querying later, but DynamoDB's performance relies heavily on optimizing for specific reads and writes up front, making "Listing top access patterns" crucial. Choosing capacity defaults or creating GSIs prematurely ignores the data modeling needed.

2. **D** - Explanation: A good partition key must distribute traffic evenly across underlying physical partitions to prevent hot spots (which lead to throttling). It must also match your primary key lookups to fulfill access patterns efficiently. A low-cardinality key (like status) or a timestamp-only key typically causes severe hot partitions.

3. **C** - Explanation: Querying with key conditions directly targets a specific partition and optionally a range, making it highly efficient and predictable for hot paths. Scans evaluate every item in a table (or index), consuming significant read capacity and time, making them unsuited for high-throughput, low-latency critical paths.

4. **C** - Explanation: A Local Secondary Index (LSI) uses the exact same partition key as the base table but a different sort key, and it must be created when the table is created. A Global Secondary Index (GSI) can use any attributes for its partition and sort keys and can be created or deleted at any time.

5. **B** - Explanation: Hot partitions occur when a single partition key receives disproportionate read or write traffic. The most robust fix is improving key design—such as adding write sharding (appending random suffixes) or changing the partition key—to spread traffic more uniformly.

6. **A** - Explanation: PostgreSQL is a powerful relational database designed for ACID transactions, relational integrity (foreign keys, constraints), and complex SQL queries. While it supports key-value and schema-less data (like JSONB), its primary strength lies in structured relational data, whereas NoSQL is usually better for pure key-value scaling.

7. **C** - Explanation: Replica lag is the time delay between a write committing on the primary node and that same write being applied to a read replica. Consequently, clients reading from the replica might receive stale data (read freshness). It does not impact the primary's write durability if synchronous replication is not strictly enforced.

8. **A** - Explanation: B-trees are balanced tree structures optimized for disk-based storage, making them highly efficient for exact equality lookups, range queries (e.g., > or <), and sorting operations. They are not suitable for fuzzy vector search (which requires ANN indexes) or deep JSONB containment (which uses GIN).

9. **A** - Explanation: Sharding adds massive operational complexity (cross-shard joins, distributed transactions). Therefore, one should first exhaust vertical scaling and standard optimizations: tuning queries, adding proper indexes, utilizing connection pooling (like PgBouncer), and offloading read traffic to replicas.

10. **A** - Explanation: To guarantee strong consistency (read-after-write), a client must read from the primary node where the write just occurred. Reading from a replica risks hitting stale data due to asynchronous replication lag, and caches might not yet be invalidated or updated.

11. **A** - Explanation: Watermarks are a core Flink mechanism used to track the progress of event time. They signal to the system that no more events with a timestamp older than the watermark should arrive, allowing windows to close and state to be emitted accurately despite out-of-order data.

12. **B** - Explanation: Achieving true end-to-end exactly-once semantics requires the data source to be replayable (like Kafka), the processing framework to checkpoint state accurately, and the sink to either support idempotent writes or participate in a two-phase commit protocol.

13. **C** - Explanation: When real-time latency is not required, batch pipelines (using tools like Spark or Airflow) are usually cheaper, simpler to reason about, and easier to operate than continuous 24/7 stateful streaming engines.

14. **C** - Explanation: Streaming applications must explicitly define how to handle late-arriving events. Frameworks like Flink allow setting an "allowed lateness" threshold to tolerate slightly delayed records and define side outputs or update strategies for extremely late data, ensuring accuracy without dropping records silently.

15. **B** - Explanation: Backpressure occurs when a downstream operator or sink cannot process data as fast as the upstream source produces it. The system intentionally slows down upstream consumers to prevent out-of-memory crashes, making it a clear symptom of a downstream bottleneck.

16. **D** - Explanation: Apache ZooKeeper provides highly reliable distributed coordination services, such as leader election, distributed locking, configuration management, and group membership. It is not designed for heavy data storage like an object store or OLAP engine.

17. **A** - Explanation: Ephemeral znodes in ZooKeeper exist only as long as the session of the client that created them remains active. If the client crashes or loses connectivity, the znode is automatically deleted. This mechanism is perfect for tracking live nodes or maintaining distributed locks.

18. **C** - Explanation: Time-Series Databases (TSDBs) partition data into time chunks. This allows queries targeting specific timeframes to quickly prune irrelevant partitions. It also makes data retention policies cheap, as entire old chunks can be dropped from disk sequentially rather than deleting individual rows.

19. **B** - Explanation: In a TSDB, cardinality refers to the total number of unique time series, which is usually the cross product of all metric names and their tag/label values. High cardinality can severely degrade TSDB performance and cause massive memory usage during indexing.

20. **A** - Explanation: A Bloom filter is a space-efficient probabilistic data structure used to test whether an element is a member of a set. It can definitively answer "no" (the item is definitely not in the set), preventing expensive disk lookups, but a "yes" might be a false positive.

21. **D** - Explanation: Hierarchical Navigable Small World (HNSW) graphs provide an excellent trade-off between query latency and recall accuracy for Approximate Nearest Neighbor (ANN) vector search. While it consumes significant memory to store the graph structures, its search speed is state-of-the-art.

22. **A** - Explanation: Inverted File (IVF) indexes cluster vectors into Voronoi cells. At query time, it only searches the closest clusters. This allows practitioners to tune latency versus recall by adjusting how many clusters to search (nprobe), trading off exhaustive search accuracy for speed.

23. **D** - Explanation: Access Control Lists (ACLs) must be securely enforced on the backend during the retrieval phase to prevent users from accessing unauthorized documents. Relying on frontend enforcement is easily bypassed and a major security vulnerability.

24. **B** - Explanation: For very small vector datasets, computing exact distance (brute-force k-NN) in memory is extremely fast and guarantees 100% recall. Complex ANN structures like HNSW add unnecessary overhead and indexing time for small collections.

25. **B** - Explanation: HyperLogLog (HLL) is a probabilistic algorithm used to estimate the cardinality (number of distinct elements) of massive datasets using very little memory. It cannot provide exact counts or track the frequency of individual items.

26. **C** - Explanation: Count-Min Sketch is a probabilistic data structure that serves as a frequency table of events in a stream of data. It provides approximate counts (with bounded errors) using sub-linear space, which is ideal for heavy hitter tracking over high-volume streams.

27. **B** - Explanation: Senior engineers recognize that specialized databases introduce operational overhead. You should adopt a TSDB only when standard relational or NoSQL databases can no longer cost-effectively handle the high ingest rates or specific time-window aggregations required by the workload.

28. **B** - Explanation: Migrating search or vector indexes carries risk of recall degradation or latency spikes. A safe pattern involves running both indexes, shadowing live traffic to compare results (without impacting users), and carefully cutting over in stages to monitor for regressions.

29. **D** - Explanation: Embedding models inevitably evolve, meaning old vectors become incompatible with new queries. Failing to design a pipeline for bulk re-indexing and versioning forces downtime or degrades search quality drastically when the model is updated.

30. **D** - Explanation: A strong architectural design proposal not only presents the chosen topology but explicitly outlines its core trade-offs and defines the metrics or scale triggers that would mandate re-evaluating the architecture in the future.
