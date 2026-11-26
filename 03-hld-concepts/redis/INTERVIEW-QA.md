# Interview Questions: Redis

## Core Concepts

### 1. Where does Redis fit in a system design?
**Q**: In a typical architecture, what role does Redis play?
**A**: Redis usually sits on hot read and coordination paths: cache, counters, session state, and short-lived control keys.

### 2. Redis vs Memcached
**Q**: Why choose Redis over Memcached?
**A**: Redis provides richer structures and primitives (streams, sorted sets, expirations, atomic ops) that fit more interview scenarios than plain key-value caching.

### 3. Event Loop and Threading
**Q**: Is Redis entirely single-threaded? How does Redis 6+ handle high I/O concurrency?
**A**: Command execution is strictly single-threaded to preserve lock-free atomicity. However, Redis 6+ introduces Multi-threaded I/O, offloading network socket parsing and output buffer writing to background worker threads.

### 4. Data-Structure Encodings
**Q**: How does Redis optimize memory for a small Hash vs a large Hash?
**A**: For small hashes, Redis uses a highly compact contiguous memory structure called a `ziplist` (or `listpack`). When the hash grows beyond a certain size or contains large values, it dynamically upgrades the encoding to a real hash table (`dict`).

### 5. Command Complexity
**Q**: Why is `KEYS *` dangerous in production, and what should you use instead?
**A**: `KEYS *` is O(N) where N is the entire keyspace. Since command execution is single-threaded, this will block all other clients until it finishes. You should use `SCAN`, which is O(1) per call and iterates through the keyspace using a cursor without blocking the server.

### 6. Expiry Policies
**Q**: How does Redis physically remove keys that have a TTL?
**A**: It uses a mix of passive and active expiration. Passively, if a client accesses an expired key, it's deleted then. Actively, Redis runs a background loop 10 times a second that samples keys with TTLs and deletes the expired ones, ensuring memory doesn't fill up with unaccessed expired keys.

### 7. Eviction Policies
**Q**: What is the difference between `volatile-lru` and `allkeys-lru`?
**A**: `volatile-lru` only evicts keys that have a TTL set, preserving permanent keys (useful when mixing cache and persistent data). `allkeys-lru` will evict the least recently used key among *all* keys in the database (useful when Redis is acting purely as a cache).

### 8. LFU and the Morris Counter
**Q**: How does Redis evict least frequently used (LFU) keys efficiently without blowing up memory?
**A**: It avoids strict counting by using a Morris approximate logarithmic counter stored in an 8-bit field, paired with a time-based decay mechanism to age out historically hot keys.

### 9. RDB Persistence
**Q**: How does Redis take an RDB snapshot without blocking the main thread?
**A**: It uses the OS `fork()` syscall. The child process gets a point-in-time copy of memory (leveraging Copy-on-Write) and writes it to disk, while the parent continues serving clients. However, heavy writes during this time can cause CoW memory spikes.

### 10. AOF vs RDB
**Q**: What is the trade-off between AOF and RDB?
**A**: RDB is compact and fast to load but loses data between snapshots (e.g., 5 mins). AOF logs every command, providing near-perfect durability (usually max 1 second loss), but creates huge files that require periodic rewrites and slower startup times. Modern Redis uses a hybrid approach.

### 11. Replication
**Q**: What happens when a Redis replica disconnects and reconnects to a primary?
**A**: It attempts a partial resynchronization by asking for the missing commands from the primary's replication backlog. If the backlog has rolled over or the replica is too far behind, it triggers a full resynchronization, forcing the primary to generate and send a full RDB file.

### 12. Sentinel vs Cluster
**Q**: When would you choose Redis Cluster over Redis Sentinel?
**A**: Sentinel provides High Availability for a single-shard setup (all data on one master). You choose Cluster when you need to horizontally scale *writes* or when your dataset exceeds the memory/CPU capacity of a single machine, as Cluster shards data across up to 16,384 slots.

### 13. MOVED and ASK Redirections
**Q**: How does a client route requests in a Redis Cluster?
**A**: A cluster-aware client calculates the slot for a key (`CRC16(key) mod 16384`) and sends it to the assumed node. If wrong, the node returns a `MOVED` error with the correct IP. If the slot is currently migrating, it returns an `ASK` error, telling the client to query the new node just for this one request.

### 14. Hash Tags
**Q**: How do you perform multi-key operations (like Lua scripts) safely across a Redis Cluster?
**A**: Multi-key operations are restricted to keys on the same node. You must use hash tags (e.g., `{user:123}.profile` and `{user:123}.settings`) to force only the substring inside the braces to be hashed, ensuring they land in the same slot.

### 15. Pipelining vs Transactions
**Q**: What is the difference between Pipelining and Transactions (`MULTI`/`EXEC`)?
**A**: Pipelining is purely a network optimization to send multiple commands without waiting for replies, reducing RTT. Transactions queue commands on the server to execute them sequentially and atomically without interruption from other clients.

### 16. Streams vs Pub/Sub
**Q**: When is Pub/Sub the wrong choice?
**A**: Pub/Sub is fire-and-forget and non-replayable; if a subscriber is down, the message is lost. Use Streams when you need durability, consumer groups, and recovery/replay semantics.

### 17. Big Keys
**Q**: Why are Big Keys a problem, and how do you mitigate them?
**A**: Deleting a big key (e.g., a hash with 10 million fields) with `DEL` blocks the single main thread. Mitigation involves using `UNLINK` for asynchronous deletion, or iteratively deleting fields using `HSCAN` and `HDEL`.

### 18. Hot Keys
**Q**: How do you handle a single hot key that is overwhelming a Redis node?
**A**: You can implement a local in-memory cache in your application servers to absorb the reads before they hit Redis. Alternatively, you can duplicate the key across multiple slots (e.g., append `_1`, `_2` to the key) and have clients randomly read from the replicas to distribute the load.

### 19. Distributed Locks
**Q**: What correctness safeguards must you mention when designing a distributed lock with Redis?
**A**: You must use a unique lock token (so you don't delete someone else's lock), set an expiration (to prevent deadlocks if the client crashes), and use a Lua script for the unlock phase to ensure atomic compare-and-delete semantics.
