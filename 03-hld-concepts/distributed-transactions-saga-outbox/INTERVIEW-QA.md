# Distributed Transactions: Interview Q&A

This document contains 10 Staff-level interview questions focusing on partial failure modes, isolation anomalies, and advanced handling in SAGA and Outbox architectures.

## 1. How do you prevent "Dirty Reads" in a Saga, considering local transactions commit immediately?
**Answer:**
Sagas lack global read isolation (ACID isolation). To prevent dirty reads, we implement **Semantic Locks**. For instance, instead of immediately transitioning a record to an active state, it is placed in a `PENDING` state while the Saga is in progress. Concurrent operations reading this record must be programmed to handle or reject operations on `PENDING` records. Alternatively, we use a pessimistic approach where concurrent requests are blocked or delayed until the Saga clears the lock by marking the state as `COMPLETED` or `CANCELLED`.

> Say: "We use semantic locks by introducing explicit intermediate states, such as `PENDING_FUNDS_TRANSFER`, so that concurrent transactions know an operation is in flight and do not read a dirty, potentially compensable state."

## 2. In a Saga, what is a "Pivot Transaction" and why is it architecturally significant?
**Answer:**
A Pivot Transaction is the critical tipping point in a Saga. Steps before the pivot are **compensable** (can be rolled back). Steps after the pivot are **retriable** (must eventually succeed and are not compensable). The pivot transaction itself is the step that makes the global transaction logically irreversible.
Architecturally, identifying the pivot step is crucial for minimizing compensation logic. If the pivot succeeds, the system commits to eventual success, and any downstream failures must be resolved via retries (forward recovery) rather than rollbacks (backward recovery).

> Say: "The pivot transaction is the point of no return; prior steps rely on compensations for rollback, whereas subsequent steps rely on infinite retries for forward recovery."

## 3. How do you handle a scenario where a compensating transaction itself fails?
**Answer:**
Compensating transactions must be designed to never fail due to business logic (e.g., if we reserved funds, releasing them should not fail due to a business rule). However, they can fail due to infrastructure issues (network timeouts, database unavailability).
To handle this, compensations must be **retriable and idempotent**. The orchestrator must persistently retry the compensation until it succeeds. If it fails permanently (e.g., the target system is permanently decommissioned or corrupted), manual intervention (alerting operators via a dead-letter queue) is the only fallback.

> Say: "Compensations must be strictly idempotent and infinitely retriable for infrastructure failures. Business-level failures in compensations represent a fundamental design flaw."

## 4. Why is Two-Phase Commit (2PC) considered a single point of failure compared to an Orchestrated Saga?
**Answer:**
In 2PC, the transaction coordinator drives the Prepare and Commit phases. If the coordinator crashes after the Prepare phase but before the Commit phase, all participating databases hold exclusive locks on their resources indefinitely (blocking).
In an Orchestrated Saga, the orchestrator tracks state (e.g., in an event store), but local transactions commit immediately, releasing database locks. If the orchestrator crashes, it can be restarted, read its persistent state, and resume the Saga without having blocked external databases in the interim.

> Say: "2PC holds exclusive database locks across the network while waiting for the coordinator, whereas Sagas release local locks immediately, avoiding system-wide blocking if the orchestrator fails."

## 5. How does the Transactional Outbox pattern solve the dual-write problem without distributed transactions?
**Answer:**
The dual-write problem occurs when a service must update its database and publish a message to a broker. If it does this sequentially, a crash between the two steps leaves the system inconsistent.
The Transactional Outbox pattern leverages a single local database transaction to update the business entities and insert an event record into an `outbox` table. Because it's a single local transaction, it's atomic. A separate process (like a CDC tool) asynchronously tails the transaction log to read the outbox and publish to the broker.

> Say: "By wrapping the business state change and the event emission (via an outbox table) in a single local ACID transaction, we guarantee atomicity without needing a distributed coordinator."

## 6. What are the trade-offs of using Change Data Capture (CDC) vs. a polling publisher for the Outbox pattern?
**Answer:**
**Polling Publisher**:
- *Pros*: Simpler to implement, database agnostic (just standard SQL).
- *Cons*: Polling introduces latency, polling queries can put significant load on the database, and updating records to mark them as "published" requires additional writes.

**CDC (e.g., Debezium)**:
- *Pros*: Near real-time publishing, minimal overhead on the database (reads from WAL/binlog), no need to update records to mark as published.
- *Cons*: Highly infrastructure-dependent, complex setup, tightly coupled to specific database engine internals.

> Say: "CDC scales much better and reduces database load by tailing the transaction log, whereas polling is easier to implement but introduces latency and unnecessary query overhead."

## 7. How do you implement "Reread Proofing" in a highly concurrent Saga environment?
**Answer:**
Reread proofing, or repeatable reads in the context of Sagas, prevents a service from processing outdated information while a Saga is mutating state.
This is achieved by implementing versioning (Optimistic Concurrency Control) on the business entities. When a Saga step updates an entity, it increments the version. If another concurrent process attempts to mutate the entity based on an older version, the update is rejected. Additionally, reading processes must be aware of the "Semantic Lock" state to know if a version is currently part of an in-flight Saga.

> Say: "We use optimistic locking with version numbers combined with semantic locks. This ensures concurrent transactions cannot blindly overwrite state mutated by an ongoing Saga."

## 8. Explain the "Lost Update" anomaly in Sagas and how to mitigate it.
**Answer:**
A Lost Update occurs when two independent Sagas (or a Saga and a local transaction) modify the same entity concurrently, and one update overwrites the other without considering the first's changes.
Mitigation strategies include:
- **Pessimistic Locking**: Locking the row `FOR UPDATE` during the local transaction.
- **Optimistic Locking**: Using a version column. The update fails if the version has changed since it was read.
- **Commutative Operations**: Designing operations so their order doesn't matter (e.g., `UPDATE account SET balance = balance + 100` instead of `SET balance = 500`).

> Say: "Lost updates are mitigated at the local database level using optimistic concurrency control (versioning) or by designing operations to be strictly commutative."

## 9. How does the Inbox pattern handle deduplication, and what are its database implications?
**Answer:**
Message brokers often guarantee at-least-once delivery, leading to duplicate messages. The Inbox pattern ensures idempotency. When a consumer receives a message, it inserts the message ID into an `inbox` table and processes the business logic within a single local transaction. A unique constraint on the message ID in the `inbox` table ensures that if a duplicate message arrives, the insert will fail with a constraint violation, allowing the consumer to safely discard the duplicate.
*Implications*: The `inbox` table can grow indefinitely. It requires a cleanup strategy (e.g., partitioning by date or TTL) to purge old message IDs, which assumes duplicates will only arrive within a specific time window.

> Say: "The Inbox pattern leverages a unique database constraint on the message ID to ensure idempotency. However, it requires a robust cleanup strategy to prevent the inbox table from growing infinitely."

## 10. When migrating from a monolithic 2PC architecture to microservices with Sagas, what is the biggest challenge?
**Answer:**
The biggest challenge is the loss of strong consistency and the paradigm shift to eventual consistency and compensation logic.
In a monolith with 2PC, failures are handled by implicit rollbacks provided by the database. In a Saga, developers must explicitly write compensating logic for every compensable step. This logic is often complex because it must account for business state changes that occurred between the initial step and the rollback. Furthermore, the business stakeholders must accept that the system will temporarily exist in inconsistent states (eventual consistency).

> Say: "The hardest part is the shift from implicit database rollbacks to explicit, developer-authored compensating logic, and managing the business implications of temporary data inconsistencies."
