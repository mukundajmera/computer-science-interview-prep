# Interview Questions: MongoDB

## Basic Questions

### 1. What is MongoDB best at in system design?

**Q**: When would you pick MongoDB over a relational database?

**A**: Pick MongoDB when the core data is document-shaped, hot access paths are known, and the system benefits from reading or writing one aggregate at a time. Examples include product catalogs, user profiles, carts, content metadata, and configuration records. I would not pick it just because "schema is flexible"; I still need deliberate document boundaries, indexes, and consistency choices.

### 2. What is the document model?

**Q**: Explain documents and collections in interview terms.

**A**: A document is the stored record, made of fields and values that can include nested objects and arrays. A collection groups related documents. The modeling question is whether the API usually needs one aggregate document, or whether the data is relational enough that joins and constraints are the better fit.

### 3. Does flexible schema mean no schema?

**Q**: How do you prevent messy production data?

**A**: Flexible schema means documents in a collection can evolve, not that the system should accept arbitrary shapes. I would enforce contracts in application code, version documents when needed, backfill old shapes, and consider database validation for critical fields.

## Data Modeling

### 4. When do you embed versus reference?

**Q**: How would you decide for orders, reviews, comments, or followers?

**A**: Embed bounded data that is read and written with the parent, such as order line items captured at purchase time. Reference unbounded or independently changing data, such as all product reviews, all comments on a viral post, or all followers for a celebrity account. The rule is locality versus growth and independent lifecycle.

### 5. How do you model a shopping cart?

**Q**: A user cart has items, coupons, totals, and timestamps. What is the MongoDB shape?

**A**: A cart can be one document keyed by `user_id` or `cart_id`, with bounded line items, coupon state, and computed totals. I would index the lookup key and maybe status/expiration for cleanup. If carts can become very large or require independent item workflows, split items into a separate collection.

### 6. How do you model product reviews?

**Q**: Product pages need summary rating and recent reviews.

**A**: Keep the product document with summary fields such as `avg_rating`, `review_count`, and maybe a small preview of recent reviews. Store full reviews in a separate collection keyed by `product_id` plus time or helpfulness. This avoids an unbounded reviews array while keeping the product page fast.

## Indexing And Query Paths

### 7. How do you choose indexes?

**Q**: What is your index design process?

**A**: I list hot queries first, then define compound indexes that match filters and sort order. For example, a tenant order list may need `(tenant_id, status, created_at)`. I avoid indexing every possible field because indexes improve reads but make writes and storage more expensive.

### 8. What is a collection scan and why is it bad?

**Q**: Why should interviewers care?

**A**: A collection scan means MongoDB may need to inspect every document in the collection to answer the query. That becomes slow and resource-heavy as data grows. Hot paths should have appropriate indexes or a different data model.

### 9. Can MongoDB replace Elasticsearch for search?

**Q**: We need product search with relevance ranking, typo tolerance, and faceting.

**A**: I would usually keep MongoDB as source of truth or operational store and project searchable data to [Elasticsearch](../elasticsearch/) or another search system when relevance ranking is central. MongoDB indexes are useful for exact and structured query paths, but search relevance is a specialized workload.

## Consistency, Replication, And Transactions

### 10. What is a replica set?

**Q**: Explain MongoDB replication simply.

**A**: A replica set is a group of `mongod` instances maintaining the same data set. One data-bearing member is primary, and secondaries replicate from it. This gives redundancy and failover, but applications still need timeouts, retries, and consistency choices.

### 11. What are read concern and write concern?

**Q**: How do they affect correctness?

**A**: Write concern controls the acknowledgment required for writes. Read concern controls consistency and isolation properties for reads from replica sets and sharded clusters. For correctness-sensitive flows, I would choose stronger settings and primary reads; for availability or latency-sensitive reads, I may accept staleness explicitly.

### 12. How do you provide read-your-writes?

**Q**: A user updates a profile and immediately refreshes the page.

**A**: Route the immediate read to the primary or use a session/consistency-safe path rather than a lagging secondary. Also make the write acknowledgment strong enough for the product requirement. If secondary reads are used elsewhere, the UI or API contract should tolerate staleness.

### 13. When do you use transactions?

**Q**: MongoDB supports multi-document transactions. Should every write use them?

**A**: No. Use transactions when multiple documents must change atomically, such as inventory reservation plus order transition. But for many hot paths, model the aggregate so the write is single-document. MongoDB's own docs caution that distributed transactions have higher cost and should not replace effective schema design.

## Sharding

### 14. When do you shard?

**Q**: Should every MongoDB deployment start sharded?

**A**: No. Start with a replica set if it meets storage and throughput needs. Shard when data size, working set, or write/read throughput exceeds what vertical scaling and replica-set design can handle. Sharding adds routing, metadata, balancing, and shard-key complexity.

### 15. How do you choose a shard key?

**Q**: What makes a good shard key?

**A**: A good shard key has high cardinality, distributes reads and writes evenly, appears in common targeted queries, and avoids hot monotonic ranges. A bad shard key creates hot shards or scatter-gather queries.

### 16. What is a scatter-gather query?

**Q**: Why is it a problem in sharded MongoDB?

**A**: It is a query that cannot target a small set of shards, so the router must fan out to many or all shards and merge results. This increases latency and cluster load. The fix is usually a better shard key, query shape, or derived read model.

## Aggregation And Operations

### 17. When is aggregation appropriate?

**Q**: Can we run analytics directly in MongoDB?

**A**: Aggregation pipelines are useful for grouped operational queries, scoped reporting, and materialized read views. I would avoid unbounded analytics on hot production collections. For heavy analytics, stream or export data to an analytics store.

### 18. What failure modes should you mention?

**Q**: What can go wrong in production?

**A**: Collection scans, over-indexed writes, unbounded arrays, large documents, stale secondary reads, primary failover ambiguity, hot shard keys, scatter-gather queries, and long-running aggregations. I would monitor slow queries, index usage, replication lag, write latency, storage growth, and shard balance.

### 19. How do you migrate schema safely?

**Q**: Documents are flexible, but the application changes shape. What do you do?

**A**: Use backward-compatible readers, write the new shape, backfill old documents gradually, and keep metrics for old-shape reads. For risky changes, dual-read or dual-write temporarily and add validation after the migration is complete.

### 20. How do you handle retries after failover?

**Q**: A write times out during primary failover. What is the safe API pattern?

**A**: Make the write idempotent with an operation id or natural idempotency key. On retry, the server can return the existing result instead of duplicating work. This matters because the client may not know whether the first attempt committed before the error.

## Common Follow-ups

- What is the aggregate boundary for this system?
- Which exact queries are hot, and what indexes serve them?
- Which data is embedded, referenced, or duplicated?
- Which reads can tolerate stale secondary data?
- What write concern and read concern does the critical path use?
- Which invariants require transactions?
- What shard key do you choose, and what value could become hot?
- How do you backfill schema changes without downtime?

## Red Flags To Avoid

- "MongoDB has no schema, so we can store anything."
- "We can shard later without thinking about the shard key now."
- "Secondary reads are always safe."
- "Transactions make MongoDB equivalent to a relational database for all workloads."
- "Add indexes for every filter."
- "Store all comments, followers, or events in one embedded array."
- "Run all analytics on the production cluster."

## 60-90 Second Explanation

"I pick MongoDB when the domain is naturally aggregate-shaped and the hot access paths can be served by indexed document reads and writes. I model documents around locality: embed bounded data that is read and written together, and reference unbounded or independently changing data. Then I design compound indexes from the exact query shapes and avoid over-indexing because every index adds write cost.

For reliability, I run replica sets and make read/write concern choices explicit. Primary reads and stronger write acknowledgment are safer for read-after-write flows; secondary reads are only for paths that tolerate lag. Transactions are available for multi-document atomicity, but I use them narrowly and prefer a schema that keeps common writes single-document. If the data or throughput outgrows one replica set, I shard, and the shard key must distribute load evenly while supporting targeted queries. The big production risks are bad shard keys, unbounded arrays, stale reads, collection scans, and broad aggregations on the operational database."

## Rubric

| Score | Interview signal |
|---|---|
| 1 | Mentions only "NoSQL" and "flexible schema" |
| 3 | Explains documents, embed/reference, indexes, and replica sets correctly |
| 5 | Connects document modeling to access patterns, consistency settings, transactions, shard-key choice, failure modes, and observability |

## Related Concepts

- [MongoDB Theory](./THEORY.md)
- [NoSQL Databases](../nosql-databases/)
- [Database Replication](../database-replication/)
- [Database Sharding](../database-sharding/)
- [Read Scaling](../read-scaling/)
- [Write Scaling](../write-scaling/)
- [Distributed Transactions](../distributed-transactions/)
- [Elasticsearch](../elasticsearch/)

## Short Source Notes

- MongoDB documents, data modeling, indexes, replication, read/write concern, transactions, sharding, shard keys, and aggregation facts are based on the MongoDB Database Manual: <https://www.mongodb.com/docs/manual/>.
- The transaction guidance is intentionally conservative: MongoDB supports distributed transactions, but the manual notes they carry greater cost than single-document writes and should not replace effective schema design.
