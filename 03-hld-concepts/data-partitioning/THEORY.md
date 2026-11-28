# Data Partitioning

## 📚 Theory

Data partitioning splits a logical dataset into independently stored or processed slices (partitions). Each record belongs to a single logical partition chosen by a partition key, bounding per-node storage, memory, and throughput while enabling parallel reads, writes, and fault isolation.

A logical partition is not always identical to a physical server: one node can host many logical partitions so that ownership can shift incrementally as the cluster grows. Choosing the wrong partition key concentrates traffic on a single slice even when total byte volume is balanced.

### Common strategies

| Strategy | Routing model | Strength | Main risk |
|---|---|---|---|
| Hash | Stable hash of a key maps to a partition | Uniform spread for point lookups | Range scans fan out; modulo changes trigger large reshuffles |
| Range | Ordered contiguous key intervals map to partitions | Efficient range scans and time-based retention | Monotonic keys (e.g., timestamps) create a hot active boundary |
| Directory (lookup) | External mapping table (`key -> partition`) directs requests | Arbitrary placement, tenant isolation, and custom moves | Lookup service becomes a latency hop and availability dependency |
| Composite | Partition key routes to a slice; clustering key orders within it | Combines horizontal spread with local range queries | Poor outer key still skews; overly wide partitions grow unbounded |
| Consistent / rendezvous hash | Membership-aware mapping of keys and nodes to shared space | Bounded key movement (~`1/N`) on topology changes | Solves ownership churn, not single-key traffic popularity |

The code sample in this folder uses a stable CRC32 hash for a small, language-parity example. CRC32 is not a security primitive and is not a universal production shard-key choice; production systems select a hash and repartitioning strategy based on key distribution, membership churn, and threat model.

### Composite keys

A composite key pairs a **partition key** (which selects the slice) with a **clustering or sort key** (which orders rows inside that slice). For example, `(tenant_id, created_at)` routes all writes for one tenant to the same partition while keeping events sorted for fast time-window scans without scatter-gather.

When a single entity can accumulate unbounded history, fold a coarse time bucket into the partition key—such as `(sensor_id, yyyy_mm)`—so each partition stays bounded in size and old buckets can be dropped cheaply.

### Hot keys and skew

Even with hash partitioning, real workloads follow Zipfian distributions: a celebrity user, flash-sale item, or large enterprise tenant can saturate one partition while peers sit idle. Monotonic write keys (auto-increment IDs or raw timestamps) cause similar append-boundary hotspots under range partitioning.

- **Key salting (write bucketing):** Append a bounded random or deterministic suffix (`key#0`..`key#K-1`) to spread writes across `K` partitions, accepting `K`-way fan-out and merge on reads.
- **Dedicated placement:** Move heavy tenants or hot keys to isolated partitions using a directory override or hybrid routing table.
- **Read offloading:** Place local caches, request coalescing (single-flight), and read replicas in front of hot read keys so traffic never hits the primary partition at full rate.
- **Adaptive splitting:** Split an overloaded range partition at its traffic midpoint when sustained QPS or storage crosses a threshold.

### Secondary indexes: local vs global

Primary-key lookups route directly to one partition, but queries on non-key attributes require secondary indexes:

| Index type | Partitioning model | Write path | Read path | Consistency |
|---|---|---|---|---|
| Local (document-partitioned) | Co-located with each data partition | Single partition, fast | Scatter-gather across all partitions; P99 tracks slowest node | Synchronous with base write |
| Global (term-partitioned) | Partitioned by indexed attribute value | Touches multiple partitions (base + index) | Single index partition lookup | Often asynchronous (eventual) to avoid 2PC |

Use local secondary indexes when write throughput dominates and secondary lookups are rare or already scoped by partition key. Use global secondary indexes (or dedicated lookup tables) when low-latency point lookups on a non-primary attribute sit on the critical read path.

### Rebalancing strategies

Moving data when nodes join, leave, or fill up requires a predictable ownership model:

- **Fixed logical partitions:** Pre-allocate far more partitions than initial nodes (for example, 1,024 partitions or 16,384 hash slots) and assign ranges of partitions to each node. Scaling moves whole partitions between nodes without re-hashing keys, though the initial count must accommodate future cluster growth.
- **Dynamic splitting and merging:** Range-partitioned stores automatically split a partition when it exceeds a byte or QPS threshold and merge under-utilized neighbors. Pre-split empty tables when starting from zero to avoid funneling all initial writes onto one node.
- **Consistent hashing with virtual nodes (vnodes):** Assign each physical server many positions on a hash ring so adding or removing a server shifts roughly `1/N` of keys and weighted vnode counts match mixed hardware. See [Consistent Hashing](../consistent-hashing/) for ring math and failure handling.

### Cross-partition queries and transactions

Operations spanning multiple partitions are the main tax of partitioning:

- **Cross-partition queries:** Scatter-gather joins, global `ORDER BY`, and `COUNT` queries amplify tail latency and coordinator memory. Avoid them on the hot path by aligning the partition key with dominant queries, maintaining denormalized read projections, or offloading global analytics to a separate store.
- **Cross-partition transactions:** Atomic multi-partition commits require two-phase commit (2PC), which adds network round-trips and risks coordinator blocking on failures. When strict multi-shard atomicity is unnecessary, prefer single-partition transactions paired with sagas, idempotency keys, and an outbox relay; see [Distributed Transactions](../distributed-transactions/).

## 🎯 When to Use

- Partition when one node or queue can no longer meet storage, write throughput, backup/recovery window, or tenant-isolation targets after indexing, caching, and read replicas are exhausted.
- Keep the partition key aligned with the dominant read/write access path so common requests touch one partition.
- Use range or composite partitions for ordered time windows and retention, while mitigating append-boundary hotspots.
- Use hash-based or consistent-hash placement for even point-lookup distribution, and plan an online resharding path early.

### Strategy decision table

| Workload / access pattern | Recommended strategy | Typical key shape | Main trade-off |
|---|---|---|---|
| Point lookups by entity ID (users, short URLs) | Hash with fixed slots or vnodes | `entity_id` | No ordered cross-key scans |
| Time-series, logs, or retention-window queries | Range or time-bucketed composite | `(source_id, yyyy_mm)` + `ts` | Active bucket needs write-rate sizing |
| Multi-tenant SaaS with varied tenant sizes | Directory / hybrid (dedicated + pooled) | `tenant_id` (plus routing table) | Routing metadata must stay cached and HA |
| User timelines, chat threads, order history | Composite (hash partition + sort key) | `(user_id, created_at)` | Celebrity accounts need salting or split |
| Frequent autoscaling cache or stateless routing | Consistent hashing with vnodes | `cache_key` | Hot keys still need local cache / coalescing |

## 📐 Capacity planning example

Assume 20 million records averaging 1 KiB each: logical data is roughly 20 GB. With three replicas (`RF=3`) and a 25% index and metadata allowance, physical storage is about 75 GB before compression and operational headroom.

At a 15 GB target per partition, five partitions are a storage lower bound; provisioning eight leaves headroom for growth and skew. Independently estimate peak operations per second per partition (for example, 40,000 peak QPS at 5,000 QPS per partition also demands at least eight partitions) and choose the larger count.

## 🏗️ Implementation and operations

[Partitioning Resharding (Mermaid source)](diagrams/partitioning-resharding.mmd)

### Resharding without downtime

Changing partition boundaries or count on a live system follows a phased cutover rather than a stop-the-world dump:

1. **Provision and dual-write (or CDC):** Bring up target partitions and either dual-write from the router or stream changes from the source write-ahead log via CDC. Keep the old partition authoritative.
2. **Throttled backfill:** Copy historical keys in resumable, idempotent chunks using version or timestamp checks so older backfill rows never overwrite newer live writes.
3. **Verify parity:** Run shadow reads and checksum or Merkle-tree comparisons between old and new partitions until mismatch rates reach zero.
4. **Cutover with rollback:** Flip read and write authority at a cutover checkpoint while briefly maintaining reverse sync so you can revert routing immediately if tail latency or error rates spike.

For a deeper step-by-step migration protocol, see [Database Live Re-sharding](../database-live-resharding/).

### Failure modes and operational guardrails

- **Stale routing metadata (correctness):** Routers holding different topology epochs split writes across old and new owners; enforce versioned metadata and reject stale-epoch requests at the storage node.
- **Hidden partition skew (scale):** Cluster-wide averages mask a single saturated partition; alert on per-partition bytes, QPS, P99 latency, replication lag, and throttling.
- **Unthrottled backfill (operations):** Aggressive resharding copies exhaust disk IOPS and starve live traffic; cap backfill bandwidth and validate range boundaries are ordered and non-overlapping (`[start, end)`).
- **Residency or isolation drift (privacy):** Multi-tenant or regional datasets must bind tenant/region rules into the routing layer so rebalancing never moves restricted records across compliance boundaries.

Technology examples include PostgreSQL declarative hash/range table partitioning, Kafka topic partitions, DynamoDB partition + sort keys, Cassandra token rings with vnodes, and Redis Cluster's 16,384 hash slots.

### Interview rubric

| Signal | What it looks like |
|---|---|
| Strong | Sizes partitions by both bytes and QPS, aligns key with dominant queries, separates structural rebalancing from hot-key skew, compares local vs global indexes, and walks through zero-downtime cutover with rollback |
| Weak | Says "hash by ID" without addressing range scans, hot keys, cross-partition queries, or how to resize when traffic grows |

## 🔗 Related Concepts

- [Consistent Hashing](../consistent-hashing/) — Ring placement, virtual nodes, and bounded key movement
- [Database Sharding](../database-sharding/) — Multi-node sharding architecture, routing layers, and shard-key selection
- [Database Live Re-sharding](../database-live-resharding/) — Zero-downtime dual-write, CDC, and cutover phases
- [Database Replication](../database-replication/) — Pairing partitions with replicas for durability and read scale
- [Distributed Transactions](../distributed-transactions/) — 2PC, sagas, and outbox patterns across partitions

## 🔗 Related HLD Projects

- [URL Shortener](../../04-hld-projects/url-shortener/)
- [Chat Service](../../04-hld-projects/chat-service/)
- [News Feed](../../04-hld-projects/news-feed/)
