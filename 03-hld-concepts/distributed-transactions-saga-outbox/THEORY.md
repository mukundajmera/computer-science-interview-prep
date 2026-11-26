# Distributed Transactions: SAGA and Transactional Outbox

## 2PC/XA vs. SAGA Pattern

In distributed systems, traditional atomic transactions spanning multiple databases often rely on the **Two-Phase Commit (2PC)** or **XA protocol**. While 2PC ensures strong consistency, it introduces significant drawbacks:
- **Blocking Coordinator**: The transaction coordinator acts as a central point of failure. If it crashes during the commit phase, participating databases hold locks indefinitely.
- **Latency and Throughput**: 2PC requires multiple synchronous network round-trips and locking resources across all participants until the global transaction completes, drastically reducing system throughput.

The **SAGA Pattern** addresses these issues by relaxing strong consistency in favor of **eventual consistency**. A Saga breaks down a global transaction into a sequence of local transactions. Each local transaction updates the database within a single service and publishes an event or message to trigger the next local transaction in the sequence. If a local transaction fails, the Saga executes **compensating transactions** to undo the changes made by the preceding successful local transactions.

## Orchestration vs. Choreography

Sagas can be coordinated using two primary approaches:

### Choreography (Event-Driven)
In a choreographed Saga, there is no central coordinator. Each service listens for events from other services and decides if an action is needed.
- **Pros**: Simple for small workflows, loose coupling, no single point of failure for coordination.
- **Cons**: Can become difficult to track as workflows grow (the "spaghetti" effect), cyclic dependencies can occur, harder to implement timeouts and retries globally.

### Orchestration (Centralized Workflow)
In an orchestrated Saga, a centralized **Saga Orchestrator** tells the participating services what local transactions to execute.
- **Pros**: Centralized logic for complex workflows, easier to manage rollbacks (compensations), avoids cyclic dependencies, clear separation of concerns.
- **Cons**: Introduces a central coordinator (which must be highly available), risk of placing too much business logic in the orchestrator.

## Transaction Steps and Anomalies

A Saga workflow typically divides steps into three categories:
1. **Compensable Transactions**: Steps that can be reversed if a later step fails. These require a corresponding compensating transaction (semantic undo).
2. **Pivot Transaction**: The "point of no return". If the pivot transaction succeeds, the Saga will run until completion. It separates compensable steps from retriable steps.
3. **Retriable Transactions**: Steps following the pivot. These are guaranteed to succeed eventually and do not need compensations; they are retried until successful.

### Compensating Transactions and Isolation Anomalies
Because Sagas do not hold locks across the entire global transaction, they operate at an isolation level lower than Serializable. This can lead to anomalies:
- **Semantic Undo**: Compensations are not physical rollbacks but logical operations (e.g., if a transaction credits an account, the compensation debits it).
- **Semantic Locks**: To prevent concurrent transactions from modifying an entity being updated by an active Saga, services can use semantic locks (e.g., setting an order status to `PENDING` instead of `CREATED`).
- **Dirty Read Anomalies**: Other transactions might read intermediate states before a Saga completes or rolls back.
- **Reread Proofing**: When reading data, a transaction might need to verify that it wasn't modified by an incomplete Saga.

## Transactional Outbox Pattern and CDC

When a service needs to both update its local database and publish an event to a message broker (like Kafka), it faces a dual-write problem. If it updates the database and crashes before publishing the event, the system becomes inconsistent.

The **Transactional Outbox Pattern** solves this:
1. The service updates its business tables and inserts an event record into a local `outbox` table within the **same local database transaction**.
2. Because it's a single transaction, the update and the outbox insertion are atomic.

To reliably publish the events from the `outbox` table, systems often use **Change Data Capture (CDC)** log tailing:
- Tools like **Debezium** or **Canal** tail the database's transaction log (e.g., PostgreSQL `pgoutput` / WAL, MySQL `binlog`).
- The CDC tool reads the outbox inserts and reliably publishes them to the message broker.
- This guarantees at-least-once delivery without distributed transactions.

## Transactional Inbox and Deduplication

Since the outbox/CDC mechanism and message brokers typically guarantee **at-least-once delivery**, consumers may receive the same message multiple times.

The **Transactional Inbox Pattern** provides idempotent consumer processing:
1. The consumer receives a message and checks if its unique ID (or idempotency key) exists in an `inbox` table.
2. If it does not exist, the consumer processes the business logic and inserts the message ID into the `inbox` table within the **same local transaction**.
3. If the message ID already exists, the consumer safely ignores the duplicate message.
