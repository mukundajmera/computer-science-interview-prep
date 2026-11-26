# Data Partitioning

## 📚 Theory

Data partitioning splits a logical dataset into independently stored or processed slices. It can bound per-node storage and throughput, isolate tenants, and allow parallel work. A partition key determines where each record and request is routed; a poor key can concentrate traffic even when the total data is well distributed.

### Common strategies

| Strategy | Routing model | Strength | Main risk |
|---|---|---|---|
| Hash | Stable hash of a key maps to a partition | Spreads unordered keys | Range scans fan out; modulo changes can trigger large reshuffles |
| Range | Ordered key intervals map to partitions | Local range scans and retention windows | Monotonic keys can create a hot newest partition |
| Composite | One dimension narrows the range, another spreads within it | Balances locality and write distribution | More routing and query complexity |
| Consistent/rendezvous hash | Stable membership-aware mapping to owners | Reduces movement when membership changes | Hot keys still need explicit splitting or replication |

The code sample uses a stable CRC32 hash for a small, language-parity example. CRC32 is not a security primitive and is not a universal production shard-key choice; production systems should select a hash and repartitioning strategy based on key distribution, membership changes, and threat model.

## 🎯 When to Use

- Partition when one node or queue cannot meet the required storage, throughput, isolation, or recovery target.
- Keep the partition key aligned with the dominant read/write access path; avoid scatter-gather for common queries.
- Use range partitions for ordered time windows and retention, while accounting for write hotspots at the active boundary.
- Use hash-based placement for even key distribution, but plan for resharding, virtual nodes, or a stable membership-aware scheme.

## 📐 Capacity planning example

Assume 20 million records averaging 1 KiB each: the logical data is about 20 GB. With three replicas and a rough 25% index/metadata allowance, physical storage is approximately 75 GB before compression and operational headroom. At a 15 GB target per shard, five shards are a storage lower bound; provision more (for example, eight) to leave growth and skew headroom. Independently estimate peak operations per second per shard and use the larger shard count. These assumptions are illustrative; production sizing needs measured record sizes, index amplification, replication, and hot-key distributions.

## 🏗️ Implementation and operations

![Partitioning Resharding](diagrams/partitioning-resharding.mmd)

- Validate that range boundaries are ordered, non-overlapping, and have a defined inclusive/exclusive convention.
- Track per-partition bytes, request rate, latency, queue depth, and throttling; averages hide hot partitions.
- Rebalance with a resumable copy, dual-read/write or shadow verification phase, cutover checkpoint, and rollback plan.
- Treat cross-partition transactions and queries as explicit cost/consistency trade-offs.

Technology examples include PostgreSQL hash/range table partitioning, Kafka topic partitions, DynamoDB partition keys, Cassandra token ranges, and consistent-hash rings. Their exact semantics differ; a logical partition is not necessarily the same thing as a physical server.

## 🔗 Related HLD Projects

- [URL Shortener](../../04-hld-projects/url-shortener/)
- [Chat Service](../../04-hld-projects/chat-service/)
- [News Feed](../../04-hld-projects/news-feed/)
