# Real-Time Gaming Leaderboard - Approach

## 1. Relational Database vs. Redis Sorted Set

### Approach 1: Relational Database (SQL)
A standard RDBMS like MySQL allows simple incrementing of a score and retrieving the top N players using an `ORDER BY score DESC LIMIT 10` query.
- **Pros:** High durability, well-understood transactional semantics, straightforward to query the top players.
- **Cons:** Determining a specific user's absolute rank requires a query like `SELECT COUNT(*) FROM leaderboard WHERE score > :user_score`. This results in an $O(N)$ full table scan (or index scan), which is prohibitively slow for 25M+ users at a latency target of < 50ms.

### Approach 2: Redis Sorted Set (SkipList + Hash Table)
Redis provides a built-in `Sorted Set` data structure that perfectly matches the leaderboard use case.
- **Data Structure:** Uses a combination of a hash table (for $O(1)$ score lookups by user ID) and a SkipList (for fast $O(\log N)$ rank calculation and range queries).
- **Operations:**
  - `ZINCRBY`: Increments a player's score ($O(\log N)$).
  - `ZREVRANK`: Finds a player's rank ($O(\log N)$).
  - `ZREVRANGE`: Retrieves players within a specific rank window, such as the top 10 ($O(\log N + M)$, where $M$ is the number of elements returned).
- **Pros:** Meets the strict < 50ms latency target. Handles ranking efficiently.
- **Cons:** Redis is an in-memory store. While it offers snapshotting and append-only files (AOF), relying on it as the sole source of truth can be risky.

### Chosen Strategy: Hybrid Model
We will use Redis Sorted Sets as the high-performance read/write layer for real-time leaderboards, backed by an asynchronous pipeline to MySQL. MySQL acts as the durable source of truth. If the Redis cluster fails, the leaderboard can be rebuilt from MySQL.

## 2. Scale and Sizing Analysis

### Memory Estimation (Baseline Scale)
- Players: 25 Million MAU (Monthly Active Users participating in a tournament)
- Data per user:
  - `user_id`: ~24 bytes (string/UUID)
  - `score` (double precision in Redis): 8 bytes
- Base size: 25M * 32 bytes ≈ 800 MB.
- Overhead: Redis Sorted Sets use a SkipList and a Hash Table. The pointer and structural overhead typically multiplies the base size by a factor of ~2.5x.
- **Total Redis RAM Requirement (25M users):** $\approx 2 \text{ GB}$.
- **Conclusion:** A 2GB dataset easily fits into the memory of a single modern Redis node.

### Extreme Scale (500M Users)
- Base size: 500M * 32 bytes ≈ 16 GB.
- Total Redis RAM Requirement (500M users): $\approx 65 \text{ GB}$.
- Write QPS: 250,000 requests per second.
- **Conclusion:** While 65 GB fits in memory on large instances, a single Redis node is bottlenecked at around 100k ops/sec due to its single-threaded nature. Therefore, **sharding is required** at extreme scale.

## 3. Sharding Strategies at Massive Scale

When scaling beyond a single Redis node's CPU capacity (e.g., at 250k QPS), we must shard the data.

### Approach A: Hash Sharding (`user_id % N`)
- **How it works:** Users are distributed evenly across $N$ Redis nodes using a hash of their `user_id`.
- **Pros:** Perfectly balanced write load.
- **Cons:**
  - Finding the global Top 10 requires querying the Top 10 from *all* $N$ nodes (scatter-gather) and merging the results.
  - Finding a single user's rank is highly inefficient. We would need to find their local rank on their shard, and then find how many users have a higher score across all other $N-1$ shards, turning an $O(\log N)$ operation into $O(N \text{ shards} \times \log (\text{keys per shard}))$.

### Approach B: Score-Range Sharding
- **How it works:** Shards are bucketed by score ranges. For example: Shard 1 holds scores [0 - 100], Shard 2 holds [101 - 500], Shard 3 holds [501 - 10,000], etc.
- **Pros:**
  - Finding the Top 10 requires querying only the highest-score shard.
  - Finding a user's absolute rank is fast: compute their rank in their local shard, then add the total size (element count) of all higher-score shards. Because we can maintain a small cache of the element counts per shard, this cross-shard calculation is an $O(1)$ addition.
- **Cons:**
  - Hotspotting on writes. If most users are clustered in a specific score range (e.g., beginners at score 0-10), that shard becomes a bottleneck. We must dynamically split shards or use smaller bucket sizes in dense score ranges.
- **Decision:** Score-Range sharding is the correct approach for leaderboards, as hash sharding fundamentally breaks efficient rank queries.

## 4. Tie-Breaking Implementation

When two users have the exact same score, the system must rank the player who achieved the score *first* higher.
Since Redis Sorted Sets sort identically-scored elements lexicographically by their member string (`user_id`), we must embed the timestamp into the score itself to ensure correct ordering.

**Composite Score Formula:**
`composite_score = score + (1.0 - (timestamp_ms / 1,000,000,000,000))`

*Example:*
- User A scores 100 at time `1600000000000`. Composite: `100 + (1.0 - 1.6) = 99.4` -> Redis requires a slightly different math to ensure strictly monotonic increases or decreases.
- **Better approach for Redis doubles:**
  Use a 64-bit integer, where the higher bits represent the score, and the lower bits represent the inverted timestamp (so earlier times are larger values).
  For double precision in Redis, a simpler method is: `score.timestamp` where timestamp is inverted.
  e.g., `score + (max_time - timestamp) / max_time`.
This ensures that the user who scores first has a slightly higher fractional value, thus breaking the tie.

## 🔗 Cross-links
- [Problem Statement](PROBLEM.md)
- [Design](DESIGN.md)
