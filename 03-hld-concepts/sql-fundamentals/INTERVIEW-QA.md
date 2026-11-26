# Interview Questions: SQL Fundamentals

## Basic Questions

### 1. When would you choose SQL in a system design interview?
**A**: Choose SQL when the system has relational data, clear invariants, transactions, and flexible query needs. Examples include orders, payments, inventory, users, subscriptions, and workflow state.

### 2. What is the relational model?
**A**: Data is organized into tables of rows and columns. Primary keys identify rows, foreign keys model relationships, and constraints enforce valid states.

### 3. DDL vs DML
**Q**: What is the difference?
**A**: DDL defines or changes schema, such as creating tables and indexes. DML reads and changes rows, such as selecting, inserting, updating, and deleting records.

### 4. Why are constraints important?
**A**: Constraints move critical invariants closer to the data. They prevent invalid rows even when multiple services, jobs, or deployments touch the same database.

## Intermediate Questions

### 5. How do you decide which indexes to add?
**A**: Start from the dominant queries. Add indexes that match selective filters, join keys, sort order, and pagination needs. Avoid indexing every column because each index adds write cost and storage overhead.

### 6. What is a query plan?
**A**: It is the database engine's chosen execution strategy: scans, index lookups, join order, sort steps, and aggregation steps. For slow queries, compare estimated and actual row counts to find missing indexes, bad predicates, or excessive result sizes.

### 7. Inner join vs left join
**Q**: How do you explain the difference?
**A**: Inner join returns only rows with matches on both sides. Left join keeps all rows from the left table and fills missing right-side values with nulls.

### 8. What makes a join expensive?
**A**: Large inputs, missing indexes on join keys, weak filters, poor cardinality estimates, and unbounded result sets. A join is reasonable when the relationship is natural and the query remains selective.

### 9. Normalization vs denormalization
**A**: Normalize to reduce duplication and protect consistency. Denormalize when hot reads need precomputed or duplicated data, but define the source of truth, freshness target, and repair path.

## Advanced Questions

### 10. What does ACID mean?
**A**: Atomicity means all-or-nothing writes. Consistency means committed data follows rules. Isolation controls concurrent visibility. Durability means committed data survives failures within the database guarantee.

### 11. How do you choose transaction boundaries?
**A**: Put all writes that must succeed or fail together in one transaction. For example, creating an order, reserving inventory, and recording payment state may need one carefully bounded state transition or a saga when work spans systems.

### 12. Which isolation anomalies matter in interviews?
**A**: The common ones are dirty reads, non-repeatable reads, phantom reads, lost updates, and write skew. The right answer ties the anomaly to business harm, then chooses isolation, locks, constraints, optimistic concurrency, or retries.

### 13. How do you prevent lost updates?
**A**: Use a transaction with row locking, compare-and-swap version checks, optimistic concurrency tokens, or single-statement conditional updates. Pick based on contention and user experience.

### 14. How do you scale a SQL-backed system before sharding?
**A**: Tune queries, add targeted indexes, reduce result sizes, use stable pagination, add read replicas for stale-tolerant reads, cache derived data, partition large tables, and only then consider sharding.

### 15. When would SQL be the wrong storage choice?
**A**: It may be wrong for simple high-throughput key-value access, append-only event streams, deep graph traversal, very large analytical scans, or access patterns that require horizontal distribution from day one.

## Scenario Questions

### 16. Your order list endpoint is slow. What do you check?
**A**: Check query plan, filters, sort order, result limit, index coverage, join fan-out, and whether the endpoint uses offset pagination over a large mutable table. Then add or adjust the index that supports the exact access pattern.

### 17. Two users claim the last ticket at the same time. What protects correctness?
**A**: Use a transaction around the reservation, enforce the inventory invariant with a conditional update or constraint, and retry or fail cleanly on conflict. Do not rely only on a read-then-write check in application code.

### 18. A read replica returns stale data after checkout. What do you do?
**A**: Route read-after-write-critical requests to the primary or use a session stickiness rule until the write is visible. Replica reads are fine only where staleness is acceptable.

### 19. A product page needs seller name, rating, stock, and price. Do you join every time?
**A**: Start with joins if the query is bounded and indexed. If the page is very hot and joins dominate latency, create a denormalized read model or cache while keeping canonical tables as the source of truth.

### 20. A migration adds a required column. How do you make it safe?
**A**: Add the column in a backward-compatible way, deploy code that writes both old and new forms if needed, backfill in batches, verify coverage, then enforce the constraint and remove old paths.

## Common Follow-ups

- What invariant would you encode as a unique constraint?
- Which query path receives the first composite index?
- How do you handle schema migrations without downtime?
- What isolation anomaly would break this product flow?
- Where can stale reads be tolerated?
- How do you reconcile denormalized tables or caches?
- What metric tells you an index is no longer useful?
- What is the trigger for partitioning or sharding?

## Red Flags to Avoid

- Saying SQL is always strongly consistent without discussing replicas and isolation.
- Adding indexes without a named query path.
- Treating transactions as free across services.
- Ignoring write contention on hot rows.
- Using denormalization without ownership and repair strategy.
- Claiming joins are always bad at scale.
- Choosing SQL only because "the data is structured."

## 60-90 second answer

"SQL is a strong default when the system has relational data, important invariants, and queries that need filters, joins, ordering, aggregation, or transactions. I model the core entities first, then enforce correctness with primary keys, foreign keys, unique constraints, check constraints, and bounded transactions.

For performance, I map the top access patterns to indexes. A good index matches the filters, join keys, sort order, and pagination shape of a real query. If a query is slow, I inspect the query plan to understand scans, joins, row estimates, and sort work before changing the schema.

The main trade-offs are schema migration discipline, write overhead from indexes, contention around hot rows, and complexity when scaling horizontally. I scale SQL with query tuning, targeted indexes, read replicas where stale reads are safe, caching, and partitioning before sharding. I denormalize only when a hot read path needs it, and I define the source of truth and repair path."

## Scoring Rubric

| Score | Interview signal |
|---|---|
| 1 | Names tables and SQL syntax but misses invariants, transactions, and access patterns |
| 2 | Explains keys, joins, and basic indexes but gives generic scaling advice |
| 3 | Connects schema design to queries, constraints, and ACID transactions |
| 4 | Discusses query planning, isolation anomalies, denormalization, and replica staleness |
| 5 | Makes workload-specific trade-offs with clear scale triggers, failure handling, and correctness boundaries |

## Practice Prompts

1. Design the SQL schema for an order checkout flow and name every invariant.
2. Explain the indexes for a paginated transaction history endpoint.
3. Diagnose a slow join between users, orders, and payments.
4. Prevent double booking for a limited-seat event.
5. Decide when to denormalize a feed, catalog, or dashboard table.

## Related Concepts and Projects

- [SQL Fundamentals Theory](./THEORY.md)
- [Relational Databases](../relational-databases/)
- [PostgreSQL](../postgresql/)
- [Database Replication](../database-replication/)
- [Database Sharding](../database-sharding/)
- [Distributed Transactions](../distributed-transactions/)
- [Read Scaling](../read-scaling/)
- [Write Scaling](../write-scaling/)
- [Payment System](../../04-hld-projects/payment-system/)
- [Quick Commerce Delivery](../../04-hld-projects/quick-commerce-delivery/)
- [Amazon Orders Case Study](../../case-studies/amazon-orders/)
