# Linkedin Connection - Common Interview Pitfalls

Common failure patterns and what to do instead.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. Using a standard RDBMS for the massive Connection Graph

- **Pitfall**: Storing edges in a SQL table and attempting to traverse 2nd or 3rd degree connections using recursive CTEs or multiple JOINs.
- **Why it hurts**: This becomes exponentially slow
- **Better**: Graph databases (like Neo4j) or highly optimized NoSQL adjacency lists are mandatory for this scale.

Detailed explanation: The Using a standard RDBMS for the massive Connection
Graph pitfall is frequently observed when candidates focus solely on the happy
path. In the context of the linkedin-connection architecture, this component is
often a bottleneck under heavy database load. Candidates should explicitly
mention how they would monitor for this issue in production using relevant
metrics. Furthermore, they should be prepared to discuss alternative approaches
and why this specific solution was chosen for linkedin-connection.

## 2. Bidirectional vs Unidirectional Confusion

- **Pitfall**: Treating connections identically to Twitter followers.
- **Why it hurts**: LinkedIn connections require mutual consent (bidirectional), whereas follows are unidirectional
- **Better**: Modeling connections strictly as unidirectional edges without a 'status' complicates mutual queries.

Detailed explanation: The Bidirectional vs Unidirectional Confusion pitfall is
frequently observed when candidates focus solely on the happy path. This
specifically highlights the need for careful resource management in linkedin-
connection. Candidates should explicitly mention how they would monitor for this
issue in production using relevant metrics. Furthermore, they should be prepared
to discuss alternative approaches and why this specific solution was chosen for
linkedin-connection.

## 3. Synchronous Path Finding

- **Pitfall**: Attempting to compute 'degrees of separation' (shortest path) synchronously during a profile page load.
- **Why it hurts**: Pathfinding in massive social graphs is computationally heavy and must be pre-computed, bounded (max depth 3), or executed asynchronously.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Synchronous Path Finding pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in linkedin-connection.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
linkedin-connection.

## 4. Ignoring Caching for 1st-degree Connections

- **Pitfall**: Hitting the primary database every time a user views a profile to check if they are connected.
- **Why it hurts**: 1st-degree connections are read frequently and updated infrequently; they must be cached aggressively in memory (e.g., Redis).
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Ignoring Caching for 1st-degree Connections pitfall is
frequently observed when candidates focus solely on the happy path. In the
context of the linkedin-connection architecture, this component is often a
bottleneck under heavy database load. Candidates should explicitly mention how
they would monitor for this issue in production using relevant metrics.
Furthermore, they should be prepared to discuss alternative approaches and why
this specific solution was chosen for linkedin-connection.

## 5. Poor Pagination Implementation

- **Pitfall**: Returning thousands of connections in a single API call, or using offset-based pagination (`LIMIT 50 OFFSET 10000`) which becomes terribly slow as the offset grows.
- **Why it hurts**: Cursor-based pagination using connection timestamps is essential.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Poor Pagination Implementation pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in linkedin-connection.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
linkedin-connection.

## 6. Missing Connection States

- **Pitfall**: Modeling connections merely by their existence in a table.
- **Why it hurts**: A connection process involves states: PENDING, ACCEPTED, BLOCKED
- **Better**: Failing to model these states leads to bugs where users can send infinite pending requests.

Detailed explanation: The Missing Connection States pitfall is frequently
observed when candidates focus solely on the happy path. Addressing this
requires a deep understanding of concurrent execution and lock management.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
linkedin-connection.

## 7. Race Conditions in Requests

- **Pitfall**: Two users (Alice and Bob) sending connection requests to each other at the exact same millisecond.
- **Why it hurts**: Without unique constraints on the undirected pair `(min(id1, id2), max(id1, id2))`, the system might create two separate pending request records.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Race Conditions in Requests pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in linkedin-connection.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
linkedin-connection.

## 8. Inefficient Feed Generation via Pull

- **Pitfall**: Attempting to generate a user's news feed by synchronously querying the recent activities of all 500+ connections at read-time.
- **Why it hurts**: This fan-out-on-read approach fails under load; a hybrid or push-based feed architecture is required.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Inefficient Feed Generation via Pull pitfall is
frequently observed when candidates focus solely on the happy path. This
specifically highlights the need for careful resource management in linkedin-
connection. Candidates should explicitly mention how they would monitor for this
issue in production using relevant metrics. Furthermore, they should be prepared
to discuss alternative approaches and why this specific solution was chosen for
linkedin-connection.

## 9. No Handling of Graph Hotspots

- **Pitfall**: Failing to address nodes with an extremely high degree of connectivity (influencers).
- **Why it hurts**: Unbounded fan-out operations on these nodes will crash message queues or overload cache clusters.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The No Handling of Graph Hotspots pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in linkedin-connection.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
linkedin-connection.

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

When concluding your design for linkedin-connection, always revisit the initial
constraints. If the system was heavily read-optimized, confirm that your caching
strategy supports the expected QPS. If it was write-heavy, ensure your database
partitioning and queuing mechanisms can handle the throughput. Remember that no
system design is perfect; it's about making informed compromises and being able
to defend them intelligently.

Finally, consider the operational aspects. How will you deploy this? How do you
monitor its health? What are the key SLIs (Service Level Indicators) you would
track? A senior engineer not only designs the architecture but also plans for
its long-term maintainability and operability in a production environment.

Note on Database Indexing: Consider this deeply when discussing linkedin-connection.
Note on Message Queues: Consider this deeply when discussing linkedin-connection.
Note on Caching Strategies: Consider this deeply when discussing linkedin-connection.
Note on Load Balancing: Consider this deeply when discussing linkedin-connection.
Note on Data Sharding: Consider this deeply when discussing linkedin-connection.
Note on Replication Lag: Consider this deeply when discussing linkedin-connection.
Note on Eventual Consistency: Consider this deeply when discussing linkedin-connection.
Note on ACID Transactions: Consider this deeply when discussing linkedin-connection.
Note on Rate Limiting: Consider this deeply when discussing linkedin-connection.
Note on Circuit Breakers: Consider this deeply when discussing linkedin-connection.
Note on Service Mesh: Consider this deeply when discussing linkedin-connection.
Note on Microservices vs Monolith: Consider this deeply when discussing linkedin-connection.
Note on API Gateway: Consider this deeply when discussing linkedin-connection.
Note on Authentication/Authorization: Consider this deeply when discussing linkedin-connection.
Note on Disaster Recovery: Consider this deeply when discussing linkedin-connection.
Note on Zero Downtime Deployments: Consider this deeply when discussing linkedin-connection.
Note on CI/CD Pipelines: Consider this deeply when discussing linkedin-connection.
Note on Monitoring and Alerting: Consider this deeply when discussing linkedin-connection.
Note on Log Aggregation: Consider this deeply when discussing linkedin-connection.
Note on Distributed Tracing: Consider this deeply when discussing linkedin-connection.

Advanced consideration for Network Partitions: How does it impact latency in linkedin-connection?
Advanced consideration for Disk I/O: How does it impact latency in linkedin-connection?
Advanced consideration for Garbage Collection Pauses: How does it impact latency in linkedin-connection?
Advanced consideration for Thread Context Switching: How does it impact latency in linkedin-connection?
Advanced consideration for Connection Pooling Limits: How does it impact latency in linkedin-connection?
Advanced consideration for DNS Resolution: How does it impact latency in linkedin-connection?
Advanced consideration for TLS Handshakes: How does it impact latency in linkedin-connection?
Advanced consideration for Serialization Overhead: How does it impact latency in linkedin-connection?
Advanced consideration for B-Tree Page Splits: How does it impact latency in linkedin-connection?
Advanced consideration for Cache Eviction Spikes: How does it impact latency in linkedin-connection?
Advanced consideration for Thundering Herd Problem: How does it impact latency in linkedin-connection?
Advanced consideration for Cold Starts: How does it impact latency in linkedin-connection?
Advanced consideration for Database Vacuuming: How does it impact latency in linkedin-connection?
Advanced consideration for Index Rebuilding: How does it impact latency in linkedin-connection?
Advanced consideration for Message Broker Backpressure: How does it impact latency in linkedin-connection?
Advanced consideration for Retry Storms: How does it impact latency in linkedin-connection?
Advanced consideration for Semantic Versioning: How does it impact latency in linkedin-connection?
Advanced consideration for Feature Flags: How does it impact latency in linkedin-connection?
Advanced consideration for Chaos Engineering: How does it impact latency in linkedin-connection?
Advanced consideration for Performance Benchmarking: How does it impact latency in linkedin-connection?
