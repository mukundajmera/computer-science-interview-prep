# Lru Cache - Common Interview Pitfalls

Common failure patterns and what to do instead.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. O(N) Eviction Time

- **Pitfall**: Using a simple array or an unlinked `ArrayList` to track usage history.
- **Why it hurts**: This requires a linear scan to find the Least Recently Used item, destroying the required O(1) performance constraint.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The O(N) Eviction Time pitfall is frequently observed when
candidates focus solely on the happy path. This specifically highlights the need
for careful resource management in lru-cache. Candidates should explicitly
mention how they would monitor for this issue in production using relevant
metrics. Furthermore, they should be prepared to discuss alternative approaches
and why this specific solution was chosen for lru-cache.

## 2. Missing Concurrency Controls

- **Pitfall**: Implementing `get` and `put` operations without any synchronization mechanisms in a multi-threaded environment, leading to corrupted data structures and race conditions..
- **Why it hurts**: Degrades overall system capability.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Missing Concurrency Controls pitfall is frequently
observed when candidates focus solely on the happy path. Addressing this
requires a deep understanding of concurrent execution and lock management.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
lru-cache.

## 3. Granular Locking Bottleneck

- **Pitfall**: Using a single, global lock (like `synchronized(this)`) around the entire cache.
- **Why it hurts**: Under high concurrent load, this serializes all access, making the cache a massive performance bottleneck.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Granular Locking Bottleneck pitfall is frequently
observed when candidates focus solely on the happy path. Addressing this
requires a deep understanding of concurrent execution and lock management.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
lru-cache.

## 4. Memory Leaks via Orphaned Data

- **Pitfall**: Forgetting to remove the evicted item's key from the internal hash map when the node is pruned from the linked list, causing the hash map to grow infinitely..
- **Why it hurts**: Degrades overall system capability.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Memory Leaks via Orphaned Data pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in lru-cache. Candidates
should explicitly mention how they would monitor for this issue in production
using relevant metrics. Furthermore, they should be prepared to discuss
alternative approaches and why this specific solution was chosen for lru-cache.

## 5. Null Value Mishandling

- **Pitfall**: Not explicitly defining the behavior for caching `null` values.
- **Why it hurts**: Returning `null` on a cache miss becomes ambiguous if `null` is also a valid cached value.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Null Value Mishandling pitfall is frequently observed
when candidates focus solely on the happy path. This specifically highlights the
need for careful resource management in lru-cache. Candidates should explicitly
mention how they would monitor for this issue in production using relevant
metrics. Furthermore, they should be prepared to discuss alternative approaches
and why this specific solution was chosen for lru-cache.

## 6. Stale Data (No TTL)

- **Pitfall**: Implementing pure LRU without any Time-To-Live (TTL) mechanism.
- **Why it hurts**: If a key is accessed frequently, it never evicts, potentially serving dangerously stale data indefinitely.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Stale Data (No TTL) pitfall is frequently observed
when candidates focus solely on the happy path. This specifically highlights the
need for careful resource management in lru-cache. Candidates should explicitly
mention how they would monitor for this issue in production using relevant
metrics. Furthermore, they should be prepared to discuss alternative approaches
and why this specific solution was chosen for lru-cache.

## 7. Inefficient Node Allocation

- **Pitfall**: Constantly instantiating new Node objects via `new Node()` on every single `put` operation.
- **Why it hurts**: In garbage-collected languages (Java/Go), this causes immense GC pressure
- **Better**: Reuse nodes instead.

Detailed explanation: The Inefficient Node Allocation pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in lru-cache. Candidates
should explicitly mention how they would monitor for this issue in production
using relevant metrics. Furthermore, they should be prepared to discuss
alternative approaches and why this specific solution was chosen for lru-cache.

## 8. Ignoring the Cache Stampede

- **Pitfall**: Allowing multiple concurrent threads to experience a cache miss for the exact same key, causing all of them to query the expensive backend database simultaneously, crashing it..
- **Why it hurts**: Degrades overall system capability.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Ignoring the Cache Stampede pitfall is frequently
observed when candidates focus solely on the happy path. In the context of the
lru-cache architecture, this component is often a bottleneck under heavy
database load. Candidates should explicitly mention how they would monitor for
this issue in production using relevant metrics. Furthermore, they should be
prepared to discuss alternative approaches and why this specific solution was
chosen for lru-cache.

## 9. Incorrect Map-List Synchronization

- **Pitfall**: Updating the hash map successfully but throwing an exception before updating the linked list, leaving the two core structures totally out of sync..
- **Why it hurts**: Degrades overall system capability.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Incorrect Map-List Synchronization pitfall is
frequently observed when candidates focus solely on the happy path. This
specifically highlights the need for careful resource management in lru-cache.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
lru-cache.

## 10. Improper Hashing Algorithm

- **Pitfall**: Utilizing a hash function with a high collision rate, causing the underlying HashMap to degrade into an O(N) linked list lookup for key retrieval..
- **Why it hurts**: Degrades overall system capability.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Improper Hashing Algorithm pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in lru-cache. Candidates
should explicitly mention how they would monitor for this issue in production
using relevant metrics. Furthermore, they should be prepared to discuss
alternative approaches and why this specific solution was chosen for lru-cache.

---

## Quick Self-Check Before You Present

1. Can you explain the core tradeoffs?
2. Is the design scalable?
3. Are concurrency issues handled perfectly?
4. Is the data schema logically normalized?

---

## Variants and Extensions You Should Mention

1. Multi-region Active-Active setups.
2. Advanced Sharding and Partitioning strategies.
3. Layered Caching and CDNs.
4. Event-driven and CQRS architectures.

When concluding your design for lru-cache, always revisit the initial
constraints. If the system was heavily read-optimized, confirm that your caching
strategy supports the expected QPS. If it was write-heavy, ensure your database
partitioning and queuing mechanisms can handle the throughput. Remember that no
system design is perfect; it's about making informed compromises and being able
to defend them intelligently.

Finally, consider the operational aspects. How will you deploy this? How do you
monitor its health? What are the key SLIs (Service Level Indicators) you would
track? A senior engineer not only designs the architecture but also plans for
its long-term maintainability and operability in a production environment.

Note on Database Indexing: Consider this deeply when discussing lru-cache.
Note on Message Queues: Consider this deeply when discussing lru-cache.
Note on Caching Strategies: Consider this deeply when discussing lru-cache.
Note on Load Balancing: Consider this deeply when discussing lru-cache.
Note on Data Sharding: Consider this deeply when discussing lru-cache.
Note on Replication Lag: Consider this deeply when discussing lru-cache.
Note on Eventual Consistency: Consider this deeply when discussing lru-cache.
Note on ACID Transactions: Consider this deeply when discussing lru-cache.
Note on Rate Limiting: Consider this deeply when discussing lru-cache.
Note on Circuit Breakers: Consider this deeply when discussing lru-cache.
Note on Service Mesh: Consider this deeply when discussing lru-cache.
Note on Microservices vs Monolith: Consider this deeply when discussing lru-cache.
Note on API Gateway: Consider this deeply when discussing lru-cache.
Note on Authentication/Authorization: Consider this deeply when discussing lru-cache.
Note on Disaster Recovery: Consider this deeply when discussing lru-cache.
Note on Zero Downtime Deployments: Consider this deeply when discussing lru-cache.
Note on CI/CD Pipelines: Consider this deeply when discussing lru-cache.
Note on Monitoring and Alerting: Consider this deeply when discussing lru-cache.
Note on Log Aggregation: Consider this deeply when discussing lru-cache.
Note on Distributed Tracing: Consider this deeply when discussing lru-cache.

Advanced consideration for Network Partitions: How does it impact latency in lru-cache?
Advanced consideration for Disk I/O: How does it impact latency in lru-cache?
Advanced consideration for Garbage Collection Pauses: How does it impact latency in lru-cache?
Advanced consideration for Thread Context Switching: How does it impact latency in lru-cache?
Advanced consideration for Connection Pooling Limits: How does it impact latency in lru-cache?
Advanced consideration for DNS Resolution: How does it impact latency in lru-cache?
Advanced consideration for TLS Handshakes: How does it impact latency in lru-cache?
Advanced consideration for Serialization Overhead: How does it impact latency in lru-cache?
Advanced consideration for B-Tree Page Splits: How does it impact latency in lru-cache?
Advanced consideration for Cache Eviction Spikes: How does it impact latency in lru-cache?
Advanced consideration for Thundering Herd Problem: How does it impact latency in lru-cache?
Advanced consideration for Cold Starts: How does it impact latency in lru-cache?
Advanced consideration for Database Vacuuming: How does it impact latency in lru-cache?
Advanced consideration for Index Rebuilding: How does it impact latency in lru-cache?
Advanced consideration for Message Broker Backpressure: How does it impact latency in lru-cache?
Advanced consideration for Retry Storms: How does it impact latency in lru-cache?
Advanced consideration for Semantic Versioning: How does it impact latency in lru-cache?
Advanced consideration for Feature Flags: How does it impact latency in lru-cache?
Advanced consideration for Chaos Engineering: How does it impact latency in lru-cache?
Advanced consideration for Performance Benchmarking: How does it impact latency in lru-cache?
