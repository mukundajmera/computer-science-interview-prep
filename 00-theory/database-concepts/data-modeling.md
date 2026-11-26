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

Example starter schema:

```text
users(id PK, email UNIQUE, username, created_at)
posts(id PK, user_id FK -> users.id, body, created_at)
likes(user_id FK -> users.id, post_id FK -> posts.id, created_at)
```

---

## Normalization vs Denormalization

- Normalize first to control consistency complexity.
- Denormalize for high-read hot paths (feed cards, counters, projections).
- Prefer derived views/caches before duplicating source-of-truth fields broadly.

---

## Sharding Considerations

- Choose shard keys aligned with dominant query routing.
- Prefer high-cardinality, stable keys.
- Avoid strategies that create hot partitions on current-time writes.

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
- [Sharding](./sharding.md)
- [Database Sharding (HLD)](../../03-hld-concepts/database-sharding/)
- [News Feed HLD](../../04-hld-projects/news-feed/)
