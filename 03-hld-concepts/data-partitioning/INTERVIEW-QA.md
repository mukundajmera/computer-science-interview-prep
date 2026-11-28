# Interview Q&A: Data Partitioning

## 1) Why partition at all, and how do you estimate the initial partition count?

**Answer:** Partitioning splits one logical dataset into bounded slices so storage, index memory, write throughput, and recovery times stay within single-node limits while enabling horizontal scale and tenant isolation. To size the initial count, calculate storage-driven and throughput-driven bounds separately: multiply logical bytes by replication factor and index/metadata overhead, divide by your per-partition size target, then divide peak QPS by safe per-partition QPS. Pick the larger count and add headroom (typically 30–50%) for growth and skew.

**Follow-up:** When should you delay partitioning and scale vertically or with read replicas instead?
- *Strong angle:* Delay partitioning while the dataset and write rate fit on a single primary plus read replicas and caching, because partitioning introduces cross-partition query cost, secondary-index trade-offs, and resharding operations.

## 2) How do hash, range, and directory partitioning compare?

**Answer:** Hash partitioning applies a stable hash to the key for uniform point-lookup spread, but breaks key ordering and forces scatter-gather on range scans. Range partitioning assigns contiguous key intervals so range queries and time-based retention stay local, at the risk of hotspots on monotonic keys like timestamps. Directory partitioning uses an explicit lookup table (`key -> partition`) for flexible placement and dedicated shards for large tenants, adding a routing lookup hop and a critical metadata service to keep highly available.

**Follow-up:** How do you keep a directory routing layer from becoming a single point of failure or latency bottleneck?
- *Strong angle:* Cache the routing table in routers/clients with versioned epochs, replicate the backing metadata store with consensus, and refresh lazily on routing-mismatch errors.

## 3) When should you use a composite partition key?

**Answer:** Use a composite key—combining a partition key with a clustering/sort key, such as `(user_id, created_at)`—when your workload needs both horizontal spread across entities and ordered range scans within a single entity. All records for one entity land on the same partition in sorted order, avoiding scatter-gather. If an entity can grow without bound, add a coarse time bucket to the partition key, such as `(sensor_id, yyyy_mm)`, so individual partitions remain bounded and old buckets can be archived cleanly.

**Follow-up:** What happens if a composite key's partition prefix has low cardinality, like `(country_code, event_id)`?
- *Strong angle:* Traffic concentrates on the few largest prefixes (for example, top countries), creating persistent skew; you must either choose a higher-cardinality prefix or split large prefixes via sub-buckets.

## 4) What is a hotspot, and how do you mitigate hot keys and traffic skew?

**Answer:** A hotspot occurs when a single partition receives disproportionate read or write traffic—caused by Zipfian popularity (a viral post or celebrity account), large multi-tenant customers, or monotonic append keys—leading to elevated P99 latency and throttling while other partitions stay under-utilized. Mitigate writes by salting/bucketing hot keys across `K` sub-keys (`key#0..K-1`) or isolating heavy tenants onto dedicated partitions. Mitigate reads with local caching, single-flight request coalescing, and read-replica fan-out.

**Follow-up:** What is the hidden cost of key salting, and how do you limit its blast radius?
- *Strong angle:* Salting turns every read into a `K`-way scatter-gather merge; apply salting selectively only to flagged hot keys (tracked in routing metadata) rather than salting the entire keyspace.

## 5) How do local and global secondary indexes differ in a partitioned store?

**Answer:** A **local (document-partitioned)** secondary index lives alongside each partition and indexes only that partition's rows. Writes are fast and touch one partition, but queries on the indexed field must fan out to all partitions and merge results, so tail latency tracks the slowest partition. A **global (term-partitioned)** secondary index is partitioned by the indexed value itself: reads hit a single index partition, but writes can span multiple partitions and are usually updated asynchronously to avoid distributed transactions, introducing eventual consistency.

**Follow-up:** Which index type would you choose for a low-latency lookup by `email` on a `user_id`-partitioned table?
- *Strong angle:* A global secondary index (or a separate lookup table partitioned by `email`), because point lookups by email happen on the critical login path and cannot afford full-cluster scatter-gather.

## 6) Why is `hash(key) % N` painful to resize, and what rebalancing strategies replace it?

**Answer:** With `hash(key) % N`, changing `N` remaps almost every key (roughly `(N-1)/N`), triggering massive data movement and cache thrash. Production systems replace naive modulo with three main strategies: (1) **fixed logical partitions** (pre-allocating many buckets or slots, such as 16,384 slots, and reassigning whole buckets across nodes), (2) **dynamic range splitting and merging** when partition size or QPS crosses thresholds, or (3) **consistent hashing with virtual nodes**, which moves roughly `1/N` of keys on node add/remove and supports weighted hardware capacity.

**Follow-up:** Does consistent hashing with virtual nodes eliminate hot-key problems?
- *Strong angle:* No—vnodes fix structural ownership imbalance across nodes, not traffic popularity skew on a single key; hot keys still require caching, salting, or dedicated capacity.

## 7) How do you handle cross-partition queries and cross-partition transactions?

**Answer:** Cross-partition queries require scatter-gather across shards, which magnifies P99 latency and coordinator load; minimize them by aligning the partition key with primary access patterns, maintaining denormalized read projections, or shipping data to an analytical store for global aggregations. For cross-partition writes, two-phase commit (2PC) gives atomic commits at the cost of extra round-trips and coordinator-failure blocking; most high-throughput services avoid 2PC on the hot path and use single-partition atomic writes combined with sagas, idempotency keys, and an outbox pattern.

**Follow-up:** How do you prevent duplicate side effects when retrying a saga step across partitions?
- *Strong angle:* Attach a deterministic idempotency key per business operation and store processed keys transactionally in the target partition so retried writes are safe no-ops.

## 8) How do you reshard a live system without downtime?

**Answer:** Execute a phased online migration instead of locking the database: (1) provision target partitions and start dual-writing or streaming source WAL changes via CDC while keeping the old partitions authoritative; (2) run a throttled, resumable backfill using version or timestamp checks so stale historical rows never overwrite newer live writes; (3) validate parity with shadow reads and checksum or Merkle-tree comparisons; (4) cut over read and write authority at a checkpoint while keeping reverse sync active briefly for rapid rollback, then decommission the old partitions.

**Follow-up:** Which metrics tell you to pause or roll back a live resharding cutover?
- *Strong angle:* Rising source or target P99 latency, growing CDC replication lag, shadow-read mismatch counts above zero, or elevated write error/throttling rates on any single partition.

## 9) How does partitioning apply to real-world system designs?

**Answer:** Partitioning choices follow the dominant access path of each system: a [URL Shortener](../../04-hld-projects/url-shortener/) hashes on `short_code` for uniform point lookups; a [Chat Service](../../04-hld-projects/chat-service/) uses a composite key `(channel_id, message_id)` so recent channel messages sit together in order; a [News Feed](../../04-hld-projects/news-feed/) partitions user timelines by `user_id` while handling celebrity fan-out separately to avoid hot-key write amplification. In all cases, per-partition metrics—not cluster averages—drive operational alerting.

**Follow-up:** In a chat service partitioned by `channel_id`, how would you handle a single massive channel with 100,000 active members?
- *Strong angle:* Combine time-bucketed composite keys `(channel_id, day_bucket)` to bound partition size, cache recent messages aggressively at the edge/in-memory tier, and route massive channels onto dedicated partitions if write throughput saturates a shared node.

## Related Concepts

- [Data Partitioning Theory](./THEORY.md)
- [Consistent Hashing](../consistent-hashing/)
- [Database Sharding](../database-sharding/)
- [Database Live Re-sharding](../database-live-resharding/)
- [Distributed Transactions](../distributed-transactions/)
