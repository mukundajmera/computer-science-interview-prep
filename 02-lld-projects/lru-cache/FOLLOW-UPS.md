# Lru Cache - Interview Follow-Ups

Junior to Staff level follow-up questions and model answers.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [PITFALLS](./PITFALLS.md) · [RUBRIC](./RUBRIC.md)

---

## Question 1: How to implement O(1) time complexity for both get and put?

**Level**: Junior

**Question**: How to implement O(1) time complexity for both get and put?

**Model Answer**: Combine a standard Hash Map with a custom Doubly Linked List. The hash map provides O(1) key lookups, and the linked list provides O(1) removals and insertions at the head.

**Interviewer Context**: For a Junior level question, the focus is on
correctness and fundamental understanding of data structures and standard APIs.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Requires highly meticulous pointer manipulation (prev/next) during node rearrangement to avoid breaking the chain.

## Question 2: What exact steps happen when the cache reaches its maximum capacity?

**Level**: Junior

**Question**: What exact steps happen when the cache reaches its maximum capacity?

**Model Answer**: Identify the tail node of the doubly linked list, remove it from the list, extract its key, and delete that key from the hash map. Finally, insert the new item.

**Interviewer Context**: For a Junior level question, the focus is on
correctness and fundamental understanding of data structures and standard APIs.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: These multiple distinct operations (list update + map update) must be executed atomically to maintain data integrity.

## Question 3: How to handle basic thread safety in Java?

**Level**: Junior

**Question**: How to handle basic thread safety in Java?

**Model Answer**: Use a `ReentrantReadWriteLock` to allow multiple concurrent readers but exclusive writers, or wrap the entire data structure in a `synchronized` block.

**Interviewer Context**: For a Junior level question, the focus is on
correctness and fundamental understanding of data structures and standard APIs.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: This prevents `ConcurrentModificationException` and broken pointers, though it limits maximum throughput.

## Question 4: How to implement a Time-To-Live (TTL) expiration feature?

**Level**: Junior

**Question**: How to implement a Time-To-Live (TTL) expiration feature?

**Model Answer**: Store an expiration timestamp inside each cache node. Upon `get()`, check if `currentTime > timestamp`. If it is, lazily evict the node and return a cache miss.

**Interviewer Context**: For a Junior level question, the focus is on
correctness and fundamental understanding of data structures and standard APIs.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Lazy eviction avoids locking overhead, but active background thread eviction is needed to reclaim memory for untouched expired keys.

## Question 5: How to significantly improve concurrency over a single global lock?

**Level**: Senior

**Question**: How to significantly improve concurrency over a single global lock?

**Model Answer**: Implement Lock Striping (similar to Java's `ConcurrentHashMap`). Divide the cache into N independent segments, each protecting its own hash map and linked list with a separate lock.

**Interviewer Context**: At the Senior level, expect candidates to independently
identify bottlenecks and propose industry-standard distributed systems patterns.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Significantly increases write throughput by reducing lock contention, as different keys map to different locks.

## Question 6: How to prevent a Cache Stampede (Thundering Herd) on a cold start?

**Level**: Senior

**Question**: How to prevent a Cache Stampede (Thundering Herd) on a cold start?

**Model Answer**: Implement a mechanism like a 'Promise' or a lock-per-key. If a key is missing, only one thread is allowed to compute/fetch it, while other requesting threads block and wait for the result.

**Interviewer Context**: At the Senior level, expect candidates to independently
identify bottlenecks and propose industry-standard distributed systems patterns.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Requires fine-grained locking and condition variables to park threads efficiently without busy-waiting.

## Question 7: How to track cache hits, misses, and eviction metrics efficiently?

**Level**: Senior

**Question**: How to track cache hits, misses, and eviction metrics efficiently?

**Model Answer**: Use a `LongAdder` (in Java) or striped atomic integers instead of a single `AtomicInteger`. Striped counters avoid CAS (Compare-And-Swap) contention on a single variable.

**Interviewer Context**: At the Senior level, expect candidates to independently
identify bottlenecks and propose industry-standard distributed systems patterns.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Non-blocking, low-contention updates are crucial so that observability doesn't degrade core cache performance.

## Question 8: How to evolve this in-memory cache into a Distributed Cache cluster?

**Level**: Staff

**Question**: How to evolve this in-memory cache into a Distributed Cache cluster?

**Model Answer**: Distribute keys across a cluster of nodes using Consistent Hashing. Implement a gossip protocol for dynamic node membership and failure detection.

**Interviewer Context**: For a Staff level question, the candidate should
consider edge cases, organizational impact, cost, and cross-region failure
scenarios.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Network latency and serialization overhead become the dominating performance factors, replacing local memory access times.

## Question 9: How to handle severely 'hot keys' (e.g., Justin Bieber's profile) in a distributed cache?

**Level**: Staff

**Question**: How to handle severely 'hot keys' (e.g., Justin Bieber's profile) in a distributed cache?

**Model Answer**: Implement local L1 caching on the client/application side, or dynamically replicate the hot keys across all cache nodes rather than sharding them.

**Interviewer Context**: For a Staff level question, the candidate should
consider edge cases, organizational impact, cost, and cross-region failure
scenarios.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Cache invalidation becomes exceedingly difficult. You must rely on short TTLs or complex broadcast invalidation protocols.

## Question 10: Design an LFU (Least Frequently Used) cache with O(1) operations.

**Level**: Staff

**Question**: Design an LFU (Least Frequently Used) cache with O(1) operations.

**Model Answer**: Maintain a Hash Map for `key -> value`, and a separate Doubly Linked List of 'Frequencies'. Each Frequency node contains a `LinkedHashSet` of keys accessed that many times.

**Interviewer Context**: For a Staff level question, the candidate should
consider edge cases, organizational impact, cost, and cross-region failure
scenarios.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Requires substantially more complex pointer management and memory overhead than LRU, as nodes move between frequency buckets.

## Question 11: How would you implement a persistent cache that survives service restarts?

**Level**: Staff

**Question**: How would you implement a persistent cache that survives service restarts?

**Model Answer**: Use a write-ahead log (WAL) for all cache mutations, or periodically snapshot the memory state to disk (similar to Redis RDB/AOF).

**Interviewer Context**: For a Staff level question, the candidate should
consider edge cases, organizational impact, cost, and cross-region failure
scenarios.

- **Complexity Considerations**: Varies heavily based on the specific data structures chosen.
- **Concurrency & Scale**: Adds significant I/O latency to write operations.

When navigating these follow-up questions during a lru-cache interview, it is
crucial to remain calm and systematic. Interviewers are often not looking for a
single 'correct' answer, but rather evaluating your thought process, your
familiarity with different architectural patterns, and your ability to weigh
competing trade-offs.

Follow-up context regarding Storage Costs: Prepare to discuss this in depth.
Follow-up context regarding Compute Costs: Prepare to discuss this in depth.
Follow-up context regarding Network Bandwidth: Prepare to discuss this in depth.
Follow-up context regarding Data Compliance (GDPR): Prepare to discuss this in depth.
Follow-up context regarding Security Posture: Prepare to discuss this in depth.
Follow-up context regarding Incident Response: Prepare to discuss this in depth.
Follow-up context regarding On-call Playbooks: Prepare to discuss this in depth.
Follow-up context regarding Performance Testing: Prepare to discuss this in depth.
Follow-up context regarding Chaos Engineering: Prepare to discuss this in depth.
Follow-up context regarding Capacity Planning: Prepare to discuss this in depth.
Follow-up context regarding Tech Debt Management: Prepare to discuss this in depth.
Follow-up context regarding Team Topologies: Prepare to discuss this in depth.
Follow-up context regarding Vendor Lock-in: Prepare to discuss this in depth.
Follow-up context regarding Open Source Alternatives: Prepare to discuss this in depth.
Follow-up context regarding Build vs Buy Decisions: Prepare to discuss this in depth.
Follow-up context regarding Time to Market: Prepare to discuss this in depth.
Follow-up context regarding A/B Testing Infrastructure: Prepare to discuss this in depth.
Follow-up context regarding Feature Flags: Prepare to discuss this in depth.
Follow-up context regarding Schema Migrations: Prepare to discuss this in depth.
Follow-up context regarding Data Archival: Prepare to discuss this in depth.

Deep Dive Scenario: Imagine Primary Database fails in the lru-cache system.
Deep Dive Scenario: Imagine Cache Layer fails in the lru-cache system.
Deep Dive Scenario: Imagine Message Queue fails in the lru-cache system.
Deep Dive Scenario: Imagine Load Balancer fails in the lru-cache system.
Deep Dive Scenario: Imagine API Gateway fails in the lru-cache system.
Deep Dive Scenario: Imagine Authentication Service fails in the lru-cache system.
Deep Dive Scenario: Imagine Search Index fails in the lru-cache system.
Deep Dive Scenario: Imagine Worker Nodes fails in the lru-cache system.
Deep Dive Scenario: Imagine CDN Edge fails in the lru-cache system.
Deep Dive Scenario: Imagine Third-party API Integration fails in the lru-cache system.
Deep Dive Scenario: Imagine DNS Provider fails in the lru-cache system.
Deep Dive Scenario: Imagine Object Storage fails in the lru-cache system.
Deep Dive Scenario: Imagine Hardware Acceleration fails in the lru-cache system.
Deep Dive Scenario: Imagine Kernel Tuning fails in the lru-cache system.
Deep Dive Scenario: Imagine Memory Fragmentation fails in the lru-cache system.
Deep Dive Scenario: Imagine Network Topologies fails in the lru-cache system.
