# Caching Strategies Answers

### Question 1
**Answer:** C
**Explanation:** Cache-aside is generally the safest default pattern for interviews because it decouples the caching layer from the database layer, allowing the application to read from the cache and write directly to the primary datastore as the source-of-truth.
**Distractor breakdowns:**
- *A (Write-through):* Requires tight coupling and custom failure logic to ensure the synchronous write to both cache and DB doesn't fail partially.
- *B (Write-behind):* Shifts the source-of-truth temporarily to the cache, introducing severe data loss risks if the cache crashes before the async flush to DB.
- *D (Read-through):* Requires the cache provider to understand how to fetch from the specific database schema, which adds unnecessary architectural complexity.

### Question 2
**Answer:** D
**Explanation:** Source-of-truth fields like price and inventory determine financial transactions and order fulfillment. They have strict correctness requirements and cannot rely on long TTLs (Time-To-Live) that allow stale data.
**Distractor breakdowns:**
- *A (Product metadata):* Descriptions and images change rarely and won't break a purchase flow if slightly stale.
- *B (Hints and layouts):* Purely presentational data has a very high tolerance for staleness.
- *C (Historical analytics):* By definition, these are backward-looking and often calculated in batch, so long TTLs are expected.

### Question 3
**Answer:** B
**Explanation:** When a large batch of popular keys (like homepage data or top-10 lists) expire at the exact same moment, all incoming requests will simultaneously miss the cache and hit the backend database. This is known as a cache stampede or thundering herd.
**Distractor breakdowns:**
- *A (Memory usage):* Expiring keys reduces memory usage; it doesn't increase it.
- *C (Read-through mode):* TTL expiration does not change the caching architecture or pattern (e.g., from cache-aside to read-through).
- *D (Consistent hashing):* Expiry is a data lifecycle event and has absolutely no impact on the cluster's consistent hashing ring or slot assignment.

### Question 4
**Answer:** C
**Explanation:** LRU (Least Recently Used) is the most common and robust default for general caching because it perfectly aligns with temporal locality: data accessed recently is highly likely to be accessed again soon.
**Distractor breakdowns:**
- *A (LFU):* Without decay mechanisms, LFU can be polluted by historically popular items that are no longer accessed, preventing new hot items from being cached.
- *B (Random):* Random eviction is non-deterministic and can easily evict the hottest keys in the system, degrading the hit ratio.
- *D (LIFO):* LIFO evicts the newest items first, which actively fights against the principle of temporal locality.

### Question 5
**Answer:** C
**Explanation:** In Redis, the LFU counter is an approximation. To prevent a key that was queried a million times yesterday from staying in the cache forever (even if it's never queried today), a background decay mechanic periodically halves or decreases the counter based on idle time.
**Distractor breakdowns:**
- *A (fsync):* The `fsync` process is related to persisting data to disk (AOF), not memory eviction policies.
- *B (Morris counter):* While Redis uses an approximate counter to save space, the counter itself doesn't solve the problem of historical dominance without the decay function.
- *D (allkeys-random):* Setting the policy to random explicitly disables LFU logic entirely.

### Question 6
**Answer:** B
**Explanation:** Redis Cluster intentionally avoids a standard consistent hashing ring. Instead, it statically partitions the keyspace into exactly 16,384 hash slots, mapping keys to slots using `CRC16(key) mod 16384`. Nodes are assigned a subset of these slots.
**Distractor breakdowns:**
- *A (Consistent hashing ring):* While common in other systems (like Cassandra or Memcached clients), Redis Cluster explicitly chose slots to simplify resharding and explicit node assignment.
- *C (External coordinator):* Redis Cluster uses a peer-to-peer gossip protocol for state coordination, specifically avoiding external dependencies like Zookeeper.
- *D (Alphabetically):* Keys are hashed to ensure uniform distribution, not sorted alphabetically which would cause severe hotspots.

### Question 7
**Answer:** C
**Explanation:** Write-behind (also called write-back) acknowledges writes instantly at the cache tier and queues them for asynchronous flushing to the database. This maximizes write throughput but sacrifices immediate durability, making it ideal for event pipelines where some data loss on crash is acceptable.
**Distractor breakdowns:**
- *A (Cache-aside):* Primarily a read-optimization pattern; writes still block on the primary database.
- *B (Write-through):* Prioritizes immediate durability by synchronously writing to both tiers, which limits write throughput to the database's speed.
- *D (Stale-while-revalidate):* A read-side pattern (common in CDNs) that serves stale data while fetching fresh data in the background; it does not handle high-volume write pipelines.

### Question 8
**Answer:** B
**Explanation:** Changing the global eviction policy to `allkeys-lru` only dictates what happens when the cache is full. It does absolutely nothing to reduce the network or CPU load on the single shard that is currently being overwhelmed by requests for a specific hot key.
**Distractor breakdowns:**
- *A (Replicating/bucketing):* Creating keys like `hotkey:1`, `hotkey:2` spreads the read load across multiple shards effectively.
- *C (In-process cache):* Adding a local Guava/Caffeine cache in the application servers completely shields the Redis shard from the read traffic.
- *D (Rate-limiting):* Shedding load is a valid defensive mechanism if the traffic is abusive or non-critical.

### Question 9
**Answer:** C
**Explanation:** Prior to Redis 7, rewriting the Append Only File (AOF) required heavy fork operations and merging large files, causing massive memory and I/O spikes. Redis 7 introduced a Multi-part AOF (base + increments) that trivially merges files without heavy fork overhead.
**Distractor breakdowns:**
- *A (Zero data loss):* AOF still relies on `fsync` policies (like `everysec`); it cannot guarantee absolute zero data loss if a crash occurs between syncs.
- *B (Automatic clustering):* AOF is strictly a persistence mechanism for single nodes; it has no relationship to clustering or hash slots.
- *D (Infinite memory swapping):* Redis is an in-memory store; AOF is for durability recovery on restart, not for swapping active memory pages to disk like virtual memory.

### Question 10
**Answer:** B
**Explanation:** In a standard cache-aside setup, the most consistent approach is to write the update to the primary database first, wait for success, and then explicitly issue a `DEL` (invalidate) command to the cache key.
**Distractor breakdowns:**
- *A (Write cache first):* If the subsequent database write fails, the cache holds permanent phantom data that doesn't exist in the source-of-truth.
- *C (Wait for TTL):* Leaves stale data visible to users for the duration of the TTL, violating read-your-writes consistency.
- *D (Nightly batch):* This is a complete anti-pattern for transactional data, ensuring the cache is stale for up to 24 hours.

### Question 11
**Answer:** C
**Explanation:** A complete cache outage means 100% of traffic falls through to the database. To prevent the database from instantly collapsing under the unmitigated load, the application must employ circuit breakers, strict admission control, or serve degraded responses (e.g., hiding recommendations).
**Distractor breakdowns:**
- *A (Long-polling):* Holding connections open while waiting for cache recovery will rapidly exhaust all available threads and connections, causing a complete system halt.
- *B (Replicate to CDN):* A CDN cannot instantly replicate or serve dynamic backend data that it hasn't already cached, especially if the primary cache is dead.
- *D (Automatically upgrade DB):* Vertically scaling a relational database takes minutes to hours and requires downtime; it is impossible to do automatically during an active traffic spike.

### Question 12
**Answer:** D
**Explanation:** The hit ratio measures the percentage of requests served directly from the cache. This directly correlates to the backend offload percentage, proving mathematically how many requests the database was spared from processing.
**Distractor breakdowns:**
- *A (Eviction rate):* High evictions just mean the cache is full and thrashing; it doesn't indicate if the requests it did serve were useful.
- *B (Size of objects):* Caching large objects saves bandwidth, but caching many small, highly requested objects often shields the database CPU much more effectively.
- *C (Network bandwidth):* High bandwidth usage could just mean the cache is returning a few massive payloads, not necessarily shielding the database from high query volume.

### Question 13
**Answer:** B
**Explanation:** Caching introduces significant complexity (invalidation logic, stale data risks). If an endpoint has low read reuse (e.g., highly personalized or volatile data), the cache will constantly miss or require invalidation. The architectural cost vastly outweighs any minor latency gains.
**Distractor breakdowns:**
- *A (Same TTL):* Endpoints can and should have wildly different TTLs based on their freshness requirements.
- *C (Impossible to configure):* Cache clusters can easily store billions of keys representing thousands of different endpoints; scale is not the limiting factor.
- *D (CPU usage):* Caching typically decreases application CPU usage by skipping heavy serialization or computation logic.

### Question 14
**Answer:** C
**Explanation:** By default, Redis Cluster hashes the entire key. Hash tags (using `{}`) instruct the hashing algorithm to only consider the substring inside the braces. This guarantees that keys like `{user:123}.profile` and `{user:123}.settings` hash to the exact same slot, enabling atomic multi-key operations (like Lua scripts or `MGET`) on them.
**Distractor breakdowns:**
- *A (Compress key name):* Curly braces add characters; they do not perform any memory compression.
- *B (Enforce TTL):* Hash tags dictate node placement, not expiry logic. TTL must be set per key regardless of tags.
- *D (Encrypt data):* Redis does not automatically encrypt data based on key naming conventions.

### Question 15
**Answer:** B
**Explanation:** The `fsync` configuration (options like `always`, `everysec`, or `no`) dictates how frequently Redis forces the OS kernel to flush the AOF buffer to physical disk, explicitly trading off maximum write performance against the risk of data loss during a crash.
**Distractor breakdowns:**
- *A (Eviction algorithm):* Eviction is controlled by the `maxmemory-policy` setting, entirely unrelated to disk persistence.
- *C (Number of replicas):* Replication consensus is controlled by commands like `WAIT`, not the local disk `fsync` policy.
- *D (TTL config):* TTL is set per-key via commands like `EXPIRE`; `fsync` handles the durability of the transaction log.

### Question 16
**Answer:** B
**Explanation:** When a slot is migrating, the source node still holds some keys and the target holds others. If the source doesn't have the key, it returns an `ASK` redirection. This tells the client "I don't have it, go ask the target node just for this specific query, but do not update your permanent routing table yet."
**Distractor breakdowns:**
- *A (MOVED redirection):* A `MOVED` error is returned only after the migration is 100% complete, instructing the client to permanently update its routing map.
- *C (OOM error):* Migration moves data; it does not trigger Out Of Memory errors unless the target node is misconfigured.
- *D (Stale value):* Redis enforces strict consistency during migration; it will not return a stale value if the key has already been moved.

### Question 17
**Answer:** B
**Explanation:** Request coalescing (or single-flighting) tracks concurrent requests for the same missing cache key. Instead of letting 100 threads hit the database simultaneously, it holds 99 threads and allows only 1 thread to query the DB, populating the cache and then unblocking the others.
**Distractor breakdowns:**
- *A (Write-behind):* Write-behind optimizes writes; stampedes are a read-side problem caused by simultaneous misses.
- *C (Disabling eviction):* Disabling eviction only stops keys from being removed due to memory pressure; it doesn't stop them from expiring due to TTL, which causes the stampede.
- *D (volatile-lfu):* Eviction policies do not prevent simultaneous cache misses when a hard TTL expires.

### Question 18
**Answer:** C
**Explanation:** A freshness contract explicitly defines the system design boundary: what data is cached (boundary), how it is addressed (key format), how long it naturally lives (TTL), and exactly what events cause it to be actively deleted (invalidation policy).
**Distractor breakdowns:**
- *A (Programming language):* The language used is an implementation detail that has zero impact on the architectural caching semantics.
- *B (Number of nodes):* Cluster sizing dictates capacity and throughput, not data freshness or consistency rules.
- *D (Total RAM):* Database memory sizing is irrelevant to defining the behavioral contract of the cache tier.

### Question 19
**Answer:** C
**Explanation:** When `maxmemory` is reached and the policy is `noeviction`, Redis acts as a strict bounded cache. It refuses to evict any existing data and will immediately return an OOM (Out of Memory) error for any command that attempts to allocate more memory (like `SET` or `HSET`).
**Distractor breakdowns:**
- *A (Delete oldest keys):* This behavior describes `allkeys-lru` or `volatile-lru`, specifically contradicting the `noeviction` policy.
- *B (Write to disk):* Redis is an in-memory datastore; it does not automatically swap active keys to disk when full (virtual memory was deprecated years ago).
- *D (Silently drop):* Redis never silently drops writes; it explicitly returns an error to the client so the application knows the write failed.

### Question 20
**Answer:** C
**Explanation:** Redis Sorted Sets (`ZSET`) store unique string members associated with a floating-point score. Redis maintains the set in sorted order automatically, allowing O(log(N)) inserts and O(1) or O(log(N)) range queries (like `ZREVRANGE` or `ZRANK`), making it perfect for real-time leaderboards.
**Distractor breakdowns:**
- *A (Hashes):* Hashes provide O(1) field lookups but have no concept of sorting or ranking among fields.
- *B (Strings):* Strings are scalar values; you would have to fetch the entire string, parse it, and sort it in application code, completely defeating the purpose.
- *D (Streams):* Streams are append-only logs designed for event sourcing and consumer groups, not for maintaining sorted ranks.
