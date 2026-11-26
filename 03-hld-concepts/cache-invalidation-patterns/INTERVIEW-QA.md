# Cache Invalidation Patterns - Interview Q&A

### 1. How do you mitigate the "Thundering Herd" (Cache Breakdown) problem for a highly concurrent system?
**Answer:** The thundering herd occurs when a popular cache key expires, causing all concurrent requests to bypass the cache and hit the database simultaneously. To mitigate this, I use a **Singleflight or Distributed Mutex Lock**. When a cache miss occurs, the application attempts to acquire a lock for that specific key. Only the thread that acquires the lock queries the database and repopulates the cache. All other threads wait for the lock to be released and then read the newly populated cache. Alternatively, for extreme read-heavy workloads, I use **Logical Expiration**: instead of setting a strict TTL, I embed an `expire_at` timestamp in the payload. If a thread detects the payload is logically expired, it immediately returns the stale data to the user but spawns an asynchronous background thread to fetch fresh data and update the cache.

### 2. What is Cache Penetration and how do you defend against it?
**Answer:** Cache penetration happens when queries are made for keys that do not exist in the database (e.g., malicious scans for invalid user IDs). Because the data isn't in the DB, it's never cached, causing every request to hit the database. 
I defend against this using two layers:
1. **Bloom Filters**: An in-memory Bloom filter stores all valid keys. If the Bloom filter says a key does not exist, the request is immediately rejected.
2. **Null Object Caching**: If a query legitimately bypasses the filter but the DB returns null, I cache a "null" object with a short TTL (e.g., 30 seconds). Subsequent requests hit the cached null and avoid the database.

### 3. How do you prevent a Cache Avalanche during a deployment or unexpected restart?
**Answer:** Cache avalanche occurs when many keys expire simultaneously, overwhelming the database. 
1. **TTL Jitter**: Instead of assigning a fixed TTL (e.g., 1 hour), I add random jitter (e.g., `1 hour + random(0, 10 minutes)`). This spreads expirations smoothly over time.
2. **Staggered Pre-warming**: On restart, a background script pre-loads hot keys into the cache gradually before accepting live traffic.
3. **Multi-tier Caching**: Using an L1 (local memory like Caffeine) and L2 (Redis) cache. If L2 is wiped, L1 still absorbs a significant percentage of reads while L2 recovers.

### 4. Why is "Update Database, then Delete Cache" preferred over "Update Database, then Update Cache"?
**Answer:** Updating the cache directly introduces a race condition. If Thread A and Thread B update the database concurrently, they might write to the database in the order A -> B, but update the cache in the order B -> A due to thread scheduling. The cache now holds older data indefinitely. Deleting the cache is idempotent and forces the next read to fetch the latest state from the database, effectively avoiding this concurrency hazard.

### 5. Even with "Update Database, then Delete Cache", how can a race condition still cause stale data?
**Answer:** A rare anomaly can occur if Thread A reads from the DB (getting an old value), but before Thread A can write it to the cache, Thread B updates the DB and deletes the cache. After Thread B finishes, Thread A resumes and writes its old value to the cache. 
**Mitigation:** This requires the DB write to be faster than the cache write, which is extremely rare. However, setting a short TTL bounds the staleness. For strict consistency, using a distributed lock on the cache key during reads and writes, or using CDC (Change Data Capture) via database binlogs, eliminates the race.

### 6. How do you guarantee cache invalidation if the application crashes immediately after updating the database?
**Answer:** Application-level dual-writes are inherently unreliable. If the app crashes between the DB commit and the cache delete, the cache remains permanently stale.
I solve this using **Change Data Capture (CDC)** (e.g., Debezium). The application only writes to the database. Debezium tails the database binlog/WAL and publishes update events to a Kafka topic. A dedicated consumer reliably reads these events and invalidates the cache. Kafka guarantees delivery, ensuring eventual consistency even if the application crashes.

### 7. How do you handle Redis cluster failover to prevent massive cache misses?
**Answer:** In a Redis Cluster, data is sharded across primary nodes, each with one or more replicas. If a primary fails, Sentinel or the Cluster protocol promotes a replica to primary. 
During the failover window (usually a few seconds), writes to that shard will fail. To mitigate impact:
1. I implement circuit breakers to fast-fail and return degraded responses or hit L1 local cache.
2. I ensure client libraries are configured to auto-discover the new primary topology.
3. I do NOT immediately fallback to querying the DB for all traffic on the failed shard, as that would cause a breakdown. Instead, I rate-limit database fallbacks until the cluster stabilizes.

### 8. In a Multi-Tier Cache setup (L1 Local + L2 Redis), how do you keep the L1 caches consistent across 100 application servers?
**Answer:** When the database changes, the L2 Redis cache is updated/invalidated. But the 100 L1 caches hold stale data until their short TTL expires.
To proactively invalidate L1 caches, I use a **Pub/Sub mechanism** (like Redis Pub/Sub). When the application or CDC updates the DB, it publishes an invalidation message for that key. All 100 servers subscribe to this topic, receive the message, and locally evict the key from their L1 cache.

### 9. What are the trade-offs of Write-Through vs. Write-Behind caching?
**Answer:** 
- **Write-Through**: The application writes to the cache, which synchronously writes to the database. **Trade-off:** High write latency, but ensures strong consistency and no data loss on cache failure.
- **Write-Behind (Write-Back)**: The application writes to the cache, which returns success immediately, and asynchronously flushes batches to the database. **Trade-off:** Extremely high write throughput and low latency, but high risk of data loss if the cache node crashes before flushing to the database. Best for metrics/counters where minor loss is acceptable.

### 10. How do you evaluate whether to cache an object as a serialized JSON string versus an explicit Hash/Object structure in Redis?
**Answer:** 
- **Serialized JSON String**: Best for "read-only" data that is always consumed as a whole (e.g., a full user profile or product page). It's simple, space-efficient, and easy to invalidate entirely.
- **Redis Hash**: Best when I need to atomically update individual fields (e.g., incrementing a "likes" counter on a post without rewriting the entire post payload). Hashes save bandwidth and CPU because I don't have to fetch, deserialize, modify, reserialize, and save the entire object.
