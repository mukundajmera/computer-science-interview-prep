# Distributed Social Graph Engine - Common Pitfalls

## 1. Naive Look-Aside Caching (Connection Explosion & Thundering Herd)

**Signal:** The candidate places a standard Redis/Memcached cluster between the web servers and the databases, where web servers directly query caches, and on a miss, directly query databases.
**Root Cause:** Failure to account for the massive scale of web servers and the impact of a hot-key cache eviction.
**Mitigation:** Introduce a Two-Tier Cache hierarchy. A "Leader" cache tier acts as a reverse proxy to the DB. It receives all cache misses from the "Follower" caches, and if 10,000 requests arrive for the same missing key simultaneously, the Leader collapses them into a single DB query. Furthermore, only Leaders connect to the DB, preventing connection pool exhaustion.
**Validation/Monitoring:** Monitor DB connections per shard and concurrent identical queries hitting the DB.

## 2. Distributed Transactions for Edge Creation

**Signal:** To create a mutual friendship, the candidate proposes a 2-Phase Commit (2PC) or strict distributed transaction to ensure both `(A, FRIEND, B)` and `(B, FRIEND, A)` are written atomically across two different database shards.
**Root Cause:** Prioritizing strict ACID consistency over availability and write throughput in a highly distributed system.
**Mitigation:** Accept eventual consistency. Write the two directed edges independently as separate operations. If one succeeds and the other fails, a background reconciliation process or asynchronous retry queue handles the failure. High write availability is far more critical than strict atomic mutual friendship creation.
**Validation/Monitoring:** Monitor write latencies and the backlog of the retry queue for failed secondary edge writes.

## 3. Synchronous Cache Invalidation Across Regions

**Signal:** On a write, the candidate designs the system such that the web server or DB master actively reaches out to all cache nodes in all global regions to delete the key before returning success to the user.
**Root Cause:** Misunderstanding the impact of cross-region network latency on the write path.
**Mitigation:** Decouple invalidation from the write path. Use asynchronous replication. The write succeeds once it hits the local cache and local DB (or forwarded master DB). A background process (like Wormhole) tails the database binlog and asynchronously broadcasts cache invalidation messages to other regions.
**Validation/Monitoring:** Monitor the replication lag of the invalidation bus (Time taken from DB write commit to cache invalidation receipt in a remote region).

## 4. The Celebrity Supernode Hotspot

**Signal:** The candidate shards the database and cache strictly by `id1` (the origin node). They fail to identify what happens when `id1` is Lady Gaga, who has 50 million followers.
**Root Cause:** Ignoring data skew and degree distribution in social graphs. A single shard will be overwhelmed by writes (new followers) and reads (fetching the follower list).
**Mitigation:** Implement virtual bucket sharding (edge partitioning) for supernodes. Instead of storing the entire association list on `hash(id1) % K`, partition the list across $M$ buckets using `hash(id1, id2) % M`.
**Validation/Monitoring:** Monitor CPU and IOPS utilization per shard. Look for massive deviations from the mean, indicating a hotspot.

## 5. Ignoring Temporal Locality

**Signal:** The candidate caches the *entire* association list for every object, or caches a random subset of edges.
**Root Cause:** Missing the product reality that social networks are heavily biased toward recency (people look at recent posts, recent likes, recent comments).
**Mitigation:** Cache only the most recent $N$ edges for an association list (ordered by timestamp). If a client requests older edges (pagination), the system allows a cache miss and queries the database via the Leader cache.
**Validation/Monitoring:** Monitor cache hit ratios specifically for paginated graph queries versus initial page load queries.