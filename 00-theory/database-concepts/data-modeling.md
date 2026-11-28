# Data Modeling Basics

Data modeling in interviews is about designing a schema that supports key reads/writes, consistency needs, and expected scale. Start simple, then justify targeted optimizations.

---

## Modeling Sequence

1. Extract core entities from requirements.
2. Define primary keys and relationship edges.
3. List top query patterns and write paths.
4. Add indexes to match access patterns.
5. Denormalize only where measured read benefit is clear.
6. Choose partition/shard strategy only when needed.

---

## Entity-Relationship Thinking

Start from the domain, not from tables. An entity is a thing the business tracks with its own identity and lifecycle (a user, an order, a post); a relationship is a fact connecting entities (a user *placed* an order). Naming each relationship's cardinality (one-to-one, one-to-many, many-to-many) drives most later decisions: it determines where foreign keys live and whether you need a join table.

Two habits keep the model honest:

- Give every entity a clear lifecycle owner: deleting the owner should have an obvious meaning for dependent rows (cascade, restrict, or archive).
- Separate identity facts (true about the entity itself) from relationship facts (true only because two entities are connected); mixing them is what creates update anomalies later.

---

## SQL-First Default

For most product interview problems, a relational model is the best starting point:

- predictable schema and constraints
- strong transactional semantics
- mature indexing and query planning

Move away from SQL only when requirements require flexible schema, extreme write throughput, or specialized retrieval patterns.

---

## Keys, Relationships, and Constraints

- Prefer stable surrogate keys (`id`) over business identifiers.
- Use foreign keys for integrity unless scale constraints force app-level enforcement.
- Encode invariants with `NOT NULL`, `UNIQUE`, and domain checks.

Choosing the key is a design decision worth stating out loud:

| Key kind | Example | Strength | Risk |
|----------|---------|----------|------|
| Natural | `email`, `isbn` | Meaningful, no extra column | Business values change or get reused |
| Surrogate | `id` bigserial, UUID | Stable forever, decoupled from business | Extra lookup in natural terms |
| Composite | `(tenant_id, order_seq)` | Encodes scope and ordering naturally | Every FK repeats all columns |

A common hybrid is a surrogate primary key plus a `UNIQUE` constraint on the natural identifier, keeping joins stable while still enforcing business identity.

Example starter schema:

```text
users(id PK, email UNIQUE, username, created_at)
posts(id PK, user_id FK -> users.id, body, created_at)
likes(user_id FK -> users.id, post_id FK -> posts.id, created_at)
```

---

## Modelling One-to-Many and Many-to-Many

- **One-to-many**: the foreign key lives on the "many" side, as `posts.user_id -> users.id` above. One row in the parent, many rows in the child, and the child can be indexed on the FK for the parent's list queries.
- **Many-to-many**: model it as a join table holding the two foreign keys, like `likes(user_id, post_id)`. The join table's primary key is usually the pair itself, which also prevents duplicate relationships. Treat the join table as a first-class entity when the relationship carries its own attributes (`created_at`, role, quantity): those columns belong on the join row, not on either parent.

---

## Normalization vs Denormalization

- Normalize first to control consistency complexity.
- Denormalize for high-read hot paths (feed cards, counters, projections).
- Prefer derived views/caches before duplicating source-of-truth fields broadly.

Normalization removes redundancy so each fact is stored once and updates cannot disagree; see [Database Normalization Theory](./database-normalization-theory.md). Denormalization deliberately copies a fact to make a read cheap, accepting that copies can drift.

Worked example with the schema above: rendering a post card needs its like count.

- *Normalized*: `SELECT COUNT(*) FROM likes WHERE post_id = ?` on every card render. Always correct, but it counts the likes table per post per view, expensive on hot feeds.
- *Denormalized*: store `posts.like_count`, maintained by the like/unlike write path. Reads become free, but every write now updates two places, and a missed or double-applied update silently corrupts the counter, so you need a transaction around both writes or a periodic reconciliation job.

The interview answer is not "pick one" but "state the read/write ratio, keep the normalized form as source of truth, and add the denormalized projection only where measurement justifies it."

---

## Sharding Considerations

- Choose shard keys aligned with dominant query routing.
- Prefer high-cardinality, stable keys.
- Avoid strategies that create hot partitions on current-time writes.

---

## Schema Evolution and Migrations

Schemas change constantly in production, and interviews reward a safe rollout story. The standard pattern is expand-and-contract:

1. **Expand**: add the new column or table as nullable/additive only; old code keeps working.
2. **Backfill and dual-run**: fill existing rows in small batches while new writes populate both shapes.
3. **Switch reads** to the new shape once parity is verified.
4. **Contract**: drop the old column only after no deployed code reads it.

Never rename or retype a column in one step; do it as add-new, migrate, drop-old. Large table rewrites can lock the table, so batch them or use online-schema-change tooling, and keep every step backward compatible with the previous deploy. Transactional guarantees during migrations rest on [ACID properties](./acid-properties.md).

---

## Modeling for Access Patterns in Document and Wide-Column Stores

Relational modeling starts from entities and normalizes; document and wide-column modeling starts from the queries and pre-computes their answers.

- In a document store you design the document boundary around what is read together: embed bounded, co-accessed data (an order with its line items) so one fetch serves the hot read, and reference unbounded or independently changing data. Duplication across documents is accepted when it removes a join from a hot path.
- In a wide-column store there are no joins at all, so each table is effectively built for one query: the partition key spreads data evenly, and the clustering columns store the query's rows contiguously in the order it wants them. A new query shape usually means a new table fed by the same write path, not a new index.

The trade-off against SQL is explicit: you give up ad-hoc querying and integrity enforcement for predictable latency at scale, so these stores are chosen after the access patterns are known, not before.

---

## Soft Deletes and Audit History

- **Soft delete**: keep the row with a `deleted_at` timestamp instead of deleting it. Reads filter `WHERE deleted_at IS NULL` (a partial index keeps that cheap), and restores become trivial. The hidden costs: every query and uniqueness check must remember the filter (two live rows can no longer share `email` under a plain `UNIQUE`), and foreign keys still point at "deleted" rows.
- **Audit history**: when you must know what changed and when, keep a history or event table that the write path appends to in the same transaction as the main update. This gives point-in-time reconstruction without polluting the primary table, the difference between "the row says X" and "we can prove how it became X".

---

## Interview Checklist

1. List the top 3 reads and top 3 writes; every modeling choice must trace back to one of them.
2. Name entities, their keys, and the cardinality of each relationship.
3. Mark which invariants need transactional integrity and which can be eventually consistent.
4. Normalize first; denormalize only a measured hot path, and say how copies stay in sync.
5. Describe one realistic schema change and walk its expand-and-contract migration.
6. Only then discuss sharding, with a key chosen from the dominant query's routing.

---

## Requirements and constraints

- Schema must directly support top 3 read paths and top 3 write paths.
- Strong-consistency workflows should stay within transactional boundaries.
- Key/relationship choices should minimize cross-shard fan-out.
- Evolution path should support backward-compatible migrations.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Entity model | Clear domain entities with key relationships | Generic boxes without domain meaning |
| Access-pattern fit | Index/shard choices tied to API/query needs | Schema divorced from query behavior |
| Consistency reasoning | Explicit where strong vs eventual consistency is acceptable | One-size-fits-all consistency claims |
| Evolution | Safe migration and version strategy acknowledged | Ignores schema change costs |

## Common pitfalls

- Starting with denormalization everywhere.
- Choosing shard key before understanding query patterns.
- Using mutable business fields as identity keys.
- Ignoring integrity constraints on critical workflows.

## Follow-up questions

- Which queries break first at 10x scale?
- What data can be eventually consistent safely?
- How would you migrate this schema with zero downtime?
- When would you split write model and read model?

## Variants and extensions

- CQRS-style read projections for feed/search surfaces.
- Multi-tenant schemas (`tenant_id`) with partition-aware indexes.
- Event-log plus materialized views for audit-heavy systems.

## Related Topics

- [SQL vs NoSQL](./sql-vs-nosql.md)
- [Indexing](./indexing.md)
- [Database Normalization Theory](./database-normalization-theory.md)
- [ACID Properties](./acid-properties.md)
- [Sharding](./sharding.md)
- [Database Sharding (HLD)](../../03-hld-concepts/database-sharding/)
- [News Feed HLD](../../04-hld-projects/news-feed/)
