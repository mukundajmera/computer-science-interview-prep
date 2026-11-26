# Database Indexing

Indexes trade extra write/storage cost for faster reads. Interview performance discussions should tie index choices to concrete query patterns.

---

## Practical Cost Model

Without an index, selective lookup becomes table scan work. With a matching index, lookup narrows quickly to relevant rows/pages.

- Read benefit: lower latency and CPU for selective queries.
- Write cost: each insert/update touches index structures.
- Storage cost: index footprint can be significant on large tables.

---

## Index Families You Should Know

| Type | Best for | Not ideal for |
|------|----------|---------------|
| B-tree | Equality + range + ordering | Very low-selectivity columns |
| Hash | Equality lookups | Range/order queries |
| Inverted | Full-text term lookup | Transactional point lookups |
| Geospatial | Proximity/region queries | Generic scalar filtering |

Use B-tree unless the workload clearly needs specialized retrieval.

---

## Composite and Covering Strategy

- Composite index order matters; align with predicate prefix and sort pattern.
- Covering indexes can remove table lookups for hot read paths.
- Keep coverage selective; over-wide indexes increase write and memory pressure.

Example:

```text
Query: WHERE user_id = ? ORDER BY created_at DESC LIMIT 20
Index: (user_id, created_at DESC)
```

---

## LSM vs B-tree (high level)

- B-tree engines: balanced read/write for OLTP.
- LSM engines: write-optimized ingest, more complex read/compaction behavior.

This is mostly a storage-engine-level choice; mention only when workload is clearly write-heavy at large scale.

---

## Requirements and constraints

- Every proposed index must map to an important query.
- Maintain write throughput budgets while adding read indexes.
- Avoid indexing low-selectivity, rarely filtered fields.
- Revisit index set as traffic/query mix evolves.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Query linkage | Index tied to specific endpoint/query | "Index everything important" |
| Trade-off awareness | Mentions write/storage overhead | Assumes free read speedup |
| Composite design | Correct column order rationale | Random index column ordering |
| Scope control | Adds minimal useful set first | Proposes many speculative indexes |

## Common pitfalls

- Adding indexes without checking query selectivity.
- Ignoring order of columns in composite indexes.
- Treating full-text/geospatial search as normal B-tree workloads.
- Forgetting that high write tables can degrade with excessive indexes.

## Follow-up questions

- Which index would you drop first if write latency regresses?
- How do you detect missing vs unused indexes in production?
- When should you move text search to Elasticsearch?
- How do you combine indexing with caching for the same endpoint?

## Variants and extensions

- Partial/filtered indexes for sparse hot subsets.
- Materialized views + narrow indexes for dashboard queries.
- Async search indexing pipeline for full-text workloads.

## Related Topics

- [Data Modeling](./data-modeling.md)
- [SQL vs NoSQL](./sql-vs-nosql.md)
- [Caching (HLD)](../../03-hld-concepts/caching/)
- [Elasticsearch (HLD)](../../03-hld-concepts/elasticsearch/)
- [E-commerce HLD](../../04-hld-projects/ecommerce-backend/)
