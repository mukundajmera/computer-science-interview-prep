# MySQL

MySQL is a relational database commonly used as the transactional source of truth for web and application systems. In system design interviews, treat it as a strong OLTP store first: model the invariants, keep writes on the primary, add indexes for known queries, and scale reads or partitions only when the workload proves the need.

## Mental Model

Think of MySQL as a SQL server plus a storage engine. For normal MySQL 8.4 OLTP tables, that storage engine is usually InnoDB, which is the default engine unless configured otherwise.

The practical model:

1. The application sends SQL to MySQL.
2. The optimizer chooses an execution plan using table/index statistics.
3. InnoDB reads or changes rows through indexes, with the primary key acting as the clustered index.
4. Transactions use ACID machinery, isolation levels, locking, undo/redo, and crash recovery.
5. Replicas can copy changes from the source for scale-out, backups, analytics, or remote reads.

## What MySQL Gives You

| Capability | Interview framing |
|------------|-------------------|
| Relational schema | Tables, primary keys, foreign keys, constraints, and joins encode business shape. |
| ACID transactions | Useful for money, inventory, workflow state, account changes, and other correctness-heavy writes. |
| InnoDB clustered indexes | The primary key determines row organization; secondary indexes carry primary-key values. |
| Row-level locking | Concurrent OLTP writes can proceed when they touch different rows or index ranges. |
| Isolation levels | Tune the balance between consistency, concurrency, and locking overhead per workload. |
| Query optimizer and `EXPLAIN` | Inspect whether a query uses the intended indexes and join order. |
| Replication | Add replicas for read scale, backups, analytics, delayed recovery, or geographic distribution. |

## Core InnoDB Facts

- In MySQL 8.4, InnoDB is the default storage engine for new tables unless the server default is changed.
- InnoDB DML follows the ACID model with transactions, commit, rollback, and crash recovery.
- InnoDB supports row-level locking and consistent reads for concurrent access.
- Every InnoDB table has a clustered index that stores row data; normally this is the primary key.
- Secondary indexes include the primary key columns, so wide primary keys also make secondary indexes wider.
- InnoDB offers the SQL standard isolation levels: `READ UNCOMMITTED`, `READ COMMITTED`, `REPEATABLE READ`, and `SERIALIZABLE`; its default is `REPEATABLE READ`.

## Data Modeling

Start with the business invariants before picking scale machinery.

### Entity and key design

- Use stable primary keys for core entities such as users, accounts, orders, payments, sessions, and inventory rows.
- Keep primary keys compact because InnoDB secondary indexes include the primary-key columns.
- Use foreign keys when the database should enforce parent-child integrity.
- Use unique constraints for invariants such as one active cart per user or one idempotency key per payment attempt.

### Table boundaries

- Normalize data when updates must stay consistent across related entities.
- Denormalize selectively for hot read paths, but keep one authoritative write path.
- Separate high-churn event or audit tables from compact current-state tables.
- Avoid putting unbounded or frequently rewritten large blobs in hot OLTP rows; store object data elsewhere and keep metadata in MySQL.

### Indexing

Design indexes from concrete queries:

- Equality filters first, then range or sort columns when the access pattern supports it.
- Add composite indexes for dominant multi-column lookup paths.
- Use `EXPLAIN` before and after index changes to verify the optimizer plan.
- Remove unused indexes when write overhead and storage cost are visible.

## Transaction and Isolation Design

Use transactions for operations where partial success is harmful.

Common interview examples:

- Reserve inventory and create an order atomically.
- Deduplicate a payment request with an idempotency key.
- Move money between ledger accounts with balanced entries.
- Advance a workflow state only if the current state matches the expected state.

Pick isolation by business harm:

| Workload | Typical stance |
|----------|----------------|
| Ledger, inventory, entitlement writes | Prefer explicit transactions and strong correctness checks. |
| User profile reads | Often fine with default isolation and normal indexed reads. |
| Reporting reads | May tolerate relaxed freshness on replicas. |
| Hot counters | Consider atomic updates, aggregation tables, batching, or moving the hot path outside MySQL. |

Do not hide concurrency risk behind "the database handles it." Explain which row or index range is protected, what happens on deadlock, and how the application retries safe transactions.

## Scaling Pattern

Scale in this order unless the problem statement proves otherwise:

1. Good schema and indexes.
2. Query plan inspection with `EXPLAIN`.
3. Connection pooling and slow-query monitoring.
4. Read replicas for stale-tolerant reads.
5. Partitioning for very large tables, retention, or localized scans.
6. Sharding or service-level data ownership when one primary is no longer enough.

### Read scaling

Use replicas for:

- Product pages, profile pages, search filters, feeds, dashboards, and analytics that tolerate replica lag.
- Backups that should not burden the write primary.
- Regional reads where a slightly stale local copy is acceptable.

Keep these reads on the primary:

- Read-after-write confirmation flows.
- Payment, inventory, entitlement, and authorization checks.
- Any path where stale data can create user-visible correctness harm.

### Write scaling

The primary is still the write bottleneck in the common single-source topology. Improve it by reducing write amplification, batching safe background work, keeping indexes purposeful, splitting independent domains, or eventually sharding by tenant, account, user, region, or another ownership key.

## Failure Modes

| Failure mode | What goes wrong | Mitigation |
|--------------|-----------------|------------|
| Replica lag | Users read stale state after writes. | Route critical reads to primary; monitor lag; expose freshness requirements. |
| Primary failure | Writes stop until failover completes. | Backups, tested failover, replication health checks, clear RTO/RPO assumptions. |
| Deadlocks | Concurrent transactions wait in a cycle and one is rolled back. | Keep transactions short; lock rows in a consistent order; retry idempotently. |
| Hot row or hot range | Many writers contend for one key or index range. | Spread writes, aggregate asynchronously, shard the counter/domain, or redesign the invariant. |
| Missing or wrong index | Queries scan too much data and overload the server. | Use slow-query logs, `EXPLAIN`, and workload-specific composite indexes. |
| Over-indexing | Writes slow down and storage grows. | Keep indexes tied to active query paths; remove unused indexes after measurement. |
| Large online change | Schema migration causes locks, lag, or long rollback. | Use expand-and-contract migrations, small batches, and rollback checkpoints. |
| Backup gap | Restore point does not meet business recovery needs. | Test restore, retain binary logs as needed, and document recovery objectives. |

## When to Use MySQL

- You need a mature relational OLTP source of truth.
- The system has clear entities, relationships, and integrity constraints.
- Correctness matters more than unlimited horizontal write scale.
- Query patterns benefit from SQL, joins, secondary indexes, and transactions.
- Your team values broad operational tooling, replication options, and managed-service support.

## When Not to Use MySQL

- The primary workload is massive append-only event ingestion with analytical scans.
- The access pattern is simple key-value at very high scale and eventual consistency is acceptable.
- The data model is mostly unstructured documents with rapidly changing nested shape.
- You need globally distributed active-active writes with low conflict-management burden.
- You cannot tolerate relational schema migration planning.

## Operational Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Keep MySQL as source of truth | Stronger transactional boundary and simpler correctness story | Primary write capacity becomes a design constraint |
| Add read replicas | More read throughput and backup/analytics isolation | Replica lag and read routing complexity |
| Add more indexes | Faster targeted reads | Slower writes and larger storage footprint |
| Use stronger isolation or locking reads | Better protection for critical invariants | More lock waits and deadlock/retry paths |
| Partition large tables | Easier retention and smaller scans | More schema/query complexity |
| Shard | Higher write and storage ceiling | Cross-shard transactions, routing, rebalancing, and operations become harder |

## Interview Pitfalls

- Saying "use MySQL" without defining the consistency boundary.
- Sending all reads to replicas without addressing read-after-write behavior.
- Claiming row-level locking means no contention; range locks and hot rows still matter.
- Adding indexes without naming the query they serve.
- Ignoring primary-key width when discussing secondary index size.
- Treating sharding as the first scale step.
- Forgetting backup restore tests, failover behavior, and replication lag.
- Mixing OLTP and heavy analytics on the same primary without isolation.

## 60-90 Second Answer

"I would use MySQL when the system needs a relational source of truth with strong transactional correctness. In MySQL 8.4, the normal OLTP path is InnoDB, which is the default storage engine and gives ACID transactions, row-level locking, consistent reads, and clustered primary-key storage. I would model the core entities and invariants first, use compact primary keys, enforce uniqueness and foreign-key constraints where the database should protect correctness, and add indexes only for known query paths.

For scale, I would first inspect query plans with `EXPLAIN`, tune indexes, and add pooling and slow-query monitoring. Then I would use replicas for stale-tolerant reads, backups, and analytics, while keeping read-after-write and correctness-critical checks on the primary. If one primary becomes the bottleneck, I would look at partitioning or domain sharding, but only after measuring write pressure and accepting the cross-shard complexity. The main risks I would call out are replica lag, hot rows, deadlocks, bad indexes, online migrations, and untested failover or restore paths."

## Rubric

| Level | Signal |
|-------|--------|
| Weak | Names MySQL as a database choice but does not discuss transactions, indexes, or replication lag. |
| Solid | Explains relational modeling, ACID transactions, primary/replica split, and index-driven query design. |
| Strong | Connects InnoDB clustered indexes, isolation, lock contention, `EXPLAIN`, read freshness, and failover to concrete product requirements. |
| Excellent | Defines correctness boundaries, retry semantics, migration safety, recovery objectives, sharding triggers, and operational observability. |

## Follow-ups to Expect

- How do you guarantee read-after-write consistency with replicas?
- What do you index for a multi-tenant orders table?
- How do you handle deadlocks safely?
- When would you shard MySQL, and what key would you pick?
- How do you migrate a large table without downtime?
- What metrics tell you MySQL is becoming the bottleneck?
- How do you design backup and restore for a payment system?

## Cross-links

- [Relational Databases](../relational-databases/)
- [PostgreSQL](../postgresql/)
- [Database Replication](../database-replication/)
- [Database Sharding](../database-sharding/)
- [Contention Control](../contention-control/)
- [Read Scaling](../read-scaling/)
- [Write Scaling](../write-scaling/)
- [Monitoring & Observability](../monitoring-observability/)
- [Payment System HLD](../../04-hld-projects/payment-system/DESIGN.md)
- [Metrics Monitoring HLD](../../04-hld-projects/metrics-monitoring/DESIGN.md)

## Short Source Notes

- [MySQL 8.4 InnoDB introduction](https://dev.mysql.com/doc/refman/8.4/en/innodb-introduction.html): InnoDB is the default engine in MySQL 8.4 and provides ACID-oriented transactions, row-level locking, consistent reads, clustered indexes, and foreign keys.
- [MySQL 8.4 clustered and secondary indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html): InnoDB stores row data in the clustered index, usually the primary key, and secondary indexes include primary-key columns.
- [MySQL 8.4 transaction isolation](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html): InnoDB supports the SQL standard isolation levels and defaults to `REPEATABLE READ`.
- [MySQL 8.4 replication](https://dev.mysql.com/doc/refman/8.4/en/replication.html): Replication is asynchronous by default; replicas support scale-out reads, backups, analytics, and remote copies, with semisynchronous and delayed options available.
- [MySQL 8.4 EXPLAIN](https://dev.mysql.com/doc/refman/8.4/en/explain.html): `EXPLAIN` shows optimizer execution-plan information for explainable statements.
