# Real-Time Gaming Leaderboard - Comparison

## Storage Engine Comparison

When designing a real-time leaderboard, the primary architectural decision is choosing the right data store to handle ranking queries.

| Concern | Relational DB (MySQL/PostgreSQL) | In-Memory Sorted Set (Redis) |
|---|---|---|
| **Data Structure** | B-Tree Index | SkipList + Hash Table |
| **Durability** | High (Disk-backed, ACID compliant) | Low/Medium (Memory-first, async disk snapshots/AOF) |
| **Score Update (Write)** | $O(\log N)$ - Update row and update B-Tree. | $O(\log N)$ - Update SkipList and Hash Table. |
| **Get Top 10 (Read)** | Fast - `ORDER BY score DESC LIMIT 10` leverages the index. | $O(\log N + M)$ - Extremely fast via `ZREVRANGE`. |
| **Get Absolute Rank** | **$O(N)$** - `COUNT(*)` requires a full index scan. Very slow at scale. | **$O(\log N)$** - SkipList allows fast rank traversal via `ZREVRANK`. |
| **Scaling (Write Heavy)** | Harder. Requires complex database sharding. | Easier. High throughput per node (~100k QPS). |
| **Memory Cost** | Low. Relies on cheap disk storage. | High. Entire dataset must fit in expensive RAM. |

## Sharding Strategy Comparison (At 500M+ Scale)

If the dataset exceeds a single Redis node's memory or CPU (QPS) limits, data must be partitioned.

| Dimension | Hash Sharding (`user_id % N`) | Score-Range Sharding (`[0-100]`, `[101-500]`) |
|---|---|---|
| **Write Distribution** | Perfectly uniform. | Prone to hotspots (e.g., most users start at score 0). |
| **Get User Score** | $O(1)$ - Direct hit to the user's specific shard. | $O(1)$ - Direct hit, but requires a secondary mapping of `user_id -> score` to find the correct shard. |
| **Get Top 10** | **Slow** - Scatter-gather query to all $N$ shards, followed by an in-memory sort on the aggregator. | **Fast** - Query only the single highest-score shard. |
| **Get Absolute Rank** | **Very Slow** - Requires calculating the count of users with higher scores across all $N$ shards. | **Fast** - Calculate local rank in the user's shard + $O(1)$ addition of the cached sizes of all higher shards. |

## 🔗 Cross-links
- [Problem Statement](PROBLEM.md)
- [Approach](APPROACH.md)
- [Design](DESIGN.md)
