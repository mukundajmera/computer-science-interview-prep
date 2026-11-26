# Library Management - Common Interview Pitfalls

Common failure patterns and what to do instead.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. Mixing Physical and Logical Entities

- **Pitfall**: Candidates often conflate `BookItem` (a specific physical copy on a shelf) with the abstract `Book` (metadata like ISBN, title, author).
- **Why it hurts**: This leads to massive duplication of book metadata across millions of items and makes global search highly inefficient
- **Better**: Instead, strictly separate `Book` and `BookItem` with a one-to-many relationship.

Detailed explanation: The Mixing Physical and Logical Entities pitfall is
frequently observed when candidates focus solely on the happy path. This
specifically highlights the need for careful resource management in library-
management. Candidates should explicitly mention how they would monitor for this
issue in production using relevant metrics. Furthermore, they should be prepared
to discuss alternative approaches and why this specific solution was chosen for
library-management.

## 2. Concurrency on Book Checkout

- **Pitfall**: Not handling concurrent checkouts of the last available copy.
- **Why it hurts**: If two members simultaneously attempt to borrow the last copy of 'Harry Potter', both might succeed if isolation levels are too low
- **Better**: Implement optimistic locking via version numbers on the `BookItem` or row-level locking using `SELECT FOR UPDATE` to serialize access.

Detailed explanation: The Concurrency on Book Checkout pitfall is frequently
observed when candidates focus solely on the happy path. Addressing this
requires a deep understanding of concurrent execution and lock management.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
library-management.

## 3. Inefficient Search Design

- **Pitfall**: Implementing search by scanning across a massive relational database using `LIKE '%title%'` without proper indexing.
- **Why it hurts**: For a library catalog, this requires full-text search capabilities
- **Better**: Implement a dedicated search index like Elasticsearch, feeding updates asynchronously from the primary transactional database.

Detailed explanation: The Inefficient Search Design pitfall is frequently
observed when candidates focus solely on the happy path. In the context of the
library-management architecture, this component is often a bottleneck under
heavy database load. Candidates should explicitly mention how they would monitor
for this issue in production using relevant metrics. Furthermore, they should be
prepared to discuss alternative approaches and why this specific solution was
chosen for library-management.

## 4. Poor Due Date Calculation

- **Pitfall**: Hardcoding due date logic (e.g., `date + 14 days`) directly inside the checkout service.
- **Why it hurts**: This fails when different member tiers (students vs
- **Better**: faculty) have different lending periods, or when special item types (magazines vs. reference books) have unique rules. Use a Strategy pattern or a Rules Engine to decouple this calculation.

Detailed explanation: The Poor Due Date Calculation pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in library-management.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
library-management.

## 5. Ignoring Fine Payment Concurrency

- **Pitfall**: Race conditions when paying fines and simultaneously updating member status (e.g., unlocking a blocked account).
- **Why it hurts**: If a member pays a fine while a concurrent overdue job adds a new fine, the account might be incorrectly unblocked
- **Better**: Ensure fine payments and account status updates are wrapped in strict, atomic database transactions.

Detailed explanation: The Ignoring Fine Payment Concurrency pitfall is
frequently observed when candidates focus solely on the happy path. In the
context of the library-management architecture, this component is often a
bottleneck under heavy database load. Candidates should explicitly mention how
they would monitor for this issue in production using relevant metrics.
Furthermore, they should be prepared to discuss alternative approaches and why
this specific solution was chosen for library-management.

## 6. Lack of State Machine for BookItem

- **Pitfall**: Relying on arbitrary string statuses or boolean flags (`isBorrowed`, `isLost`) that can enter conflicting states.
- **Why it hurts**: A `BookItem` has a well-defined lifecycle (AVAILABLE -> RESERVED -> LOANED -> LOST/RETURNED)
- **Better**: Enforce this lifecycle using a strict state machine pattern to reject invalid transitions.

Detailed explanation: The Lack of State Machine for BookItem pitfall is
frequently observed when candidates focus solely on the happy path. This
specifically highlights the need for careful resource management in library-
management. Candidates should explicitly mention how they would monitor for this
issue in production using relevant metrics. Furthermore, they should be prepared
to discuss alternative approaches and why this specific solution was chosen for
library-management.

## 7. Incomplete Reservation Logic

- **Pitfall**: Failing to define the lifecycle of a reservation.
- **Why it hurts**: What happens when a reserved book is returned, but the reserver doesn't pick it up within 48 hours? The system must include a background job or TTL mechanism to expire pending reservations and notify the next person in the queue or return the item to circulation.
- **Better**: Adopt a robust standard pattern.

Detailed explanation: The Incomplete Reservation Logic pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in library-management.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
library-management.

## 8. Scalability of Overdue Checks

- **Pitfall**: Designing an overdue notification system that relies on a daily cron job performing a full table scan (`SELECT * FROM loans WHERE dueDate < NOW() AND status = 'ACTIVE'`).
- **Why it hurts**: At scale, this times out
- **Better**: Use secondary indexes on `dueDate` + `status`, or emit delayed messages to a queue (like AWS SQS) at the time of checkout.

Detailed explanation: The Scalability of Overdue Checks pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in library-management.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
library-management.

## 9. No Consideration for Archival

- **Pitfall**: Keeping every historical loan record in the primary operational table.
- **Why it hurts**: As years pass, the `loans` table grows to billions of rows, degrading checkout performance
- **Better**: Old loans should be asynchronously archived to a separate data warehouse.

Detailed explanation: The No Consideration for Archival pitfall is frequently
observed when candidates focus solely on the happy path. This specifically
highlights the need for careful resource management in library-management.
Candidates should explicitly mention how they would monitor for this issue in
production using relevant metrics. Furthermore, they should be prepared to
discuss alternative approaches and why this specific solution was chosen for
library-management.

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

When concluding your design for library-management, always revisit the initial
constraints. If the system was heavily read-optimized, confirm that your caching
strategy supports the expected QPS. If it was write-heavy, ensure your database
partitioning and queuing mechanisms can handle the throughput. Remember that no
system design is perfect; it's about making informed compromises and being able
to defend them intelligently.

Finally, consider the operational aspects. How will you deploy this? How do you
monitor its health? What are the key SLIs (Service Level Indicators) you would
track? A senior engineer not only designs the architecture but also plans for
its long-term maintainability and operability in a production environment.

Note on Database Indexing: Consider this deeply when discussing library-management.
Note on Message Queues: Consider this deeply when discussing library-management.
Note on Caching Strategies: Consider this deeply when discussing library-management.
Note on Load Balancing: Consider this deeply when discussing library-management.
Note on Data Sharding: Consider this deeply when discussing library-management.
Note on Replication Lag: Consider this deeply when discussing library-management.
Note on Eventual Consistency: Consider this deeply when discussing library-management.
Note on ACID Transactions: Consider this deeply when discussing library-management.
Note on Rate Limiting: Consider this deeply when discussing library-management.
Note on Circuit Breakers: Consider this deeply when discussing library-management.
Note on Service Mesh: Consider this deeply when discussing library-management.
Note on Microservices vs Monolith: Consider this deeply when discussing library-management.
Note on API Gateway: Consider this deeply when discussing library-management.
Note on Authentication/Authorization: Consider this deeply when discussing library-management.
Note on Disaster Recovery: Consider this deeply when discussing library-management.
Note on Zero Downtime Deployments: Consider this deeply when discussing library-management.
Note on CI/CD Pipelines: Consider this deeply when discussing library-management.
Note on Monitoring and Alerting: Consider this deeply when discussing library-management.
Note on Log Aggregation: Consider this deeply when discussing library-management.
Note on Distributed Tracing: Consider this deeply when discussing library-management.

Advanced consideration for Network Partitions: How does it impact latency in library-management?
Advanced consideration for Disk I/O: How does it impact latency in library-management?
Advanced consideration for Garbage Collection Pauses: How does it impact latency in library-management?
Advanced consideration for Thread Context Switching: How does it impact latency in library-management?
Advanced consideration for Connection Pooling Limits: How does it impact latency in library-management?
Advanced consideration for DNS Resolution: How does it impact latency in library-management?
Advanced consideration for TLS Handshakes: How does it impact latency in library-management?
Advanced consideration for Serialization Overhead: How does it impact latency in library-management?
Advanced consideration for B-Tree Page Splits: How does it impact latency in library-management?
Advanced consideration for Cache Eviction Spikes: How does it impact latency in library-management?
Advanced consideration for Thundering Herd Problem: How does it impact latency in library-management?
Advanced consideration for Cold Starts: How does it impact latency in library-management?
Advanced consideration for Database Vacuuming: How does it impact latency in library-management?
Advanced consideration for Index Rebuilding: How does it impact latency in library-management?
Advanced consideration for Message Broker Backpressure: How does it impact latency in library-management?
Advanced consideration for Retry Storms: How does it impact latency in library-management?
Advanced consideration for Semantic Versioning: How does it impact latency in library-management?
Advanced consideration for Feature Flags: How does it impact latency in library-management?
Advanced consideration for Chaos Engineering: How does it impact latency in library-management?
Advanced consideration for Performance Benchmarking: How does it impact latency in library-management?
