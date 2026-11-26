# Caching Strategies Quiz

### Question 1
Which caching pattern is generally considered the safest default for an interview setting because it keeps the source-of-truth in the primary store and avoids mandatory cache coupling?
- A) Write-through cache
- B) Write-behind cache
- C) Cache-aside cache
- D) Read-through cache

### Question 2
When implementing a cache for a high-traffic product page, which specific piece of data should ideally NOT have a long TTL because of strict correctness and consistency requirements?
- A) Product metadata like description and images
- B) Display-only hints and static layouts
- C) Historical purchase analytics
- D) Source-of-truth price and inventory

### Question 3
What is the primary danger of using synchronized expiry (TTL) for a large batch of highly popular keys?
- A) It dramatically increases the memory usage of the cache tier.
- B) It can cause a thundering herd (stampede) that overwhelms the backend database.
- C) It causes the cache to automatically switch to read-through mode.
- D) It violates the requirements for consistent hashing across shards.

### Question 4
Which eviction policy is often considered the robust default for general caching workloads?
- A) LFU (Least Frequently Used)
- B) Random Replacement
- C) LRU (Least Recently Used)
- D) LIFO (Last In First Out)

### Question 5
In Redis, which feature helps to prevent historically popular keys from dominating the LFU (Least Frequently Used) cache forever?
- A) The `fsync` background process
- B) The Morris approximate logarithmic counter
- C) A decay mechanic that periodically decreases the LFU counter based on idle time
- D) Setting the `maxmemory-policy` to `allkeys-random`

### Question 6
How does Redis Cluster map keys to specific nodes?
- A) By using a consistent hashing ring directly
- B) By using exactly 16,384 hash slots based on `CRC16(key) mod 16384`
- C) By relying on an external Zookeeper or etcd coordinator
- D) By assigning keys to nodes alphabetically

### Question 7
Which caching pattern is most appropriate for analytics or event pipelines where throughput is prioritized over immediate durability, and eventual persistence is acceptable?
- A) Cache-aside
- B) Write-through
- C) Write-behind
- D) Stale-while-revalidate

### Question 8
If a single hot key is severely overloading one Redis shard, which of the following is NOT an effective mitigation strategy?
- A) Replicating or bucketing the hot key
- B) Switching the eviction policy to `allkeys-lru`
- C) Adding an in-process fallback cache layer
- D) Rate-limiting abusive traffic paths

### Question 9
In the context of Redis 7, what is the primary benefit of the Multi-part AOF architecture compared to the traditional AOF?
- A) It guarantees zero data loss in all failure scenarios.
- B) It automatically clusters data without needing hash slots.
- C) It significantly simplifies the AOF rewrite process and reduces disk I/O overhead.
- D) It allows for infinite memory usage by swapping to disk automatically.

### Question 10
When writing to the database and keeping the cache consistent, what is a typical approach to handle the cache update?
- A) Write to the cache first, then asynchronously write to the database
- B) Write to the database first, then invalidate (delete) the cache key
- C) Wait for the cache TTL to expire naturally without invalidating
- D) Write to the database and rely on a nightly batch job to update the cache

### Question 11
What is a recommended fallback mechanism to protect the source database when the cache tier experiences a complete outage?
- A) Fall back to long-polling the database until the cache recovers
- B) Replicate the cache data immediately to a CDN
- C) Implement circuit breakers, admission control, and possibly degraded responses
- D) Automatically upgrade the database to a larger instance

### Question 12
Which metric is generally the most direct indicator of how much a cache is successfully shielding the backend database?
- A) Cache eviction rate
- B) The size of the cache objects
- C) Network bandwidth used by the cache
- D) Hit ratio and backend offload percentage

### Question 13
Why should you generally avoid caching every single endpoint in a system?
- A) Because all endpoints require the same TTL
- B) Low reuse and highly volatile data add invalidation complexity without meaningful latency gain
- C) It is impossible to configure a cache cluster for more than a few endpoints
- D) Because caching always increases the overall CPU usage of the application servers

### Question 14
In a Redis Cluster, what is the purpose of hash tags (using curly braces like `{user:123}.profile`)?
- A) To compress the key name to save memory
- B) To enforce a strict TTL on all keys with the same tag
- C) To ensure that multiple keys are hashed to the exact same hash slot for multi-key operations
- D) To automatically encrypt the key data

### Question 15
What is the primary role of the `fsync` configuration in Redis AOF persistence?
- A) It determines which eviction algorithm is used.
- B) It controls the balance between write throughput performance and data durability guarantees.
- C) It defines the number of replicas required for a successful write.
- D) It configures the TTL for ephemeral data.

### Question 16
What response does a Redis Cluster node return when a client attempts to access a key for a hash slot that is currently being actively migrated to another node?
- A) A permanent `MOVED` redirection
- B) A transient `ASK` redirection
- C) An `OOM` (Out of Memory) error
- D) The stale value from the old node

### Question 17
Which of the following techniques is commonly used alongside jittered TTL to prevent cache stampedes on top hot keys?
- A) Switching to write-behind caching
- B) Request coalescing (single-flight)
- C) Disabling cache eviction entirely
- D) Using the `volatile-lfu` eviction policy

### Question 18
When defining a cache design in an interview, what should you ideally state to define the freshness contract?
- A) The programming language used to implement the cache
- B) The maximum number of Redis nodes in the cluster
- C) The cache boundary, key format, TTL, and explicit invalidation policy
- D) The total amount of RAM available on the database server

### Question 19
If a Redis server reaches its `maxmemory` limit and the policy is set to `noeviction`, what will happen when a new write command arrives?
- A) Redis will automatically delete the oldest keys to make room.
- B) Redis will write the new data to disk instead of memory.
- C) Redis will return an error and reject the write command.
- D) Redis will silently drop the new data but acknowledge the write.

### Question 20
Which Redis data structure is best suited for implementing real-time leaderboards and ranking systems?
- A) Hashes
- B) Strings
- C) Sorted Sets
- D) Streams

