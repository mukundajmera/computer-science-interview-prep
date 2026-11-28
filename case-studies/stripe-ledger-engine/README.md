# Stripe Ledger Engine Case Study

## 1. Problem Statement

At its core, Stripe is a money movement company. The foundation of any money movement platform is the ledger—a system of record that tracks every single cent that moves through the system. 
As Stripe grew from a simple payment processor to a complex financial platform supporting millions of businesses, the volume and complexity of transactions exploded.

### Business Challenge
Stripe needs to process thousands of transactions per second, reliably track the flow of funds across thousands of currencies and financial products, and guarantee absolute correctness. Losing a transaction or recording a fractional cent incorrectly is catastrophic. The system must provide real-time balances to users while strictly adhering to financial accounting standards.

### Technical Requirements
- **Absolute Accuracy (Correctness):** No lost transactions, no double-counting, zero precision loss.
- **High Throughput & Low Latency:** Must handle thousands of API requests per second with minimal latency for authorization and balance checks.
- **Idempotency:** Network failures and retries must never result in duplicate money movement.
- **Auditability:** Every state change must be traceable and justifiable.
- **Scalability:** The architecture must scale horizontally as payment volume grows globally.

### Scale Metrics
- **Volume:** Millions of transactions processed daily.
- **Throughput:** High thousands of transactions per second (TPS) globally.
- **Data Size:** Petabytes of transaction data stored securely.
- **Availability:** 99.999% uptime required for critical paths.
- **Consistency:** Strict serializability for core financial records.

---

## 2. Architecture Evolution

Stripe's ledger evolved through several phases as the company scaled.

### Phase 1: Simple Database Tables
Initially, Stripe used standard relational database tables to track transactions. Balances were calculated by summing up transaction rows.
- **Pros:** Simple, easy to understand.
- **Cons:** Slow balance queries as data grew. Risk of database contention and deadlocks under high concurrency. No strict double-entry guarantees built-in.

### Phase 2: Denormalized Balances
To solve the slow read problem, balances were materialized in separate tables and updated alongside transaction inserts.
- **Pros:** Fast balance reads.
- **Cons:** Race conditions. Keeping transactions and materialized balances in sync required complex distributed transactions or risked inconsistencies.

### Phase 3: The Event-Sourced Ledger Engine (Current)
Stripe built a dedicated Ledger Engine based on event sourcing, double-entry bookkeeping, and immutable logs.
- **Transactions** are written to an append-only log.
- **Balances** are derived from this log and snapshotted periodically.
- **Idempotency** is enforced at the edge of the ledger.

## 📊 Diagrams

- [Architecture: write and read paths](diagrams/architecture.mmd) - idempotency key check, double-entry validation, the immutable ledger write, and the snapshot-plus-replay read path.

---

---

## 3. Core Accounting Invariant

The fundamental principle governing the ledger is the **Double-Entry Bookkeeping** model. Every transaction must have at least two entries (legs): a debit to one account and a credit to another.

### The Accounting Equation
`Assets = Liabilities + Equity`

Or, more simply in a transactional context:
`Sum(Debits) + Sum(Credits) = 0`

If a user deposits $10, the system must debit a cash account (increasing asset) and credit the user's balance account (increasing liability) by exactly $10. The transaction is instantly rejected if the sum of all legs does not equal exactly zero.

### Currency Handling
Financial systems cannot use standard floating-point arithmetic (`float` or `double`). Floating-point representations introduce rounding errors (e.g., `0.1 + 0.2 = 0.30000000000000004`).
- **Integer Cents / Nanos:** All currency values are stored as 64-bit integers representing the smallest unit of the currency (e.g., cents for USD, yen for JPY).
- **Strict Zero Floating-Point:** Any calculation involving money is performed using integer math or arbitrary-precision decimal libraries (like `BigDecimal`). Floating-point types are strictly banned in the ledger codebase.

---

## 4. Idempotency & Concurrency

Money movement APIs are called over unreliable networks. Clients will inevitably retry requests. The ledger must guarantee exactly-once processing.

### Idempotency Key Mechanics
Stripe utilizes idempotency keys extensively.
1. **Client Provides Key:** The API client sends an `Idempotency-Key` header with their request.
2. **First-Party Unique Constraint Tables:** The ledger maintains a dedicated table to track idempotency keys. This table has a unique constraint on the key.
3. **Locking Window:** When a request arrives, the ledger attempts to insert the key. If successful, it holds a lock for a short window while processing the transaction.
4. **Deterministic Replay:** If a request with an existing key is received, the ledger checks the state. If the original transaction completed, the ledger deterministically replays the exact same response payload without executing any financial side-effects.

### Optimistic Concurrency Control
To handle concurrent transactions on the same account (e.g., a rapid series of purchases), the ledger uses Optimistic Concurrency Control (OCC) instead of heavy pessimistic locks.
- **Sequence Numbers / Versions:** Every account balance has a monotonically increasing sequence number (or version).
- **Update Logic:** When a transaction modifies a balance, it reads the current sequence number (e.g., `v10`). It computes the new balance. The update statement is:
  `UPDATE balances SET amount = new_amount, version = v11 WHERE account_id = X AND version = v10`
- **Conflict Resolution:** If another transaction modified the balance in the meantime, the version will have changed (to `v11`), and the `UPDATE` will affect 0 rows. The ledger engine detects this and retries the transaction from the beginning.

---

## 5. Event Sourcing & Balance Materialization

The ledger's source of truth is an immutable, append-only log of transactions.

### Immutable Append-Only Log
- Every money movement is modeled as an immutable event (a ledger entry).
- These events are written to a highly durable, append-only database.
- **Why?** Immutability guarantees auditability. You can never delete or update a past transaction. To fix a mistake, you must post a reversing transaction.

### Balance Materialization
Calculating a balance by summing millions of rows on every API read is too slow.
- **Snapshots:** The system periodically rolls up the event log and creates a snapshot of the balance at a specific point in time or sequence number.
- **Read Path:** When a user queries their balance, the system fetches the latest snapshot and replays only the small number of events that occurred after the snapshot.
- This design decouples the high-throughput write path (appending to the log) from the low-latency read path (serving balances).

---

## 6. Reconciliation & Auditing

Internal consistency is not enough. Stripe must also ensure that its internal ledger matches the external reality of the banking system.

### Automated Continuous Reconciliation
Stripe employs automated systems that continuously reconcile internal ledger entries with external bank settlement files.
1. **Data Ingestion:** Bank statements, ACH settlement files, and network (Visa/Mastercard) reports are ingested daily.
2. **Matching Engine:** A rule-based engine attempts to match every external transaction line item to an internal ledger entry.
3. **Exceptions Management:** If a discrepancy is found (e.g., the bank reports a $10 fee but Stripe recorded $9), an alert is generated for a manual operational review.
- This continuous process ensures that internal bugs do not silently leak money over time.

---

## 7. Key Design Decisions & Technologies

| Component | Technology / Concept | Rationale |
| :--- | :--- | :--- |
| **Core Database** | Horizontally Scalable RDBMS (e.g., distributed PostgreSQL, Citus, or Spanner-like systems) | Requires strict ACID semantics, strong consistency, and secondary index support. |
| **Idempotency Store** | Redis + RDBMS fallback | Redis provides ultra-fast `SETNX` for the initial locking window, while the RDBMS provides durable, long-term storage of idempotency keys and response payloads. |
| **Event Bus** | Kafka | High-throughput, durable log for publishing ledger events to downstream consumers (analytics, webhooks, reporting). |
| **Types** | `int64` / `BigDecimal` | Absolute precision required for currency. |

---

## 8. Trade-offs Made

1. **Write Latency vs. Throughput:** Implementing strong consistency, idempotency checks, and OCC adds latency to the write path. However, it guarantees correctness, which is non-negotiable. Throughput is achieved via horizontal sharding of independent accounts.
2. **Storage Cost vs. Auditability:** Event sourcing (never deleting data) requires massive storage. This is a worthwhile trade-off for perfect auditability and the ability to travel back in time to debug financial discrepancies.
3. **Optimistic vs. Pessimistic Locking:** OCC fails and requires retries under high contention (e.g., a single hot account receiving thousands of micro-deposits). Pessimistic locking would serialize these, but would destroy overall system throughput and increase deadlock risk. OCC was chosen for general performance, with batching strategies used for hot accounts.

---

## 9. Lessons Learned

- **Design for Failure:** Assume clients will retry. Assume networks will drop packets. Idempotency is not a nice-to-have; it is the foundation of a reliable API.
- **Immutability is Powerful:** Append-only architectures make debugging, auditing, and scaling significantly easier.
- **Money is Complex:** Handling multi-currency routing, exchange rates, and fractional cents requires meticulous attention to detail and rigorous automated testing.
- **Reconcile Early and Often:** Do not wait for end-of-month accounting to find discrepancies. Continuous reconciliation limits exposure.

---

## 10. Staff Interview Questions & Scoring Rubrics

### Question 1: Idempotency Under Pressure
**Prompt:** A client sends a payment request with `Idempotency-Key: A`. Our ledger receives it, starts processing, but the database connection drops right before committing. The client times out and retries with `Idempotency-Key: A`. Walk me through the exact sequence of events to ensure we do not charge the user twice.

**Scoring Rubric:**
- **Red Flags (Fail):** Uses the client's payload hash instead of the provided key. Forgets to lock the key. Doesn't distinguish between a "processing" state and a "completed" state.
- **Acceptable (Pass):** Mentions a database table with a unique constraint on the key. Describes checking the table first. Explains that the second request must be rejected or queued until the first one resolves.
- **Excellent (Strong Hire):** Details a multi-phase state machine (e.g., `STARTED`, `COMPLETED`, `FAILED`). Explains that the first request writes `STARTED`. The second request sees `STARTED` and returns a 409 Conflict (or blocks). Details how to handle the edge case where the database commit fails but the `STARTED` record persists (requires an expiration or lease timeout on the lock).

### Question 2: The Hot Account Problem
**Prompt:** We have a massive marketplace platform (like Uber) acting as a single entity on our ledger. Millions of riders are paying this one platform account simultaneously. If we use Optimistic Concurrency Control (OCC), most of these transactions will fail due to version conflicts. How do we design the ledger to handle this high-contention "hot account"?

**Scoring Rubric:**
- **Red Flags (Fail):** Suggests switching the entire system to pessimistic table locks (will kill throughput). Suggests disabling consistency checks.
- **Acceptable (Pass):** Identifies that OCC breaks down under high contention. Suggests sharding the hot account (e.g., `Uber_Balance_1`, `Uber_Balance_2`, etc.) and aggregating them on read.
- **Excellent (Strong Hire):** Proposes asynchronous batching or a write-ahead log pattern. Instead of updating the core balance synchronously on every ride, append the credit to a high-throughput queue/log. A background worker (or micro-batch process) reads the queue, aggregates the credits (e.g., "add $10,000 for 1,000 rides"), and updates the core ledger balance once every second, drastically reducing the update rate and avoiding OCC conflicts entirely.

### Question 3: Precision and Currency
**Prompt:** We are expanding to support fractional cents (e.g., for gas station pricing or API usage billing, where an API call costs $0.0015). How do you alter the database schema and application code to support this without losing precision?

**Scoring Rubric:**
- **Red Flags (Fail):** Suggests changing the database column to `FLOAT` or `DOUBLE`.
- **Acceptable (Pass):** Suggests using a `DECIMAL(precision, scale)` type in the database and `BigDecimal` in code.
- **Excellent (Strong Hire):** Suggests sticking to integer arithmetic but changing the base unit. Introduces the concept of "nanos" or "micro-cents" (e.g., storing $1.00 as 1000000). Explains how to handle the presentation layer (displaying to the user) vs. the storage layer, and explicitly details rounding rules (e.g., Bankers' Rounding) when aggregating micro-transactions for final billing.

---

## 11. Interview Relevance

- **Fintech Interviews:** Mandatory reading for companies like Stripe, Square, Plaid, Robinhood, or any banking institution.
- **E-commerce & Marketplaces:** Highly relevant for Amazon, Airbnb, Uber, where tracking balances, payouts, and seller accounts is critical.
- **Distributed Systems:** A masterclass in applying exactly-once semantics, idempotency, and strict serializability to a real-world, high-stakes problem.

---

*End of Case Study*

### Additional Context: Handling Distributed Transactions
In a distributed microservices environment, a single user action might span multiple systems. For example, charging a credit card via the Payment Gateway and then updating the Ledger.
1. **Saga Pattern:** Stripe heavily utilizes the Saga pattern or similar choreographed/orchestrated distributed transaction models to ensure consistency across service boundaries without relying on 2PC (Two-Phase Commit).
2. **Reversals:** If a downstream service fails after an upstream service has committed, a compensating transaction (reversal) is issued to undo the work. The ledger must natively support linking original entries to their subsequent reversals for auditing.

### Advanced Topics: The Balance Rollup
As the append-only log grows to billions of entries, materializing balances from scratch becomes computationally infeasible.
- **Continuous Rollups:** Background jobs continuously aggregate ledger entries. Instead of scanning from the beginning of time, they start from the last known snapshot.
- **Temporal Queries:** This architecture allows querying a balance "as of" any historical timestamp, which is vital for month-end financial reporting and dispute resolution.

### System Scalability Deep Dive
1. **Sharding by Account ID:** To achieve high throughput, the ledger database is horizontally sharded. The `account_id` is typically the shard key, ensuring that all transactions for a given account reside on the same physical node.
2. **Cross-Shard Transactions:** If a transaction involves two accounts on different shards (e.g., a transfer between two users), the system must orchestrate a distributed transaction. This often involves a multi-step process or a coordinator node to ensure atomic commitment across shards.
3. **Read Replicas:** Read queries for historical data and balance checks are offloaded to read replicas to reduce load on the primary writer nodes.

### Security and Compliance
Financial systems are prime targets for attacks and must adhere to strict regulatory standards (e.g., PCI DSS, SOX).
- **Immutability as Security:** The append-only nature of the ledger protects against malicious tampering. An attacker cannot simply UPDATE a balance; they must insert a new event, which leaves a permanent audit trail.
- **Access Controls:** Strict Role-Based Access Control (RBAC) ensures that only authorized services and personnel can write to or read from the ledger.
- **Encryption:** All data at rest and in transit is encrypted using strong cryptographic algorithms.

### Multi-Region Availability
To ensure 99.999% uptime, the ledger engine must survive whole-region failures.
- **Active-Passive vs Active-Active:** Depending on the specific requirements, Stripe might deploy the ledger in an Active-Passive or Active-Active configuration across multiple geographical regions.
- **Synchronous Replication:** For critical financial data, synchronous replication across availability zones within a region is often used to guarantee zero data loss, though it incurs a latency penalty.
- **Failover Mechanisms:** Automated failover systems monitor the health of the primary region and seamlessly promote a standby region in case of a catastrophic failure.

### Performance Tuning
- **Connection Pooling:** Services communicating with the ledger use connection pooling to minimize the overhead of establishing new database connections.
- **Query Optimization:** Database queries are heavily optimized, with careful indexing on `account_id`, `idempotency_key`, and timestamps.
- **Caching Strategies:** While core balances must be read from the source of truth, certain immutable metadata or frequently accessed reference data might be cached in Redis or Memcached to reduce database load.

### Future Architectural Directions
- **Streaming Analytics:** Real-time processing of the ledger event stream using tools like Apache Flink or Spark Streaming for fraud detection, risk assessment, and real-time reporting.
- **Machine Learning Integration:** Leveraging historical ledger data to train ML models for predicting payment failures, detecting anomalies, and optimizing routing strategies.
- **Serverless Compute:** Exploring serverless architectures for processing asynchronous ledger tasks and event-driven workloads to improve resource utilization and scalability.

### Conclusion
Building a ledger engine at Stripe's scale is a monumental engineering challenge. It requires a deep understanding of distributed systems, database internals, and financial accounting principles. By prioritizing absolute correctness, embracing idempotency, and leveraging an event-sourced architecture, Stripe has built a resilient and scalable foundation for global money movement.

---

## 12. Deep Dive: Handling Failure Scenarios

### Network Partitions
In a distributed system, network partitions are inevitable. The ledger engine must handle them gracefully without compromising correctness.
- **CAP Theorem Trade-offs:** The ledger prioritizes Consistency and Partition Tolerance (CP) over Availability (AP) during a partition. If a node cannot communicate with the majority of the cluster, it will refuse writes to prevent split-brain scenarios and data inconsistencies.
- **Quorum Reads and Writes:** Distributed databases underlying the ledger often use quorum-based replication to ensure strong consistency. A write must be acknowledged by a majority of nodes before being considered successful.

### Database Node Failures
Hardware failures and software crashes can bring down database nodes.
- **Automated Failover:** When a primary node fails, a secondary node is automatically promoted to primary. The ledger engine uses distributed consensus algorithms (e.g., Raft or Paxos) to elect a new leader and ensure a smooth transition.
- **Data Durability:** The append-only log ensures that committed transactions are not lost even if a node crashes immediately after acknowledging a write.

### Upstream Service Outages
The ledger engine often depends on upstream services (e.g., identity verification, fraud detection).
- **Circuit Breakers:** If an upstream service is experiencing high latency or failure rates, circuit breakers trip to prevent cascading failures. The ledger might reject transactions or process them in a degraded mode depending on the criticality of the upstream dependency.
- **Fallback Mechanisms:** In some cases, the ledger might use fallback mechanisms or cached data to continue processing transactions when an upstream service is unavailable.

### Data Corruption
While rare, data corruption can occur due to hardware faults or software bugs.
- **Checksums:** The ledger engine uses checksums to verify the integrity of data at rest and in transit.
- **Regular Backups:** Automated, point-in-time backups allow the ledger to be restored to a known good state in the event of catastrophic data corruption.

### Operational Mistakes
Human error is a significant source of outages.
- **Infrastructure as Code:** All infrastructure changes are managed through code and reviewed before deployment.
- **Canary Deployments:** New versions of the ledger engine are gradually rolled out to a small subset of traffic to detect regressions before full deployment.
- **Rollback Plans:** Every deployment has a clear rollback plan to quickly revert to the previous version if issues arise.

---

## 13. Deep Dive: Monitoring and Observability

To maintain high availability and performance, the ledger engine requires comprehensive monitoring and observability.

### Metrics and Dashboards
- **Throughput:** Transactions per second (TPS) processed by the ledger.
- **Latency:** P50, P90, and P99 latency for API requests and database queries.
- **Error Rates:** Number of failed transactions, idempotency conflicts, and OCC retries.
- **System Health:** CPU, memory, and disk utilization of database nodes and application servers.
- **Business Metrics:** Total payment volume, number of active accounts, and reconciliation discrepancies.

### Distributed Tracing
- **Request Tracking:** Every transaction is assigned a unique trace ID, allowing engineers to track its path across multiple microservices and identify bottlenecks or points of failure.
- **Performance Bottlenecks:** Distributed tracing helps pinpoint performance bottlenecks in the distributed transaction workflow.

### Log Aggregation and Alerting
- **Centralized Logging:** All application and database logs are aggregated in a centralized system for easy searching and analysis.
- **Automated Alerts:** Engineers configure automated alerts based on critical metrics (e.g., a sudden spike in error rates or a drop in throughput). Alerts are routed to the on-call engineer via PagerDuty or similar tools.
- **Anomaly Detection:** Machine learning algorithms monitor metrics for anomalous patterns and trigger alerts before issues escalate into major outages.

### Incident Response
- **Runbooks:** Detailed runbooks provide step-by-step instructions for handling common incidents and troubleshooting complex issues.
- **Post-Mortems:** After every major incident, the team conducts a blameless post-mortem to identify root causes and implement preventative measures.

---

## 14. Deep Dive: The Role of the Event Bus

The event bus is a crucial component of the ledger architecture, enabling asynchronous communication and decoupling services.

### Event Publishing
- **Transaction Events:** Whenever a transaction is committed to the ledger, an event is published to the event bus. This event contains all the relevant details, such as the `account_id`, `amount`, `currency`, and `timestamp`.
- **At-Least-Once Delivery:** The event bus guarantees at-least-once delivery of events to all subscribed services.

### Downstream Consumers
- **Notifications Service:** Subscribes to transaction events and sends email or push notifications to users.
- **Reporting Service:** Subscribes to events and aggregates data for financial reporting and analytics.
- **Fraud Detection:** Subscribes to events and analyzes transaction patterns to detect fraudulent activity in real-time.
- **Webhooks Service:** Subscribes to events and triggers webhooks to external partner systems.

### Event Schema Evolution
- **Schema Registry:** A schema registry is used to manage and version event schemas. This ensures backward and forward compatibility as schemas evolve over time.
- **Protobuf or Avro:** Events are typically serialized using efficient binary formats like Protocol Buffers or Avro to minimize payload size and improve parsing performance.

### Handling Poison Pills
- **Dead Letter Queues (DLQs):** If a consumer repeatedly fails to process an event (e.g., due to a bug or an invalid payload), the event is moved to a DLQ for manual inspection and reprocessing. This prevents the consumer from getting stuck on a "poison pill" event.

---

## 15. Deep Dive: Testing the Ledger Engine

Testing a financial ledger requires rigorous and comprehensive methodologies.

### Unit Testing
- **Business Logic:** Extensive unit tests verify the correctness of the double-entry bookkeeping rules, currency conversions, and idempotency checks.
- **Mocking:** External dependencies and database interactions are mocked to isolate the core logic.

### Integration Testing
- **Database Interactions:** Integration tests verify that the ledger correctly interacts with the underlying database, including transaction commits, rollbacks, and OCC conflict resolution.
- **Event Publishing:** Tests ensure that events are correctly published to the event bus when transactions are processed.

### End-to-End (E2E) Testing
- **User Flows:** E2E tests simulate complete user flows, such as creating an account, depositing funds, making a payment, and checking the balance.
- **API Contracts:** Tests verify that the ledger API adheres to its documented contracts and returns appropriate HTTP status codes and error messages.

### Property-Based Testing
- **Invariant Checking:** Property-based testing generates a wide range of random inputs and verifies that fundamental invariants hold true. For example, testing that `Sum(Debits) + Sum(Credits) = 0` for any randomly generated sequence of valid transactions.

### Chaos Engineering
- **Fault Injection:** Chaos engineering involves intentionally injecting faults into the system to verify its resilience. This might include simulating network partitions, killing database nodes, or injecting latency into upstream dependencies.
- **Game Days:** The team regularly conducts "Game Days" to practice incident response and validate the effectiveness of runbooks and failover mechanisms.

### Shadow Testing
- **Production Traffic:** In shadow testing, a new version of the ledger is deployed alongside the production version. It receives a copy of real production traffic, but its outputs are not returned to the user or committed to the database. The results are compared against the production version to detect regressions or discrepancies before full deployment.

---

## 16. Summary

The Stripe Ledger Engine is a masterclass in distributed systems design, financial engineering, and operational excellence. By adhering to strict accounting principles, embracing idempotency and immutability, and leveraging modern database technologies, Stripe has built a highly reliable, scalable, and auditable system that powers millions of businesses worldwide.

The architecture evolution from simple tables to an event-sourced ledger highlights the challenges of scaling a financial platform and the importance of continuous refinement. The deep dives into failure scenarios, observability, and testing demonstrate the rigorous engineering practices required to maintain a 99.999% uptime and ensure absolute correctness in every transaction.

## 17. The Role of Replay and Rollback

In any complex distributed system dealing with financial transactions, the ability to replay events and rollback state is critical for disaster recovery, debugging, and auditing.

### Deterministic Replay
- **Event Log as Source of Truth:** Because the ledger is event-sourced, the append-only log contains the entire history of state changes.
- **Rebuilding State:** If a balance snapshot is corrupted or lost, the system can deterministically rebuild the exact balance by replaying the event log from the beginning of time (or from the last known good snapshot).
- **Debugging:** Engineers can replay a specific sequence of events in a staging environment to reproduce bugs and verify fixes without touching production data.

### Rollback Mechanisms
- **Compensating Transactions:** In an immutable ledger, you cannot simply `DELETE` a row. If a transaction was recorded in error (e.g., a fraudulent charge), a compensating transaction must be issued to reverse the effect.
- **Automated Reversals:** The system often includes automated workflows for common reversal scenarios, such as refunds or chargebacks, ensuring that the double-entry invariant is maintained during the rollback process.
- **Audit Trail:** Compensating transactions provide a clear audit trail of corrections, which is essential for compliance and financial reporting.

## 18. Continuous Improvement

Stripe's engineering culture emphasizes continuous improvement and learning from incidents. The ledger engine is constantly evolving to handle new product requirements, larger scale, and emerging edge cases.
- **Performance Profiling:** Continuous profiling of the application and database layers identifies new bottlenecks as workload patterns change.
- **Capacity Planning:** Rigorous capacity planning ensures that the infrastructure is always provisioned ahead of projected growth, preventing resource exhaustion during peak traffic events (e.g., Black Friday).

---

## Related Repo Content

### Similar HLD Projects
- [Payment System](../../04-hld-projects/payment-system/)
- [Digital Wallet & Transactional Ledger - Problem Statement](../../04-hld-projects/digital-wallet/)
- [Stock Exchange Matching Engine](../../04-hld-projects/stock-exchange-matching-engine/)
