# Database Indexing

Indexes trade extra write/storage cost for faster reads. Interview performance discussions should tie index choices to concrete query patterns.

---

## Practical Cost Model

Without an index, selective lookup becomes table scan work. With a matching index, lookup narrows quickly to relevant rows/pages.

- Read benefit: lower latency and CPU for selective queries.
- Write cost: each insert/update touches index structures.
- Storage cost: index footprint can be significant on large tables.

---

## How a B-Tree Index Is Searched and Updated

The default index structure is the B-tree (in practice, the B+ tree): a balanced tree of fixed-size pages with a root, internal pages, and leaf pages holding the sorted keys. Each page holds hundreds of keys, so fanout is high and even a very large table is only about three to four levels deep: a point lookup costs one page read per level, which is why indexed lookups stay fast as the table grows.

- Equality lookup: descend from the root to the single leaf page holding the key.
- Range lookup: descend once to the leaf holding the range start, then walk forward; B+ tree leaves are linked in key order, so ranges read consecutive leaves sequentially.
- Updates and page splits: an insert walks to its target leaf; a full leaf splits in two and pushes a separator key to the parent, which can itself split. Each split turns one logical row write into several physical page writes, all logged in the write-ahead log. This is write amplification.
- Insert pattern matters: append-ordered keys (auto-increment ids, timestamps) fill pages densely at the right edge, while random keys (random UUIDs) scatter inserts across the tree, causing more splits and worse page utilization.

For the internal structure and concurrency control of these trees, see [B+ Tree Internals and Latch Crabbing](./b-plus-tree-indexing-and-latch-crabbing.md).

---

## Index Families You Should Know

| Type | Best for | Not ideal for |
|------|----------|---------------|
| B-tree | Equality + range + ordering | Very low-selectivity columns |
| Hash | Equality lookups | Range/order queries |
| Inverted | Full-text term lookup | Transactional point lookups |
| Geospatial | Proximity/region queries | Generic scalar filtering |

Use B-tree unless the workload clearly needs specialized retrieval.

## Beyond B-Trees: Hash, GIN, GiST, and Bitmap

Specialized families exist because some data has no useful total order or needs different match semantics.

- **Hash**: maps a key hash to a bucket; answers `=` predicates only, since hashing destroys order.
- **GIN (Generalized Inverted Index)**: maps each element of a composite value (a word, array element, JSON key) to the rows containing it; the workhorse for full-text, arrays, and document fields.
- **GiST (Generalized Search Tree)**: an extensible balanced-tree framework for types with no single sort order, such as geometric shapes, ranges, and nearest-neighbor search.
- **Bitmap**: one bitmap per column value, one bit per row; filters over low-cardinality columns become fast bitmap AND/OR operations. Standard in analytical stores, but expensive under concurrent writes, so it fits read-heavy warehouses rather than OLTP tables.

---

## Selectivity and When the Planner Skips an Index

Selectivity is the fraction of rows a predicate matches; the smaller the fraction, the more selective the predicate. Selectivity drives the planner's cost estimate more than the mere existence of an index.

- A highly selective predicate (matching a tiny share of rows) favors an index: a few tree pages plus a few row fetches beat scanning everything.
- A weakly selective predicate (matching a large share of the table) favors a sequential scan: sequential I/O beats random page-per-row hops, and every index hit still costs a heap fetch for the row itself.

Common reasons an index exists but the planner ignores it:

- Stale table statistics, so the row-count estimate is wrong.
- The predicate wraps the column in a function the index does not cover (`lower(email) = ?` against a plain `email` index).
- Type mismatches or implicit casts between the column and the compared value.
- A table small enough that scanning it outright is cheaper than touching the index.
- Physical row order correlating poorly with index order, inflating the random-I/O estimate.

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

### Leftmost-Prefix Rule

A composite index `(a, b, c)` can serve predicates on `(a)`, on `(a, b)`, and on `(a, b, c)`, because those prefixes keep the index's sort order usable. It cannot efficiently serve predicates on `(b)` or `(c)` alone, because without the leftmost column the matching entries are scattered across the whole index.

```text
Index: (tenant_id, status, created_at)

WHERE tenant_id = ?                                       -> uses the index
WHERE tenant_id = ? AND status = ?                        -> uses the index
WHERE tenant_id = ? AND status = ? ORDER BY created_at    -> uses the index, no extra sort
WHERE status = ?                                          -> leftmost column missing: not used
```

The practical ordering rule: equality-tested columns first, then the range or sort column last.

### Covering and Partial Indexes

- A covering index includes every column a hot query returns, so the engine answers from the index alone (an index-only scan) and never touches the table pages. Powerful for the hottest read paths, but every extra column widens the index and raises write and memory cost.
- A partial index carries a `WHERE` clause and indexes only a hot subset, such as open orders rather than all orders. It stays small and cheap to maintain when queries consistently filter to that subset.

---

## LSM vs B-tree (high level)

- B-tree engines: balanced read/write for OLTP.
- LSM engines: write-optimized ingest, more complex read/compaction behavior.

A B-tree updates pages in place, keeping reads predictable but paying write amplification through splits and random page writes. An LSM tree buffers writes in memory, flushes sorted runs to disk, and merges them during background compaction, turning random writes into sequential ones for very high ingest throughput. The costs move to reads (a lookup may consult several runs) and to compaction I/O. Choose B-tree engines by default for OLTP; consider LSM engines for write-dominated workloads like logging, telemetry, and time-series ingest.

This is mostly a storage-engine-level choice; mention only when workload is clearly write-heavy at large scale.

---

## Interview Index-Design Checklist

1. Name the hot queries and endpoints before proposing any index.
2. Propose one index per important query, starting minimal.
3. Order composite columns: equality predicates first, range or sort column last; check the order against the leftmost-prefix rule.
4. Estimate selectivity; skip indexes on low-selectivity, rarely filtered columns.
5. Consider a covering index for the single hottest read path, and a partial index for a stable hot subset.
6. Budget the write side: every index adds write amplification and storage on every insert and update.
7. Verify with the query plan (`EXPLAIN`) that the planner actually uses the index, and revisit the index set as the query mix evolves.

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
- [B+ Tree Internals and Latch Crabbing](./b-plus-tree-indexing-and-latch-crabbing.md)
- [Sharding](./sharding.md)
- [Caching (HLD)](../../03-hld-concepts/caching/)
- [Elasticsearch (HLD)](../../03-hld-concepts/elasticsearch/)
- [E-commerce HLD](../../04-hld-projects/ecommerce-backend/)
