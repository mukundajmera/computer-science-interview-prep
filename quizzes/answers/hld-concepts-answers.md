# Hld Concepts Quiz - Answer Key

> **Detailed explanations for all 74 questions**

---

### Question 1
**Answer: D**

**Why Correct:**
- Establishing functional and non-functional requirements defines the scope, scale, and constraints, dictating the rest of the architecture. Distractors like picking a DB without knowing access patterns lead to fundamentally flawed designs. The correct choice is "Clarify requirements and constraints". Conversely, jumping to an architectural diagram early limits your ability to adapt to critical constraints that emerge during deeper discussion.

**Why Not Distractors:**
- **A**: This distractor (Never clarify requirements and constraints during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Pick database technology) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Estimate yearly storage only) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-1)

### Question 2
**Answer: C**

**Why Correct:**
- Capacity planning should drive concrete technical choices (e.g., whether to shard or cache) rather than just being an exercise in arithmetic. Precision without impact wastes valuable interview time. The correct choice is "Estimate that changes an architecture decision". For instance, calculating the exact storage cost in pennies is unhelpful unless it actively shifts the storage medium from SSDs to cold tape archives.

**Why Not Distractors:**
- **A**: This distractor (Any estimate done early) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Most precise estimate regardless of impact) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Never estimate that changes an architecture decision during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-2)

### Question 3
**Answer: D**

**Why Correct:**
- This structured flow starts with constraints, moves to scale, defines API contracts, outlines the high-level architecture, and finally addresses specific technical risks via deep dives. The correct choice is "Requirements -> capacity -> interfaces -> architecture -> deep dives". This prevents the common pitfall of diving into database schema definitions before fundamentally establishing what APIs the system even needs to serve.

**Why Not Distractors:**
- **A**: This distractor (APIs -> data model -> requirements -> deep dives) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Capacity only -> architecture) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (deep dives -> architecture -> interfaces -> capacity -> Requirements (which is incorrect)) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-3)

### Question 4
**Answer: B**

**Why Correct:**
- A solid conclusion summarizes the architecture, explicitly acknowledges what was sacrificed (trade-offs), and identifies remaining bottlenecks or risks, demonstrating senior-level maturity. The correct choice is "Final design + key trade-off + risk note". Merely listing considered tools or pseudocode fails to show the high-level synthesis expected from senior engineers.

**Why Not Distractors:**
- **A**: This distractor (Assuming that final design + key trade-off + risk note is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Future roadmap only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (A list of all tools considered) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-4)

### Question 5
**Answer: C**

**Why Correct:**
- Spending excessive time on trivial components (e.g., basic load balancers) leaves no time for the complex, high-signal parts of the design, which is a critical failure in time management. The correct choice is "Missing deep dives due over-detailing low-impact areas". When candidates over-index on standard components, they run out of time to discuss the core complexities of the actual problem domain.

**Why Not Distractors:**
- **A**: This distractor (Defining out-of-scope boundaries) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Stating trade-offs) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Missing deep dives due over-detailing high-impact areas) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-5)

### Question 6
**Answer: A**

**Why Correct:**
- Network partitions are inevitable in distributed systems. Therefore, the practical choice is between Consistency and Availability during a partition, making partition tolerance a mandatory baseline assumption. The correct choice is "Mandatory assumption". Since networks are inherently unreliable, a distributed system must handle partitions, leaving only the choice between strong consistency and high availability.

**Why Not Distractors:**
- **B**: This distractor (Equivalent to strong consistency) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Only for NoSQL) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Optional) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-6)

### Question 7
**Answer: B**

**Why Correct:**
- Systems rarely have a single global CAP stance. Different features (e.g., critical checkout vs. casual browsing) require specific trade-offs between consistency and availability based on business impact. The correct choice is "Choose per operation based on business harm and failure mode". Applying a blanket policy across the entire system usually over-engineers non-critical paths or under-protects critical state.

**Why Not Distractors:**
- **A**: This distractor (Label the whole system AP or CP once) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that choose per operation based on business harm and failure mode is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Always choose consistency) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-7)

### Question 8
**Answer: A**

**Why Correct:**
- Financial transactions or inventory-locking events like seat booking cannot tolerate conflicting states. Strong consistency is required to prevent double-booking and financial loss. The correct choice is "Seat booking commit". If a system prioritized availability over consistency for seat bookings, it would inevitably sell the same seat to multiple users.

**Why Not Distractors:**
- **B**: This distractor (Recommendation feed) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Public profile image read) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Product browse page) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-8)

### Question 9
**Answer: B**

**Why Correct:**
- A slightly delayed or out-of-order recommendation feed does not impact business correctness or cause user harm, making it an ideal candidate for highly available, eventually consistent designs. The correct choice is "Feed ranking refresh". Recommendations can easily tolerate eventual consistency; dropping requests completely just to guarantee the absolute latest model weights harms the user experience.

**Why Not Distractors:**
- **A**: This distractor (Payment capture authorization) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Final invoice generation) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Inventory decrement commit) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-9)

### Question 10
**Answer: D**

**Why Correct:**
- In the context of CAP, consistency refers to linearizability—every read receives the most recent write or an error. It differs from ACID consistency, which enforces relational schema rules. The correct choice is "Read visibility behavior under partition". It focuses strictly on the visibility of updates across nodes in a distributed system, rather than the ACID properties enforced within a single database instance.

**Why Not Distractors:**
- **A**: This distractor (Network throughput) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (SQL schema constraints) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that read visibility behavior under partition is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-10)

### Question 11
**Answer: B**

**Why Correct:**
- Sharding introduces significant operational complexity and cross-node query challenges. It should only be adopted when vertical scaling, read replicas, and caching fail to meet write or storage limits. The correct choice is "Sustained bottleneck after indexes, caching, and replicas are insufficient". Premature sharding introduces massive operational overhead and cross-shard querying complexities, making it a last resort rather than a first step.

**Why Not Distractors:**
- **A**: This distractor (Team preference for distributed systems) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Data reached 100 GB once) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Sustained bottleneck before indexes, caching, and replicas are insufficient) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-11)

### Question 12
**Answer: B**

**Why Correct:**
- A robust shard key distributes data evenly to avoid hot spots (high cardinality/even spread) while aligning with common query access patterns to minimize expensive cross-shard scatter-gather operations. The correct choice is "High cardinality, even spread, query alignment". A poorly chosen key with low cardinality or skewed distribution will quickly create hot nodes, defeating the purpose of sharding entirely.

**Why Not Distractors:**
- **A**: This distractor (Low cardinality, even spread, query alignment in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Timestamp only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Boolean flags) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-12)

### Question 13
**Answer: A**

**Why Correct:**
- Range sharding groups contiguous keys together, making it highly efficient for queries that need to scan adjacent intervals (e.g., time-series data), unlike hash sharding which scatters keys randomly. The correct choice is "Range scans over adjacent key intervals". If queries frequently require adjacent records, hash sharding would scatter them across the cluster, forcing a slow scatter-gather operation on every request.

**Why Not Distractors:**
- **B**: This distractor (Hot-key mitigation by itself) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Strictly random access with no ordering) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that range scans over adjacent key intervals is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-13)

### Question 14
**Answer: D**

**Why Correct:**
- Using simple modulo hashing (e.g., hash(key) % N) means adding or removing a single node alters the routing for almost all keys, triggering massive and disruptive data migrations. The correct choice is "Significant remap when shard count changes". This approach forces a near-total data reshuffling when scaling out, causing massive performance degradation during the cluster expansion process.

**Why Not Distractors:**
- **A**: This distractor (Assuming that significant remap when shard count changes is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Strong consistency by default) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (No routing layer needed) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-14)

### Question 15
**Answer: C**

**Why Correct:**
- Querying all shards at runtime for global Top-K creates a massive fan-out bottleneck. Precomputing the results asynchronously and caching them provides fast, scalable reads with acceptable staleness. The correct choice is "Precomputed aggregate + cache with bounded staleness". Executing a scatter-gather aggregation across all shards for every single request will quickly exhaust database connections and CPU.

**Why Not Distractors:**
- **A**: This distractor (Full-table joins on all shards) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Precomputed aggregate + cache without bounded staleness) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Scatter-gather on every request) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-15)

### Question 16
**Answer: D**

**Why Correct:**
- Consistent hashing maps keys and nodes to a ring. Adding or removing a node only affects its immediate neighbors, drastically reducing data movement during cluster scaling operations. The correct choice is "Reduced key remapping on node membership changes". By organizing nodes on a ring, consistent hashing minimizes the blast radius when nodes join or leave the cluster, avoiding catastrophic rebalancing.

**Why Not Distractors:**
- **A**: This distractor (Assuming that reduced key remapping on node membership changes is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Automatic hotspot elimination) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Elimination of replica needs) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-16)

### Question 17
**Answer: D**

**Why Correct:**
- Virtual nodes assign multiple hash ring positions to a single physical machine. This improves load balancing and allows routing proportionally more traffic to nodes with higher hardware capacity. The correct choice is "Improve distribution and support weighted capacity". This abstraction ensures that more powerful hardware can shoulder a proportionally larger share of the traffic by holding more segments on the hash ring.

**Why Not Distractors:**
- **A**: This distractor (Encrypt shard traffic) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that improve distribution and support weighted capacity is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Replace replication) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-17)

### Question 18
**Answer: D**

**Why Correct:**
- With consistent hashing, only 1/(N+1) of the data needs to be relocated when adding a node. For an 11-node cluster, this is roughly 9%, whereas modulo hashing would move almost 100%. The correct choice is "~9% with consistent hashing". This demonstrates the mathematical advantage of consistent hashing: it only moves the exact fraction of data necessary to accommodate the new node.

**Why Not Distractors:**
- **A**: This distractor (~50%) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (~100%) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (~9% without consistent hashing) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-18)

### Question 19
**Answer: B**

**Why Correct:**
- While consistent hashing evenly distributes the key space, it does not prevent a single highly popular entity (a 'hot key', like a celebrity's profile) from overwhelming the specific node that owns it. The correct choice is "Traffic popularity hotspots". If millions of users request the exact same key, the routing algorithm will still send all that traffic to the single node that owns it.

**Why Not Distractors:**
- **A**: This distractor (Replica walk selection) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Membership remap churn) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Ownership stability during scaling) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-19)

### Question 20
**Answer: C**

**Why Correct:**
- Hot keys cannot be solved by sharding alone. They require layered defenses like read replicas, caching, and key bucketing (splitting the hot key) to distribute the concentrated load. The correct choice is "Replica reads, key bucketing where valid, and cache protections". Since a single key cannot be sharded across nodes, the load must be deflected at the cache layer or distributed via read replicas.

**Why Not Distractors:**
- **A**: This distractor (Replica reads, key bucketing where valid, and database protections) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Only more virtual nodes) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Always re-shard entire dataset) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-20)

### Question 21
**Answer: D**

**Why Correct:**
- Standard latency and capacity numbers should be used as heuristics to determine if a proposed design will meet its Service Level Objectives (SLOs) before committing to a complex architecture. The correct choice is "Use ranges to justify architecture evolution against SLOs". Knowing these numbers allows you to confidently defend your architectural choices and prove that the system can handle the expected load profile.

**Why Not Distractors:**
- **A**: This distractor (Memorize fixed limits and apply blindly) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Never use ranges to justify architecture evolution against SLOs during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Avoid estimates entirely) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-21)

### Question 22
**Answer: A**

**Why Correct:**
- Before introducing complex distributed systems like message queues or sharded clusters, optimizing the database schema and indexes often yields sufficient performance gains with minimal risk. The correct choice is "Optimize schema/indexing and validate headroom". Many perceived scalability issues are simply the result of poor query optimization or missing indexes, which are much cheaper to fix than re-architecting.

**Why Not Distractors:**
- **B**: This distractor (Multi-region active-active rollout) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (CRDT adoption) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that optimize schema/indexing and validate headroom is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-22)

### Question 23
**Answer: A**

**Why Correct:**
- This pragmatic statement shows maturity: sharding is a tool for specific scaling thresholds, not a default starting point. It balances future-proofing against the dangers of premature over-engineering. The correct choice is ""I will shard when measured pressure exceeds safe headroom"". This approach avoids the traps of premature optimization while still demonstrating an awareness of how to handle growth when it arrives.

**Why Not Distractors:**
- **B**: This distractor ("Sharding is always future-proof") represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that "I will shard when measured pressure exceeds safe headroom" is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor ("I will shard now to avoid future migration") represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-23)

### Question 24
**Answer: D**

**Why Correct:**
- Request coalescing (single-flight) ensures that concurrent requests for the same missing cache key only trigger one database query, preventing the DB from collapsing under a cache miss storm. The correct choice is "Request coalescing/single-flight and backpressure". By collapsing concurrent identical requests into a single database query, you protect the backend from being overwhelmed during unexpected cache stampedes.

**Why Not Distractors:**
- **A**: This distractor (Increase retries from clients) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Request coalescing/multiple-flight and backpressure) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Disable monitoring) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-24)

### Question 25
**Answer: A**

**Why Correct:**
- A safe database migration must ensure that tail latency (P99) doesn't degrade the user experience and that the new datastore exactly matches the old one (data parity) to prevent corruption. The correct choice is "P99 latency impact and data parity checks". Ensuring both low latency and strict data correctness is critical; measuring unrelated metrics like sprint velocity offers no technical safety guarantees.

**Why Not Distractors:**
- **B**: This distractor (Number of meetings and code churn) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that p99 latency impact and data parity checks is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Team availability and sprint velocity) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-25)

### Question 26
**Answer: B**

**Why Correct:**
- Mixed criticalities demand targeted policies. Financial writes require strong consistency to prevent loss, while recommendation reads should prioritize availability to ensure UI responsiveness. The correct choice is "Consistency-first for payment writes, availability-first for recommendation reads". This targeted approach ensures that critical financial state remains perfectly accurate while non-critical UI components remain responsive.

**Why Not Distractors:**
- **A**: This distractor (Same consistency mode for everything) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Consistency-first for payment writes, availability-first for recommendation writes) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Availability-first for payment commits) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-26)

### Question 27
**Answer: B**

**Why Correct:**
- For non-critical browse functionality, serving slightly stale local data from a cache is far better for user experience than failing the request entirely during a cross-region partition. The correct choice is "Serve local data with bounded staleness contract". A graceful degradation strategy that serves slightly older data is significantly better for user retention than throwing hard errors.

**Why Not Distractors:**
- **A**: This distractor (Serve local data without bounded staleness contract) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Reject all reads) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Stop serving traffic globally) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-27)

### Question 28
**Answer: A**

**Why Correct:**
- A severe CPU imbalance indicates a hot shard. The immediate step is to protect the node via rate limiting or caching, followed by analyzing the access pattern to adjust the sharding strategy. The correct choice is "Diagnose skew type, apply short-term guardrails, then structural fix". Blindly re-architecting without diagnosing the root cause wastes time; implementing short-term protections buys the time needed to fix the underlying skew.

**Why Not Distractors:**
- **B**: This distractor (Assuming that diagnose skew type, apply short-term guardrails, then structural fix is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Immediate full rearchitecture) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Ignore if SLA not breached today) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-28)

### Question 29
**Answer: C**

**Why Correct:**
- Zero-downtime migrations require writing to both schemas (dual writes), backfilling historical data, and slowly cutting over reads to verify correctness before deprecating the old system. The correct choice is "Dual writes + checkpointed backfill + staged read cutover". This multi-stage process is the industry standard for safe migrations, allowing for rapid rollback if inconsistencies are detected during the read cutover.

**Why Not Distractors:**
- **A**: This distractor (Dual reads + checkpointed backfill + staged read cutover in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Stop writes, migrate all, restart) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Change routing in one deploy without verification) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-29)

### Question 30
**Answer: A**

**Why Correct:**
- Senior engineering candidates distinguish themselves by anticipating failure modes, acknowledging the limits of their proposed design, and providing clear, actionable operational fallback plans. The correct choice is "Tying each major component to a measured risk and fallback plan". This demonstrates a realistic understanding that no architecture is perfect and that every decision carries inherent risks that must be managed.

**Why Not Distractors:**
- **B**: This distractor (Assuming that tying each major component to a measured risk and fallback plan is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Listing many technologies without linkage) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Ending after diagram only) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-30)

### Question 31
**Answer: B**

**Why Correct:**
- Precomputing and caching personalized feeds avoids expensive database joins and massive read loads during user requests, effectively shielding the primary DB from fan-out query exhaustion. The correct choice is "Precompute feed snapshots and serve them from a dedicated cache with TTLs". This completely removes the computational burden from the primary database, shifting it to a highly scalable caching tier.

**Why Not Distractors:**
- **A**: This distractor (Duplicate every read request to all read replicas) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Precompute feed snapshots and serve them from a dedicated cache without TTLs) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Fan-out every request to each follower in real time) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-31)

### Question 32
**Answer: A**

**Why Correct:**
- CDNs distribute static content globally. Allowing users to fetch profile data from geographically close edge servers drastically reduces latency and offloads traffic from the central database. The correct choice is "CDN edge caches with origin fallback and controlled TTLs". Serving static assets directly from edge nodes drastically reduces latency and prevents cross-continental traffic from overwhelming the origin servers.

**Why Not Distractors:**
- **B**: This distractor (Central database with synchronous cross-region replication only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Refuse cross-region traffic and keep all reads local) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Replicate the entire dataset to each region and disable caching) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-32)

### Question 33
**Answer: D**

**Why Correct:**
- Cache-aside with asynchronous targeted invalidation ensures the cache is cleared when new data is written, maintaining eventual consistency without adding blocking latency to the critical write path. The correct choice is "Use cache-aside with targeted invalidations and TTL refreshers". This ensures the application stays responsive and eventually consistent, whereas synchronous purges could block critical paths under heavy load.

**Why Not Distractors:**
- **A**: This distractor (Force clients to clear their local caches manually) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Let stale data linger until TTLs expire naturally) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Use cache-aside without targeted invalidations and TTL refreshers) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-33)

### Question 34
**Answer: B**

**Why Correct:**
- Stale-while-revalidate immediately serves the user from the cache while triggering a background refresh, offering a perfect balance between ultra-low latency and eventual data freshness. The correct choice is "Stale-while-revalidate: serve cached data and refresh asynchronously". This pattern perfectly balances the need for instantaneous read responses with the requirement to eventually reflect new updates in the background.

**Why Not Distractors:**
- **A**: This distractor (Assuming that stale-while-revalidate: serve cached data and refresh asynchronously is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Serve from replicas without any refresh logic) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Always hit the primary data store for every request) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-34)

### Question 35
**Answer: A**

**Why Correct:**
- A durable message queue acts as a shock absorber during burst traffic, capturing incoming writes quickly and allowing the database to process them asynchronously at its own safe maximum rate. The correct choice is "Queue writes through a durable buffer and batch them against the primary database". This acts as a critical shock absorber, decoupling the fast ingestion path from the slower, durable storage layer.

**Why Not Distractors:**
- **B**: This distractor (Start sharding immediately across hundreds of partitions) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Queue writes through a durable buffer and batch them against the primary cache in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Disable monitoring until traffic subsides) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-35)

### Question 36
**Answer: B**

**Why Correct:**
- Salting or appending a randomized prefix to a sequential key prevents all new writes from hitting the same partition, distributing the concentrated load across the entire cluster. The correct choice is "Introducing a composite key with region/user bucket or salted prefix". This technique forces writes to distribute evenly across partitions, entirely eliminating the hotspot created by monotonically increasing keys.

**Why Not Distractors:**
- **A**: This distractor (Doubling the hardware behind the hotspot only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Introducing a composite key without region/user bucket or salted prefix) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Partitioning purely by timestamp) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-36)

### Question 37
**Answer: A**

**Why Correct:**
- Backpressure signals clients to slow down, queues buffer the load, and circuit breakers protect struggling downstream services, working together to prevent cascading system failures. The correct choice is "Apply backpressure with circuit breakers, queues, and retry policies". This combination of defenses ensures the system degrades gracefully under extreme load rather than failing catastrophically.

**Why Not Distractors:**
- **B**: This distractor (Apply backpressure without circuit breakers, queues, and retry policies) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Scale down compute resources) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Drop the overflowed writes until traffic drops) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-37)

### Question 38
**Answer: B**

**Why Correct:**
- Network unreliability often causes clients to retry requests. Idempotency guarantees that multiple identical requests have the exact same effect as a single one, preventing duplicate transactions. The correct choice is "Tolerate retries and dedupe without corrupting state". This makes it safe for upstream services to blindly retry requests without fear of double-charging users or corrupting internal state.

**Why Not Distractors:**
- **A**: This distractor (Require clients to do extra bookkeeping) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Tolerate retries and dedupe with corrupting state in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Guarantee no duplicate writes even with retries) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-38)

### Question 39
**Answer: A**

**Why Correct:**
- Splitting a large file into chunks allows a failed upload to resume from the last successful chunk rather than starting over, which is essential for massive files over unreliable network connections. The correct choice is "Split the upload into multiple chunked requests tracked by a session coordinator". This drastically improves reliability over unstable networks by only re-uploading the specific chunks that failed, rather than the entire file.

**Why Not Distractors:**
- **B**: This distractor (Upload the entire blob in one synchronous request to the database) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Split the upload into single chunked requests tracked by a session coordinator in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Retry at the network layer without tracking chunks) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-39)

### Question 40
**Answer: A**

**Why Correct:**
- Relational databases are optimized for structured queries, not binary payloads. Storing large blobs degrades performance; they should reside in object storage (like S3) with only metadata in the DB. The correct choice is "Offload payloads to object storage and keep lightweight metadata in the DB". Keeping heavy binary data out of the transactional database ensures that index scans and relational queries remain fast and memory-efficient.

**Why Not Distractors:**
- **B**: This distractor (Cache blobs in memory until a manual download) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Keep blobs in the same table as metadata) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Never offload payloads to object storage and keep lightweight metadata in the DB during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-40)

### Question 41
**Answer: C**

**Why Correct:**
- CDNs cache large media close to users and support HTTP range requests for efficient streaming. Signed URLs ensure secure, authorized access without routing heavy downloads through app servers. The correct choice is "Using CDN/edge caches with range support and signed URLs". This delegates the heavy lifting of serving massive files to specialized edge networks, saving enormous amounts of origin bandwidth.

**Why Not Distractors:**
- **A**: This distractor (Streaming each download directly from the origin object store with no caching) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Forcing users to fetch blobs from the primary database for every request) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Sending blobs as email attachments) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-41)

### Question 42
**Answer: D**

**Why Correct:**
- Signed URLs provide time-bound authorization, while cryptographic checksums (like SHA-256) allow the client to verify that the file was not corrupted or tampered with during transit. The correct choice is "Signed URLs, checksum validation, and metadata tags". This ensures that only authorized users can access the payload, and that the payload itself hasn't been altered maliciously during transfer.

**Why Not Distractors:**
- **A**: This distractor (Assuming that signed URLs, checksum validation, and metadata tags is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Trusting clients to verify integrity offline) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Random identifiers and no validation) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-42)

### Question 43
**Answer: C**

**Why Correct:**
- A centralized queue ensures jobs aren't lost, while lease-based locking prevents multiple workers from executing the same job concurrently and handles worker crashes by letting the lease expire. The correct choice is "A job tracker, durable queue, and lease-based worker coordination". This prevents jobs from being lost if a worker crashes, while ensuring that no two workers process the same task simultaneously.

**Why Not Distractors:**
- **A**: This distractor (Workers retrying independently without centralized status) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that a job tracker, durable queue, and lease-based worker coordination is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Unlimited threads per request with no tracking) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-43)

### Question 44
**Answer: B**

**Why Correct:**
- If a worker crashes, it cannot report failure. Continuous heartbeats prove the worker is alive; if heartbeats cease, the tracker assumes a failure and re-queues the job automatically. The correct choice is "Heartbeats from workers with timeout-based retry logic". If the central tracker stops receiving heartbeats, it can safely assume the worker has died and reassign the lease to a healthy instance.

**Why Not Distractors:**
- **A**: This distractor (Manual emails after timeouts) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Clients polling every second) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Heartbeats from workers without timeout-based retry logic) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-44)

### Question 45
**Answer: A**

**Why Correct:**
- Infinitely retrying a broken job blocks processing capacity. Moving it to a Dead-Letter Queue (DLQ) removes it from the active flow, allowing engineers to manually debug the underlying issue. The correct choice is "Moved to a dead-letter queue for investigation". This prevents poisonous messages from continuously crashing workers and blocking the entire queue from processing healthy traffic.

**Why Not Distractors:**
- **B**: This distractor (Removed entirely from the queue so the system can keep going) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Dropped silently) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Archived without alerting) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-45)

### Question 46
**Answer: A**

**Why Correct:**
- Synchronous blocking leads to dropped connections and timeouts. Returning a task token immediately allows the client to poll a status endpoint asynchronously, keeping the API responsive. The correct choice is "Poll a token that returns the latest status and ETA". This async pattern prevents long-running tasks from tying up HTTP connections and exhausting server resources.

**Why Not Distractors:**
- **B**: This distractor (Trigger the job repeatedly until it finishes) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Hide task status to keep APIs simple) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Never poll a token that returns the latest status and ETA during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-46)

### Question 47
**Answer: B**

**Why Correct:**
- Server-Sent Events (SSE) is ideal for unidirectional server-to-client streaming. It operates over standard HTTP, natively supports auto-reconnection, and avoids the bidirectional overhead of WebSockets. The correct choice is "Server-Sent Events (SSE) with heartbeat and reconnect". For purely unidirectional event streaming, SSE is significantly lighter and easier to scale than maintaining fully bidirectional WebSockets.

**Why Not Distractors:**
- **A**: This distractor (Custom TCP clients for every platform) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Full WebRTC mesh for all updates) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Server-Sent Events (SSE) without heartbeat and reconnect) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-47)

### Question 48
**Answer: A**

**Why Correct:**
- Corporate firewalls often block WebSocket upgrades. A graceful downgrade to SSE or long polling ensures connectivity, while a replay cursor guarantees no messages are lost during the switch. The correct choice is "Downgrade to SSE, then long polling, with replay cursor support". This provides a robust fallback mechanism for restrictive network environments, ensuring that all clients receive updates regardless of firewall rules.

**Why Not Distractors:**
- **B**: This distractor (Keep retrying WebSocket upgrades with no delay) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Disable updates until the client reloads) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Downgrade to SSE, then long polling, without replay cursor support) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-48)

### Question 49
**Answer: C**

**Why Correct:**
- Heartbeats detect dead sockets, caps prevent excessive fanout, and jittered reconnects stagger client retry attempts, protecting the backend from a devastating 'thundering herd' spike after an outage. The correct choice is "Heartbeats, idle timeout, per-connection fanout caps, and jittered reconnect". This comprehensive set of controls prevents a massive wave of reconnecting clients from taking down the backend immediately after a recovery.

**Why Not Distractors:**
- **A**: This distractor (Unlimited idle sockets and no heartbeat) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that heartbeats, idle timeout, per-connection fanout caps, and jittered reconnect is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Disable auth refresh on long-lived sessions) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-49)

### Question 50
**Answer: D**

**Why Correct:**
- Standard pub/sub works for targeted groups, but massive broadcasts (e.g., millions watching a live stream) require edge caching to deduplicate the payload and prevent the fanout layer from collapsing. The correct choice is "Topic-based pub/sub fanout with edge caching for massive broadcasts". This hybrid approach prevents the pub/sub fanout layer from being completely crushed by the sheer volume of a massive broadcast event.

**Why Not Distractors:**
- **A**: This distractor (Direct-send from app servers for all audiences) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Topic-based pub/sub fanout without edge caching for massive broadcasts) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Polling reads from the primary database for all subscribers) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-50)

### Question 51
**Answer: A**

**Why Correct:**
- Optimistic concurrency uses version numbers instead of expensive locks. It allows concurrent reads and only fails writes if a conflict is detected, making it highly efficient for moderate contention. The correct choice is "Optimistic concurrency with bounded retries and idempotency keys". This avoids the massive performance penalties of distributed locks by simply failing and retrying the small percentage of writes that actually conflict.

**Why Not Distractors:**
- **B**: This distractor (Optimistic concurrency without bounded retries and idempotency keys) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Serial queue for all writes across all entities) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Two-phase commit for every update) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-51)

### Question 52
**Answer: D**

**Why Correct:**
- When optimistic concurrency fails repeatedly due to extreme contention on a single key, routing those specific writes through a localized, serialized queue resolves the race conditions safely. The correct choice is "Move hotspot entities to per-key serialized queues". This safely serializes the heavily contended operations without imposing a massive performance penalty on the rest of the system.

**Why Not Distractors:**
- **A**: This distractor (Never move hotspot entities to per-key serialized queues during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Increase retry count and keep strategy unchanged) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Spread writes randomly across shards) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-52)

### Question 53
**Answer: B**

**Why Correct:**
- If a client pauses, its lock lease might expire and be reassigned. Fencing tokens (monotonically increasing IDs) allow the database to explicitly reject delayed writes from the original, expired owner. The correct choice is "Lease expiry plus fencing tokens validated at write boundary". This guarantees that even if a paused client wakes up and attempts a delayed write, the database will reject its expired token.

**Why Not Distractors:**
- **A**: This distractor (Single lock for the entire service domain) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Client-side mutex only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that lease expiry plus fencing tokens validated at write boundary is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-53)

### Question 54
**Answer: C**

**Why Correct:**
- Event choreography becomes a distributed monolith when spanning many services. An orchestrator centralizes the state machine, manages retries, and reliably coordinates compensating rollback transactions. The correct choice is "Multi-step cross-service flows needing retries, compensation, and checkpoints". This centralized control is absolutely necessary to reliably manage distributed transactions, retries, and rollbacks across multiple independent services.

**Why Not Distractors:**
- **A**: This distractor (Assuming that multi-step cross-service flows needing retries, compensation, and checkpoints is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Single-service, single-step operations) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Stateless telemetry ingestion) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-54)

### Question 55
**Answer: C**

**Why Correct:**
- Auctions involve immense contention on a single key (the current highest bid) and strict correctness requirements (only one definitive winner), necessitating bulletproof concurrency control. The correct choice is "Online auction highest-bid update". This is because multiple users might attempt to outbid each other in the exact same millisecond, requiring absolute serialization.

**Why Not Distractors:**
- **A**: This distractor (Daily batch ETL) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that online auction highest-bid update is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Log archive pipeline) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-55)

### Question 56
**Answer: D**

**Why Correct:**
- Live streams demand low-latency push delivery, but mobile networks are flaky. Pairing push with a replay cursor allows reconnecting clients to fetch exactly the comments they missed during the drop. The correct choice is "Real-time push with replay cursor". This ensures that even if a mobile client temporarily loses connectivity, it can seamlessly fetch the exact gap in messages upon reconnecting.

**Why Not Distractors:**
- **A**: This distractor (Offline export only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Full-table DB scans) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Real-time push without replay cursor) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-56)

### Question 57
**Answer: D**

**Why Correct:**
- The relational database (OLTP) must remain the definitive source of truth. The search index should be updated asynchronously via Change Data Capture (CDC) to keep write paths fast and decoupled. The correct choice is "OLTP as source, async index projection". This isolates the critical write path from the heavy, complex indexing requirements of the search infrastructure.

**Why Not Distractors:**
- **A**: This distractor (Search index as only write store) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Client-side index only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that oLTP as source, async index projection is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-57)

### Question 58
**Answer: B**

**Why Correct:**
- Calculating global Top-K continuously over a massive event firehose is computationally unfeasible. Precomputing the ranking periodically in tumbling windows provides fast retrieval at extreme scale. The correct choice is "Precomputed windowed ranking". This allows the system to serve extremely fast read responses without continuously recalculating rankings on every single incoming event.

**Why Not Distractors:**
- **A**: This distractor (Random sampling only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Query-time global scan) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that precomputed windowed ranking is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-58)

### Question 59
**Answer: D**

**Why Correct:**
- Notifications involve checking preferences, formatting, and calling external APIs. A durable multi-step workflow guarantees that the notification process succeeds even if an external provider temporarily fails. The correct choice is "Durable multi-step workflow". This ensures that the entire sequence—evaluating rules, checking preferences, and dispatching messages—is reliably executed even during partial outages.

**Why Not Distractors:**
- **A**: This distractor (Static cron report) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that durable multi-step workflow is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Spreadsheet export job) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-59)

### Question 60
**Answer: B**

**Why Correct:**
- Embedding images directly in the feed payload bloats memory usage and network transfer times. Media belongs in blob storage and should be served via a CDN, keeping API responses extremely lightweight. The correct choice is "Stored/served via blob+CDN path". This keeps the core API responses extremely fast and small, delegating the heavy media transfers to specialized CDN networks.

**Why Not Distractors:**
- **A**: This distractor (Inlined in feed row payload always) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Stored only in relational text columns) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Embedded in cache key) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-60)

### Question 61
**Answer: D**

**Why Correct:**
- Auctions experience massive load spikes in the final milliseconds. Failing to account for network latency, clock drift, and write contention at the exact closing moment leads to incorrect winners. The correct choice is "Ignoring close-time race semantics". This failure mode ignores the reality that network delays could cause a valid bid submitted before the deadline to arrive at the server slightly after.

**Why Not Distractors:**
- **A**: This distractor (Idempotent bid submission) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that ignoring close-time race semantics is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Durable accepted-bid storage) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-61)

### Question 62
**Answer: C**

**Why Correct:**
- Requesting comments since a specific acknowledged cursor (e.g., a message ID) bridges network gaps perfectly, ensuring a reconnecting user doesn't lose context or receive duplicate messages. The correct choice is "Replay from last acknowledged cursor". This guarantees perfect continuity in the comment stream, completely avoiding missing or duplicated messages during network blips.

**Why Not Distractors:**
- **A**: This distractor (Replay from first acknowledged cursor) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Start from newest only, drop gap) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Clear all comments) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-62)

### Question 63
**Answer: B**

**Why Correct:**
- If a cache node crashes and there is no durable backing store or fallback strategy, users will experience empty feeds or catastrophic data loss, severely degrading the core product functionality. The correct choice is "Stale/inconsistent view without recovery path". This means that any cache eviction or node failure will result in permanent data loss, breaking the core functionality of the application.

**Why Not Distractors:**
- **A**: This distractor (Guaranteed ordering) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (No invalidation need) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Stale/inconsistent view with recovery path in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-63)

### Question 64
**Answer: A**

**Why Correct:**
- Viral events generate massive localized spikes. Ingestion nodes must perform local aggregation (combining events before forwarding) to prevent downstream pipelines from choking on a single hot ID. The correct choice is "Partition-aware ingestion with hotspot mitigation". This aggregates the massive volume of identical events at the edge, protecting the central pipelines from being overwhelmed by a single viral entity.

**Why Not Distractors:**
- **B**: This distractor (Disable metrics) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Ignore skew) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Partition-aware ingestion without hotspot mitigation) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-64)

### Question 65
**Answer: C**

**Why Correct:**
- Choosing between displaying the absolute newest posts versus the most relevant (but older) posts dictates entirely different indexing architectures, and this fundamental trade-off must be clearly stated. The correct choice is "Explicitly stated and measured". This clarifies exactly how the system prioritizes recent content versus highly engaging historical content, fundamentally shaping the database schema.

**Why Not Distractors:**
- **A**: This distractor (Hidden from requirements) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Solved only by bigger servers) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that explicitly stated and measured is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-65)

### Question 66
**Answer: C**

**Why Correct:**
- Phased rollouts must pass through automated quality gates (unit testing, integration checks) and verify that documentation matches the new implementation to prevent widespread production breakages. The correct choice is "Batched gates with compile/test + docs parity". This rigorous staged approach catches edge-case regressions early and guarantees that the system remains stable as new features are deployed.

**Why Not Distractors:**
- **A**: This distractor (Skip tests until end) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Update index docs first) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Batched gates without compile/test + docs parity) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-66)

### Question 67
**Answer: A**

**Why Correct:**
- Even with AI generation, engineering fundamentals rule. Defining the problem space, clarifying constraints, and structuring a logical plan are prerequisites before evaluating any generated code. The correct choice is "Clarify requirements and constraints, then phase the plan". This proves that you are driving the engineering process, rather than blindly relying on the AI to guess the implicit constraints of the problem.

**Why Not Distractors:**
- **B**: This distractor (Focus only on prompt style) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Never clarify requirements and constraints, then phase the plan during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Start optimizing complexity immediately) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-67)

### Question 68
**Answer: D**

**Why Correct:**
- Blindly accepting AI code demonstrates a lack of technical ownership. Strong engineers critically evaluate generated output for correctness, edge cases, and performance regressions before integration. The correct choice is "Reviewing each generated change against constraints before accepting". This critical review process ensures that subtle bugs, security flaws, or performance regressions are caught before they enter the codebase.

**Why Not Distractors:**
- **A**: This distractor (Accepting generated code if it compiles) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Reviewing each generated change against constraints after accepting in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Letting AI decide architecture while you narrate) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-68)

### Question 69
**Answer: B**

**Why Correct:**
- Before modifying unfamiliar code, you must understand the existing architecture, map the entry points, and pace the interview phases to ensure the entire feature can be cleanly implemented. The correct choice is "Codebase orientation and phase pacing". This methodical approach prevents you from making chaotic, fragmented changes that fail to integrate cleanly with the overall system.

**Why Not Distractors:**
- **A**: This distractor (Building custom tooling) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Multi-model benchmarking) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that codebase orientation and phase pacing is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-69)

### Question 70
**Answer: C**

**Why Correct:**
- Interviewers evaluate your methodology. Demonstrating a systematic approach, writing robust verification tests, and clearly articulating trade-offs are the strongest signals of senior engineering competence. The correct choice is "Demonstrating structured workflow, verification, and explainability". This highlights the core difference between a junior developer typing code and a senior engineer delivering a fully validated, reliable solution.

**Why Not Distractors:**
- **A**: This distractor (Avoiding tests to move faster) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that demonstrating structured workflow, verification, and explainability is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Deferring architecture decisions to later) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-70)

### Question 71
**Answer: C**

**Why Correct:**
- Understanding how data enters the system and recognizing the rules that must never be violated (invariants) is the most effective way to prevent catastrophic bugs when modifying new code. The correct choice is "Identifying entry flow and key invariants". This guarantees that any modifications you make will respect the fundamental rules of the system, preventing catastrophic data corruption.

**Why Not Distractors:**
- **A**: This distractor (Memorizing all filenames) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Rewriting modules to preferred style) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that identifying entry flow and key invariants is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-71)

### Question 72
**Answer: C**

**Why Correct:**
- AI can generate subtle logical flaws. Manually reading the code, verifying critical boundaries, and running automated test suites form a robust, multi-layered defense against regressions. The correct choice is "Walkthrough + targeted checks + tests". This multi-layered approach provides the necessary confidence that the AI-assisted code is actually correct, robust, and production-ready.

**Why Not Distractors:**
- **A**: This distractor (No verification if code looks correct) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that walkthrough + targeted checks + tests is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Code walkthrough only) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-72)

### Question 73
**Answer: C**

**Why Correct:**
- Narrating your intent before prompting the AI, and summarizing the outcome afterward, proves you are driving the execution. It highlights your leadership and clarity of thought to the interviewer. The correct choice is "Narrate intent before prompt and summarize outcomes after each change". This explicit communication style proves to the interviewer that you are in complete control of the logic and the AI tool.

**Why Not Distractors:**
- **A**: This distractor (Discuss trade-offs only at the end) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Narrate intent after prompt and summarize outcomes after each change in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Read generated code line by line without decisions) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-73)

### Question 74
**Answer: C**

**Why Correct:**
- Submitting unverified code is a critical failure. It is always better to deliver a slightly reduced but fully tested and verified feature than a larger implementation riddled with unhandled bugs. The correct choice is "Final verification checkpoint". This demonstrates a mature understanding that shipping unverified, broken code is significantly worse than shipping a slightly incomplete but stable feature.

**Why Not Distractors:**
- **A**: This distractor (Last optimization brainstorm) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Extra benchmark scenario) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that final verification checkpoint is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-concepts-quiz.md#question-74)
