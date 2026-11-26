# Interview Questions: MySQL

## Basic Questions

### 1. When would you choose MySQL in a system design interview?

Use MySQL when the system needs a relational OLTP source of truth with transactions, constraints, secondary indexes, and SQL queries. Strong examples include orders, payments, users, inventory, subscriptions, entitlement state, workflow state, and SaaS control-plane data.

Avoid presenting it as "the database" without a workload. Say what data lives in MySQL, which operations need transactions, which reads tolerate stale replicas, and what scale trigger would force partitioning or sharding.

### 2. What does InnoDB add to MySQL?

InnoDB is the default MySQL 8.4 storage engine unless the server is configured differently. For interview purposes, it is the normal engine behind transactional MySQL tables.

It provides the important OLTP properties: ACID-oriented transactions, commit and rollback, crash recovery, row-level locking, consistent reads, foreign keys, and clustered primary-key storage.

### 3. Why does the primary key matter so much in InnoDB?

InnoDB stores row data in the clustered index, which is normally the primary key. Secondary indexes carry the primary-key columns so InnoDB can find the full row through the clustered index.

That means the primary key is not just a logical identifier. A compact, stable primary key can reduce secondary-index size, while a wide primary key can make every secondary index heavier.

### 4. How do you decide what indexes to add?

Start from named query paths, not from column lists. For example: "fetch open orders for a merchant sorted by created time" suggests an index aligned with merchant, status, and created time.

Use `EXPLAIN` to inspect the optimizer plan. Keep indexes that support hot reads or constraints, and avoid indexing every column because each index adds write and storage cost.

## Intermediate Questions

### 5. How do you scale reads with MySQL?

Use replicas for reads that can tolerate stale data: product pages, dashboards, analytics, feed hydration, and non-critical profile lookups. Keep writes on the source/primary.

For read-after-write flows, either read from the primary, use session stickiness for a short window, or expose freshness requirements in the API. The key interview signal is acknowledging replica lag as a product correctness issue, not just an infrastructure metric.

### 6. What are the main replication trade-offs?

MySQL replication is asynchronous by default, so it is useful for scale-out reads, backup isolation, analytics, remote copies, and delayed recovery. The trade-off is that replicas can lag behind the source.

MySQL 8.4 also supports semisynchronous replication, where the source waits for at least one replica to acknowledge receipt and logging of the transaction events before returning to the client. That can reduce data-loss windows but adds commit-path latency and still requires careful failover design.

### 7. How do you handle write scaling?

First reduce unnecessary work on the primary: fix bad queries, add targeted indexes, remove unused indexes, batch safe background writes, and separate heavy analytics from OLTP.

Then consider partitioning large tables for retention or localized scans. Shard only when measured primary write pressure or storage growth justifies the operational cost: routing, rebalancing, cross-shard queries, and cross-shard transactions.

### 8. What isolation level does InnoDB use by default, and why does it matter?

InnoDB supports `READ UNCOMMITTED`, `READ COMMITTED`, `REPEATABLE READ`, and `SERIALIZABLE`. The default is `REPEATABLE READ`.

In interviews, explain isolation through business harm. A payment ledger, inventory reservation, or entitlement update needs stronger correctness checks than an analytics query. Also distinguish normal non-locking reads from locking reads such as `SELECT ... FOR UPDATE`.

### 9. How do row-level locks help, and where can they still hurt?

Row-level locking allows concurrent transactions to update different rows without blocking the whole table. It is a major reason MySQL with InnoDB works well for OLTP workloads.

It does not eliminate contention. Hot rows, range scans, missing indexes, and inconsistent lock ordering can still cause waits or deadlocks. A strong answer includes short transactions, consistent lock order, appropriate indexes, and idempotent retry logic.

## Advanced Questions

### 10. How would you design MySQL for an order service?

Use MySQL as the source of truth for users, carts, orders, order_items, payments, inventory reservations, and idempotency keys. Use transactions to create an order, reserve inventory, and record payment state transitions where partial success would be harmful.

Index by customer/order lookup paths, merchant/status/time dashboards, and idempotency keys. Route write-confirmation reads to the primary, use replicas for history pages and dashboards where stale data is acceptable, and plan partitioning by time or tenant if tables grow large.

### 11. How do you prevent duplicate payment or order creation?

Use a unique idempotency key scoped to the actor and operation, such as `(merchant_id, idempotency_key)` or `(user_id, request_id)`. Insert the key and state in the same transaction as the business mutation.

If the client retries, the unique constraint lets the service return the original result instead of creating another payment or order. The application still needs deterministic retry behavior and clear expiration policy for idempotency records.

### 12. How do you debug a slow MySQL query?

Start with the query, the table size, cardinality, and the expected access pattern. Run `EXPLAIN` to inspect join order, access type, chosen indexes, filtered rows, and whether the plan is scanning too much data.

Then decide whether the fix is query rewrite, composite index, statistics refresh, data model change, pagination change, or moving a reporting workload away from the primary. Do not default to adding an index without proving it supports the hot path.

### 13. How do you design for failover?

State the recovery goals first: acceptable write outage, acceptable data loss window, and what clients should do during failover. Then describe monitored replication, tested promotion, application connection rerouting, backups, and restore drills.

Also call out what can fail silently: replicas may lag, backups may be unrestorable, application pools may hold old primary connections, and delayed jobs may replay operations twice unless writes are idempotent.

### 14. How do you migrate a large MySQL table safely?

Use expand-and-contract: add backward-compatible schema first, deploy code that writes both old and new shape when needed, backfill in bounded batches, verify consistency, flip reads, then remove the old shape later.

For large tables, watch lock time, replication lag, disk growth, rollback cost, and application compatibility. Keep a rollback or pause point at each phase.

### 15. When would you choose PostgreSQL, DynamoDB, Cassandra, or Kafka instead?

Choose PostgreSQL when you want a similarly relational database with PostgreSQL-specific strengths or ecosystem fit. Choose DynamoDB for managed key-value/document access with predictable partition-key patterns and high horizontal scale. Choose Cassandra for wide-column, high-write, multi-node distributed storage when eventual consistency is acceptable. Choose Kafka for event streaming, not as the primary relational source of truth.

The important interview move is not brand comparison. Tie the choice to consistency, query shape, write scale, operational model, and failure behavior.

## Common Follow-ups

- How do you route reads after a write?
- What metrics define replica lag and primary saturation?
- What is your shard key and what query becomes harder after sharding?
- How do you keep transactions short under high traffic?
- How do you handle deadlock retries without double-applying side effects?
- Which schema constraints belong in MySQL versus application code?
- How would you move analytics off the primary?
- How do you test restore, not just backup creation?

## Red Flags to Avoid

- "Use replicas for all reads" with no freshness policy.
- "Use transactions" without naming the rows or invariants protected.
- "Add indexes" without a query path or `EXPLAIN` evidence.
- "Shard MySQL" before discussing indexing, replicas, partitioning, and domain split.
- Ignoring primary-key width and secondary-index storage.
- Ignoring hot rows, deadlocks, and retry behavior.
- Using MySQL for event streaming or heavy analytical scans without isolation.

## 60-90 Second Answer

"I would choose MySQL for a transactional relational core where correctness matters: users, orders, payments, inventory, or workflow state. In MySQL 8.4, InnoDB is the default engine, so I get ACID transactions, row-level locking, consistent reads, clustered primary-key storage, and foreign keys. I would model invariants first, use compact primary keys, enforce uniqueness where duplicate operations are harmful, and add composite indexes only for known hot queries verified with `EXPLAIN`.

For scale, I would keep writes and correctness-critical reads on the primary, send stale-tolerant reads to replicas, and monitor replica lag as part of the product contract. Before sharding, I would tune queries, remove bad indexes, add pooling, isolate analytics, and partition large tables where useful. The risks I would discuss are replica lag, primary failover, deadlocks, hot rows, online migrations, backup restore, and the complexity of cross-shard operations if we eventually outgrow one primary."

## Rubric

| Signal | Weak | Strong |
|--------|------|--------|
| Workload fit | Says MySQL is popular | Names OLTP entities and correctness boundaries |
| Transactions | Mentions ACID generally | Explains invariants, isolation, locks, and retries |
| Indexes | Adds indexes broadly | Maps indexes to queries and verifies with `EXPLAIN` |
| Replication | Uses replicas as a generic scale fix | Handles lag, read-after-write, backups, and failover |
| Scaling | Jumps to sharding | Uses schema, indexes, replicas, partitioning, then sharding |
| Operations | Ignores recovery | Defines monitoring, migrations, backups, restore, and rollback |

## Cross-links

- [MySQL Theory](./THEORY.md)
- [Relational Databases](../relational-databases/)
- [PostgreSQL](../postgresql/)
- [Database Replication](../database-replication/)
- [Database Sharding](../database-sharding/)
- [Contention Control](../contention-control/)
- [Monitoring & Observability](../monitoring-observability/)

## Short Source Notes

- [MySQL 8.4 InnoDB introduction](https://dev.mysql.com/doc/refman/8.4/en/innodb-introduction.html): default engine, ACID-oriented DML, row-level locking, consistent reads, clustered indexes, and foreign keys.
- [MySQL 8.4 clustered and secondary indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html): clustered-index behavior and secondary-index relationship to the primary key.
- [MySQL 8.4 transaction isolation](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html): supported isolation levels and default `REPEATABLE READ`.
- [MySQL 8.4 replication](https://dev.mysql.com/doc/refman/8.4/en/replication.html): asynchronous-by-default replication, scale-out reads, backups, analytics, semisynchronous replication, and delayed replication.
- [MySQL 8.4 EXPLAIN](https://dev.mysql.com/doc/refman/8.4/en/explain.html): optimizer execution-plan inspection for explainable statements.
