# Sharding and Partitioning Quiz - Answer Key

## Answers


1. **B** - Sharding typically refers to horizontal partitioning across multiple physical machines, while partitioning often refers to logical division within a single database instance.

Explanation: While often used interchangeably informally, strictly speaking, 'partitioning' usually refers to logical separation (e.g., PostgreSQL table partitions on the same disk), whereas 'sharding' implies distributing data across physically separate nodes or clusters.

Distractor breakdowns:
- A: They have subtle technical distinctions.
- C: Both apply to both SQL and NoSQL.
- D: Dividing by columns is vertical partitioning; sharding is horizontal.

2. **A** - Splitting a table by moving certain columns (e.g., large text fields or BLOBs) into a separate table or database.

Explanation: Vertical partitioning splits a schema by columns. A common use case is extracting large, rarely accessed columns (like bios or images) from a frequently accessed table (like user authentication details) to reduce I/O.

Distractor breakdowns:
- B: This is Horizontal Partitioning (Sharding).
- C: This is Vertical Scaling (Scaling Up).
- D: This is a form of Range/Horizontal Partitioning.

3. **C** - It allows for efficient range queries (e.g., fetching all users between ID 1000 and 2000).

Explanation: Range-based sharding groups contiguous keys (like IDs 1-1000) onto the same shard. This allows range queries to hit a single shard rather than scatter-gathering across all shards.

Distractor breakdowns:
- A: A routing tier (or directory) is still needed to know which shard holds which range.
- B: Range sharding is highly susceptible to hot shards if a specific range (e.g., recent timestamps) becomes very active.
- D: Ranges can grow unevenly, requiring periodic rebalancing/splitting.

4. **B** - Range queries become very inefficient as contiguous data is randomly scattered across all shards.

Explanation: Because hash-based sharding uses a hash function to randomly distribute keys, contiguous keys (e.g., adjacent IDs or dates) are unlikely to be on the same shard. A range query must therefore be broadcast to all shards and the results merged.

Distractor breakdowns:
- A: Many SQL databases (like Vitess or Citus) support hash-based sharding.
- C: Point queries (by ID) are highly efficient and hit exactly one shard.
- D: Consistent hashing makes adding shards manageable.

5. **D** - It stores a mapping of which shard holds which specific data key or tenant.

Explanation: Directory-based sharding uses a central lookup table or service to maintain the mapping between a sharding key (like TenantID) and its corresponding physical shard. This decouples the sharding logic from a static algorithm (like hash or range), allowing for flexible, custom placement.

Distractor breakdowns:
- A: Garbage collection is handled by the database engines themselves.
- B: This is a standard cache, not a sharding directory.
- C: Enforcing cross-shard foreign keys is notoriously difficult and usually avoided or handled by application logic.

6. **B** - It minimizes data movement when adding or removing nodes from the cluster.

Explanation: Consistent hashing maps both data keys and node IDs to a circular hash ring. When a node is added or removed, only the data mapped to the immediate adjacent segment of the ring needs to be moved (typically 1/N of the data), rather than rehashing almost all keys.

Distractor breakdowns:
- A: Virtual nodes help with even distribution, but it's never exact.
- C: Hot keys can still occur if many requests hit the same specific key.
- D: Consistent hashing affects data distribution, not necessarily query execution time.

7. **D** - They map a single physical server to multiple points on the hash ring, improving data distribution and load balancing.

Explanation: Virtual nodes map one physical node to multiple random or spaced points on the hash ring. This artificially creates more 'segments', meaning the data load is statistically distributed much more evenly across physical servers, and load from a failing server is distributed across all remaining servers rather than just its immediate neighbor.

Distractor breakdowns:
- A: A hash function is still fundamentally required.
- B: Virtual nodes do not provide encryption.
- C: Virtual nodes are active representations, not standby backups.

8. **B** - A shard that receives a disproportionately high amount of read/write traffic compared to others.

Explanation: A hot shard (or hot spot) occurs when the sharding key causes a large volume of traffic to hit one specific node, overwhelming it while other nodes remain underutilized. This often happens in range sharding with sequential IDs (the latest ID shard gets all new writes) or when a specific key (e.g., a celebrity user) goes viral.

Distractor breakdowns:
- A: This is a 'cold' cache.
- C: Hot refers to traffic heat, not encryption.
- D: This is a network partition or offline node.

9. **B** - The process of moving data between shards to ensure an even distribution of load and storage.

Explanation: As data grows or access patterns change, some shards may become fuller or hotter than others. Rebalancing is the background operational task of migrating chunks of data from overloaded shards to underloaded shards.

Distractor breakdowns:
- A: This is just a reboot.
- C: This is failover/leader election.
- D: This is a schema migration.

10. **A** - The Tenant ID (or Organization ID).

Explanation: In a multi-tenant system, most queries and transactions are scoped to a single tenant. Sharding by Tenant ID ensures that all data for a specific tenant lives on the same shard, allowing for fast, single-shard queries and localized transactions.

Distractor breakdowns:
- B: Sharding by timestamp scatters tenant data and creates write hot-spots.
- C: Sharding by row ID would scatter a single tenant's data across all shards.
- D: A tenant can have many users; grouping by user scatters the tenant data.

11. **D** - A query that does not include the sharding key, forcing the routing tier to send the query to all shards, gather the results, and merge them.

Explanation: If a query lacks the sharding key, the system doesn't know which shard holds the data. It must scatter the query to every single shard, wait for all of them to reply, and gather/aggregate the results. This is highly inefficient.

Distractor breakdowns:
- A: This is database vacuuming or defragmentation.
- B: This is not a recognized caching term.
- C: Clients usually go through a router; they don't guess.

12. **D** - Because the routing tier must fetch (OFFSET + LIMIT) records from *every* shard, sort them all in memory, and then return the top 10.

Explanation: Deep pagination across shards is notoriously expensive. To find items 1000-1010 globally, the aggregator must ask every shard for its top 1010 items, sort them all globally in memory, and then discard everything except the final 10.

Distractor breakdowns:
- A: Distributed engines support it, but it performs poorly.
- B: Shards will return what is requested, which is the problem (too much data).
- C: NTP keeps time reasonably synchronized; the issue is data volume.

13. **C** - They require massive amounts of network bandwidth and scatter-gather processing, leading to high latency.

Explanation: To perform a join across shards, the database coordinator often has to pull large amounts of raw data from multiple shards over the network into memory to perform the join, severely impacting latency and throughput.

Distractor breakdowns:
- A: The SQL standard does not dictate physical deployment topologies.
- B: Joins are read operations; they don't corrupt indexes.
- D: While distributed transactions can deadlock, joins (reads) don't inherently deadlock.

14. **A** - Denormalization (e.g., duplicating related data into a single document or table on the same shard).

Explanation: Denormalization involves intentionally duplicating data so that all data required for a specific query resides on a single shard. For example, storing a user's display name directly inside their 'Orders' record.

Distractor breakdowns:
- B: Range vs. Hash doesn't fix cross-shard joins unless the specific join condition aligns perfectly with the range.
- C: Bloom filters don't help with joining relational data.
- D: While more CPU helps process the join, it doesn't solve the fundamental network bottleneck.

15. **C** - When an extremely popular entity (e.g., a celebrity account) receives massive traffic, creating a hot shard regardless of the sharding strategy.

Explanation: Even with perfect hash distribution, a single key representing a highly active entity (a 'celebrity' with millions of followers) will direct a massive amount of traffic to the single shard hosting that key, overwhelming it.

Distractor breakdowns:
- A: This is a security/RBAC issue.
- B: This is a budgetary issue.
- D: This is a data compliance issue.

16. **A** - By caching the celebrity data heavily and potentially serving it from a CDN or distributed in-memory cache.

Explanation: For read-heavy hot keys, caching is the most effective solution. Serving the popular data from Memcached, Redis, or a CDN prevents the massive read volume from ever hitting the database shard.

Distractor breakdowns:
- B: Write-Through synchronizes writes; it doesn't inherently distribute reads better than async caches.
- C: Slower drives will make the problem worse.
- D: Range sharding won't solve single-key hotspots.

17. **C** - Partitioning data such that records are stored in the physical region closest to the user or where the data is legally required to reside.

Explanation: Geo-partitioning routes data to specific datacenters based on location. This minimizes read/write latency for local users and complies with data residency laws (e.g., GDPR requiring EU data to stay in the EU).

Distractor breakdowns:
- A: This is full geographic replication, not partitioning/sharding.
- B: Encryption strategy is separate from partitioning.
- D: While GPS might be used in GIS apps, geo-partitioning refers to the infrastructure placement.

18. **D** - The application cannot route queries to the correct shards, effectively causing a total cluster outage.

Explanation: The directory service is a critical single point of failure (SPOF) in this architecture. If the routing layer cannot look up which shard holds a tenant, it cannot route the query, causing downtime. Therefore, directories are usually highly available (e.g., using ZooKeeper/etcd).

Distractor breakdowns:
- A: Shards hold data, not routing logic; they don't elect routing directors natively.
- B: It cannot fall back because the data was not distributed via modulo hashing.
- C: Reads also fail because the router doesn't know where to read from.

19. **C** - Two-Phase Commit (2PC).

Explanation: Two-Phase Commit (2PC) is a distributed algorithm that coordinates all shards involved in a transaction. In phase 1, it asks all shards to prepare; in phase 2, if all prepared successfully, it tells all shards to commit. It provides strict consistency but has high performance overhead.

Distractor breakdowns:
- A: Caching doesn't provide transactional guarantees.
- B: Bloom filters optimize lookups.
- D: Consistent Hashing determines data placement.

20. **A** - Take a snapshot and bulk load -> use CDC to apply ongoing changes -> switch application reads/writes when replication lag is near zero.

Explanation: A zero-downtime migration involves taking a snapshot of the old DB, bulk-loading it into the new sharded DB, and using a CDC stream (like Debezium reading the WAL) to replay all changes that occurred since the snapshot. Once the new DB catches up (lag is near zero), the application traffic is cut over.

Distractor breakdowns:
- B: Dual writes are an alternative to CDC but are notoriously complex to make reliable and consistent.
- C: CDC is for ongoing changes; snapshots are for historical baseline data.
- D: This implies significant downtime.

21. **B** - It requires a full redistribution (rehashing) of nearly all existing data across all nodes, causing significant operational overhead and potential downtime.

Explanation: With standard modulo hashing (e.g., hash(key) % N), changing the number of nodes (N) to N+1 changes the result of the modulo operation for almost all keys. Consequently, a vast majority of the data must be moved to new locations (rehashed), which is highly inefficient and the primary reason consistent hashing was developed.

Distractor breakdowns:
- A: Proxies cannot magically map data if the underlying standard hash function outputs different shard destinations.
- C: Sharding architectures rarely "automatically transition" to entirely different paradigms like directory-based sharding simply by adding a node.
- D: Two-phase commit ensures transaction consistency, not data rebalancing or hashing algorithms.

22. **B** - It allows for flexible and dynamic reassignment of specific keys or tenants to different shards without rehashing the entire dataset.

Explanation: Directory-based sharding maintains a lookup table (directory) that maps specific keys or ranges to specific shards. This decoupling allows administrators or automated systems to move data between shards (e.g., to alleviate a hotspot caused by a very active tenant) and simply update the directory entry, which is more flexible than the rigid mathematical distribution of standard hash-based sharding.

Distractor breakdowns:
- A: It actually introduces a lookup mechanism (the directory), which can add latency or become a single point of failure if not cached or distributed properly.
- C: Sharding strategies distribute data; they do not inherently solve replication lag or strict consistency guarantees, which are handled by consensus protocols or replication mechanisms.
- D: This describes standard hash-based sharding (modulo operation), not directory-based sharding, and even hashing does not guarantee prevention of hotspotting if a single key is disproportionately accessed.

23. **B** - To distribute the data of extremely large tenants across multiple shards while keeping queries for specific users localized to a single shard.

Explanation: If a single tenant grows too large for one shard (a "megatenant"), sharding purely by `tenant_id` causes a hot shard or out-of-space error. A composite key like `(tenant_id, user_id)` allows the megatenant's data to be split across multiple shards based on `user_id`, preventing the hotspot while still allowing targeted queries for a specific user to hit a single shard.

Distractor breakdowns:
- A: Composite keys do not inherently enforce storage quotas or limits.
- C: Composite keys do not magically enable native cross-shard joins; those are still inherently network-bound and complex.
- D: A composite key still requires a routing strategy (hash or directory) to find the correct shard; it doesn't eliminate the need for routing.
