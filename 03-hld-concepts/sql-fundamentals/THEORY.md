# SQL Fundamentals

## What is it?

SQL is the standard language for defining, querying, and changing data in relational databases. It is built around tables, rows, columns, keys, constraints, and set-based operations.

In system design interviews, SQL usually means more than syntax. It means choosing a relational data model when the system needs integrity, flexible queries, joins, transactions, and clear consistency boundaries.

## Why do we need it?

Many real systems need:
- Durable records with explicit schemas.
- Relationships between entities, such as users, orders, payments, and inventory.
- Constraints that prevent invalid states before application code sees them.
- Query flexibility for filters, joins, grouping, ordering, and reporting.
- Transactions that keep related writes correct under failure and concurrency.

SQL databases are strongest when correctness and relational access patterns matter more than raw key-value throughput.

## Core model

| Concept | Interview meaning |
|---|---|
| Table | Collection of rows with a declared shape |
| Row | One entity or relationship instance |
| Column | Typed attribute with optional defaults and constraints |
| Primary key | Stable row identity |
| Foreign key | Relationship to another table |
| Unique constraint | Enforces a business invariant such as one active account per email |
| Check constraint | Enforces local validity such as non-negative quantity |
| Index | Extra access structure that speeds reads but adds write cost |

Good SQL design starts with invariants, not tables. First identify what must never be wrong, then encode the strongest safe version in keys, constraints, transactions, and application workflow.

## DDL and DML

### DDL: define structure

Data Definition Language changes the database shape:
- `CREATE TABLE` for entities and relationship tables.
- `ALTER TABLE` for adding columns, constraints, or indexes.
- `DROP` operations for removing schema objects.

In production systems, DDL is often treated like a deployment. Safe schema evolution usually uses expand-and-contract migrations: add backward-compatible fields first, deploy compatible code, backfill in batches, then remove old fields after all callers have moved.

### DML: read and change data

Data Manipulation Language operates on rows:
- `SELECT` reads rows and derived result sets.
- `INSERT` creates rows.
- `UPDATE` changes rows.
- `DELETE` removes rows.

Interview-quality answers tie DML to access paths. A query is not "fast" because it is short; it is fast when predicates, joins, sort order, and result size align with the data model and indexes.

## Joins

Joins combine rows from related tables.

| Join | Use case | Common pitfall |
|---|---|---|
| Inner join | Return matching rows on both sides | Accidentally dropping unmatched business cases |
| Left join | Keep all rows from the left side | Filtering right-side columns in `WHERE` and turning it into an inner join |
| Many-to-many join | Use a junction table | Creating duplicate rows or missing uniqueness constraints |
| Self join | Relate rows in the same table | Hard-to-read queries without clear aliases |

Use joins when relationships are natural and the result set is bounded. Avoid join-heavy request paths when each request fans out across very large tables without selective filters.

## Indexes

Indexes make reads faster by maintaining an ordered or searchable structure outside the base table. They are most useful when they support a concrete query pattern:
- Equality lookups by id, email, tenant id, or status.
- Range queries by time or score.
- Ordered pagination with a stable sort key.
- Join predicates on foreign keys.
- Uniqueness checks for business rules.

Indexes are not free. They consume storage, slow writes, complicate migrations, and can be ignored by the planner when selectivity is low or the predicate shape does not match the index.

### Index design checklist

1. Start from the highest-volume user-facing query.
2. Identify filters, join keys, sort order, and result limits.
3. Put high-selectivity equality filters first in composite indexes.
4. Include range and ordering needs intentionally.
5. Remove unused or duplicate indexes after measurement.

## Query planning

A SQL engine decides how to execute a query using table statistics, indexes, join order, and cost estimates. The planner may choose:
- Full table scan when most rows are needed.
- Index lookup when predicates are selective.
- Nested loop join for small or indexed inputs.
- Hash or merge join for larger sets.
- Sort, aggregate, or temporary materialization steps.

The practical interview answer is to inspect the execution plan, compare estimated versus actual row counts, and fix the root cause: missing index, stale statistics, non-selective predicate, expensive sort, excessive result size, or a join order problem.

## Transactions

A transaction groups operations into one logical unit of work.

| ACID property | Meaning |
|---|---|
| Atomicity | All writes commit or none do |
| Consistency | Committed data satisfies declared rules |
| Isolation | Concurrent transactions do not expose unsafe intermediate states |
| Durability | Committed writes survive failures within the database guarantee |

Use transactions for money movement, inventory reservation, order state transitions, account creation, and any workflow where partial success would violate a business invariant.

## Isolation anomalies

Isolation level controls which concurrent behaviors are allowed. Stronger isolation reduces anomalies but can reduce concurrency or increase retries.

| Anomaly | What happens | Example |
|---|---|---|
| Dirty read | A transaction reads uncommitted data | Showing a payment that later rolls back |
| Non-repeatable read | Re-reading the same row returns a different committed value | Balance changes mid-transaction |
| Phantom read | Re-running a predicate returns new or missing rows | Seat count changes while checking availability |
| Lost update | Two writers overwrite each other | Concurrent profile edits drop one change |
| Write skew | Two transactions each pass a check, but together violate an invariant | Two doctors both go off call after separate checks |

In interviews, do not recite isolation names alone. Tie the isolation choice to the business harm. Use stronger isolation, row locks, optimistic concurrency, unique constraints, or transactional retries when the invariant matters.

## Normalization and denormalization

Normalization reduces duplication and protects consistency by storing each fact in one place. It helps with:
- Clear ownership of facts.
- Fewer update anomalies.
- Smaller writes for canonical entities.
- Better constraint enforcement.

Denormalization duplicates or precomputes data to improve read performance. It helps with:
- High-volume read endpoints.
- Avoiding expensive joins on hot paths.
- Serving summaries, feeds, counters, and search views.

The design trade-off is freshness and complexity. If data is duplicated, define the source of truth, update path, repair job, and acceptable staleness.

## When to use SQL

- Core transactional data with strong correctness requirements.
- Entities with clear relationships and constraints.
- Workloads needing ad hoc filtering, joins, sorting, and aggregation.
- Systems where schema clarity helps teams reason about data quality.
- Products that need both online workflows and operational reporting from the same model early on.

## When not to use SQL

- Ultra-high-throughput key-value access where every request is a simple lookup.
- Append-only event streams where log storage and stream processing are the primary model.
- Graph traversal workloads where relationships are deep and path-oriented.
- Large analytical scans better served by columnar warehouse or OLAP systems.
- Schemas changing so fast that relational constraints would be mostly bypassed.

## Trade-offs

| Pros | Cons |
|---|---|
| Strong integrity through keys, constraints, and transactions | Schema changes need discipline |
| Flexible querying across related entities | Poor queries can become expensive at scale |
| Mature operational patterns and tooling | Horizontal sharding adds application complexity |
| Clear transaction boundaries | Contention can appear on hot rows or indexes |
| Natural fit for many business domains | Over-normalization can hurt hot read paths |

## Common pitfalls

- Modeling tables before clarifying invariants and access patterns.
- Adding indexes for every column instead of measured query paths.
- Ignoring transaction boundaries around multi-row updates.
- Relying on application checks when a unique constraint can enforce the rule.
- Using offset pagination on large mutable result sets without a stable cursor.
- Allowing unbounded joins, sorts, or aggregations in request paths.
- Treating read replicas as always fresh after writes.
- Denormalizing without a repair or reconciliation strategy.

## Interview checklist

1. State the entities, relationships, and invariants.
2. Choose primary keys, foreign keys, and uniqueness constraints.
3. Name the main read and write queries.
4. Add indexes only for those concrete query paths.
5. Define transaction boundaries and isolation needs.
6. Explain how to handle contention, retries, and idempotency.
7. Call out where denormalized views or caches are justified.
8. Define scale triggers for partitioning, replicas, or sharding.

## 60-90 second answer

"I use SQL when the system has relational data, strong invariants, and query patterns that benefit from joins, filters, ordering, and transactions. I start by modeling the entities and business rules: primary keys for identity, foreign keys for relationships, unique and check constraints for invariants, and transactions around multi-row state changes.

For performance, I work backward from access patterns. The main request paths get targeted indexes that match filters, join keys, and sort order. I inspect query plans when a query is slow instead of guessing. For scale, I usually try query tuning, index cleanup, read replicas, pagination, and partitioning before sharding.

The main risks are over-indexing, unbounded joins, replica staleness, and weak transaction design. If reads become too expensive, I denormalize into a derived view or cache, but I keep one source of truth and define freshness, repair, and rollback behavior."

## Scoring rubric

| Score | Interview signal |
|---|---|
| 1 | Says "use SQL" only because data is structured, with no constraints, query, or transaction reasoning |
| 3 | Explains tables, keys, joins, indexes, and basic ACID trade-offs |
| 5 | Ties schema, indexes, query plans, transactions, isolation, denormalization, and scale triggers to concrete workload requirements |

## Follow-up questions

1. Which invariant must be enforced by the database instead of only application code?
2. What are the top three queries and which indexes support them?
3. Where can a transaction fail halfway, and what is the rollback behavior?
4. Which isolation anomaly would be unacceptable for this workflow?
5. Where would read replicas be safe, and where would stale reads be harmful?
6. What would make you denormalize, partition, or shard?

## Related concepts and projects

- [Relational Databases](../relational-databases/)
- [PostgreSQL](../postgresql/)
- [Database Replication](../database-replication/)
- [Database Sharding](../database-sharding/)
- [Distributed Transactions](../distributed-transactions/)
- [Read Scaling](../read-scaling/)
- [Write Scaling](../write-scaling/)
- [Caching](../caching/)
- [Payment System](../../04-hld-projects/payment-system/)
- [Quick Commerce Delivery](../../04-hld-projects/quick-commerce-delivery/)
- [Amazon Orders Case Study](../../case-studies/amazon-orders/)
- [HLD Concepts Quiz](../../quizzes/hld-concepts-quiz.md)
- [HLD Concepts Flashcards](../../flashcards/hld-concepts.md)

## Short Source Notes

- This page is clean-room curriculum content based on standard SQL interview knowledge and repo-native HLD patterns.
- It intentionally avoids version-specific SQL dialect behavior. Use the MySQL and PostgreSQL concept pages when an interview asks for engine-specific locking, indexing, or replication semantics.
