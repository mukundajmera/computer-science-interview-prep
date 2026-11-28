# MongoDB

MongoDB is a document database used in system design when the natural unit of data is an aggregate-shaped document and the dominant access patterns can be served by indexed document reads, writes, and aggregations.

## Mental Model

Think of MongoDB as a distributed document store, not as a relational database with a different syntax.

- **Document**: the unit of storage, represented as field-value pairs; values can include nested documents and arrays.
- **Collection**: a group of documents, usually representing one aggregate type such as users, orders, products, posts, or sessions.
- **Index**: a read-path accelerator that reduces scans, but every maintained index also adds write cost.
- **Replica set**: multiple `mongod` members that keep the same data set; one data-bearing member is primary and the others are secondaries.
- **Sharded cluster**: horizontal partitioning across shards, with `mongos` routers and config servers coordinating routing and metadata.

The interview framing is: model documents around the read and write paths, index only the important query shapes, choose consistency settings intentionally, then shard only when one replica set cannot meet storage or throughput needs.

## Why It Matters in HLD

MongoDB is common in interviews because it forces explicit trade-offs:

- Flexible document shape versus schema governance.
- Embedded data locality versus duplicated data and document growth.
- Index-rich reads versus slower, more expensive writes.
- Replica-set availability versus stale secondary reads and failover behavior.
- Sharding scale-out versus shard-key, routing, and operational complexity.
- Multi-document transactions versus modeling data so the common write is single-document when possible.

## When To Use

Use MongoDB when:

- The main entity is naturally document-shaped, such as product catalog items, user profiles, content documents, configuration records, shopping carts, or event metadata.
- Most hot reads fetch one aggregate by key or by a small set of indexed predicates.
- The schema evolves frequently, but the application can still enforce validation and backward compatibility.
- Embedding related data lets the system answer common requests in one read without cross-service joins.
- You need replica-set durability and optional horizontal scaling with sharding.

## When Not To Use

Prefer another store when:

- The product relies on complex joins, strict relational constraints, and ad-hoc analytical SQL.
- Cross-entity transactions are the core hot path rather than an exception.
- You cannot tolerate careful shard-key design or operational ownership for a sharded cluster.
- Workloads are dominated by text relevance search; use a search system projection such as [Elasticsearch](../elasticsearch/) instead.
- Workloads are append-heavy analytics over large time windows; consider [stream processing](../stream-processing/) or OLAP-oriented stores.

## Data Modeling

### Embed When Locality Wins

Embed fields or subdocuments when they are usually read together, updated together, and bounded in size.

Good examples:

- Product document with current price, inventory summary, and top-level attributes.
- User profile with preferences and small settings objects.
- Order document with line items captured at purchase time.

Benefits:

- Fewer round trips.
- Single-document atomicity for the aggregate.
- Query shape matches the API response.

Risks:

- Large or unbounded arrays can grow documents and make updates expensive.
- Duplicated embedded facts need reconciliation when the source changes.
- Over-embedding can make unrelated write paths contend on the same document.

### Reference When Independence Wins

Reference separate documents when data is large, high-cardinality, updated independently, or reused across many parents.

Good examples:

- Product reviews separated from the product document after a small preview set.
- Users referenced by posts, comments, and likes.
- Ledger entries separated from account summary documents.

The practical rule: embed for bounded, co-accessed state; reference for unbounded, independently changing state.

## Index Strategy

Indexes should be designed from the queries:

| Query shape | Index implication |
|---|---|
| Fetch by `_id` or external id | Unique lookup index |
| Tenant-scoped list by status and time | Compound index such as `(tenant_id, status, created_at)` |
| Prefix/filter plus sort | Compound index that matches filter and sort order |
| Rare admin search | Avoid over-indexing if a slower path is acceptable |
| Query on large unbounded arrays | Validate cardinality and write cost before indexing |

Index interview checklist:

1. Name the hot queries.
2. State the compound indexes.
3. Confirm each hot query can avoid a collection scan.
4. Budget write amplification from each index.
5. Monitor slow queries and index usage, then prune unused indexes.

## Replication And Consistency

Replica sets provide redundancy and failover. A primary receives writes, secondaries replicate the data set, and failover elects a new primary when needed.

Consistency is controlled by read and write settings:

- **Write concern** decides how much acknowledgment a write requires before success is returned.
- **Read concern** controls the consistency and isolation properties of data read from replica sets and sharded clusters.
- **Read preference** decides which member can serve reads; secondary reads can improve read scaling but may see lagged data.

Interview-safe defaults:

- Use majority-style acknowledgement for correctness-sensitive writes.
- Use primary reads for read-after-write correctness unless the application can tolerate staleness.
- State staleness and failover behavior explicitly instead of saying "strongly consistent" without qualifiers.
- For user-visible read-your-writes, use sessions or route the read to a consistency-safe path.

## Transactions

MongoDB supports multi-document transactions on replica sets and sharded clusters. They are useful when multiple documents must change atomically.

Use transactions for:

- Payment state plus idempotency record update.
- Inventory reservation plus order state transition.
- Account summary plus audit event when the system requires atomic visibility.

Avoid making transactions the default modeling strategy:

- Single-document writes are simpler and usually cheaper.
- Distributed transactions carry higher performance cost.
- A denormalized model can often remove the need for a transaction on the hot path.

In interviews, say which invariants are single-document and which truly require a transaction.

## Sharding

Sharding distributes data across machines for very large data sets or high-throughput workloads.

A sharded cluster includes:

- **Shards**: each contains a subset of sharded data and is deployed as a replica set.
- **`mongos` routers**: application-facing query routers.
- **Config servers**: metadata and configuration storage for the cluster.

The shard key is the core design decision. It determines how documents are distributed and how queries route.

Good shard keys tend to:

- Have high cardinality.
- Spread writes and storage evenly.
- Appear in common targeted queries.
- Avoid a single hot value or monotonically increasing hot range.
- Preserve tenant isolation if tenant-level routing is important.

Poor shard keys cause:

- Hot shards.
- Scatter-gather queries.
- Chunk movement pressure.
- Hard migrations or resharding work later.

## Aggregation

Aggregation pipelines process multiple documents and return computed results. They are useful for:

- Grouping and summarizing operational data.
- Building materialized read views.
- Running scoped analytics without moving data to another platform.
- Precomputing dashboards for small to medium operational windows.

Do not use aggregation as an excuse to run unbounded analytics on the primary database. For heavy analytics, export or stream data into an analytics path.

## Scaling And Failure Modes

| Pressure | First response | Common failure mode |
|---|---|---|
| Read latency | Add or tune indexes, reduce document payload, cache hot reads | Collection scans and large result sets |
| Write throughput | Reduce unnecessary indexes, batch safely, partition workload | Index write amplification |
| Large documents | Split unbounded arrays or large blobs into separate collections/storage | Document growth and update pressure |
| Replica lag | Reduce secondary read dependence, monitor lag, scale hardware | Stale reads after writes |
| Primary failover | Retry idempotently, handle transient errors, use sane timeouts | Duplicate writes without idempotency |
| Storage growth | Archive cold data, shard when justified, compact retention model | Sharding too late or with a poor key |
| Hot tenant/key | Bucket, add write distribution, or isolate heavy tenants | One shard or primary saturates |

## Operational Trade-offs

- **Schema flexibility is not schema absence**: enforce validation in application code, migration jobs, and optional database validators.
- **Indexes are production features**: each index changes write cost and operational rollout risk.
- **Backups and restore drills matter**: replica sets are not a substitute for backup.
- **Retries require idempotency**: failover and network errors can make client-visible state ambiguous.
- **Observability must include storage, slow queries, index usage, replication lag, lock/queue pressure, and shard balance.**

## Common Pitfalls

- Treating MongoDB as a drop-in replacement for relational joins.
- Embedding unbounded arrays such as all comments, all followers, or all events.
- Adding indexes for every possible filter without measuring write cost.
- Choosing `_id` or timestamp as a shard key when it creates write concentration.
- Running broad aggregations on hot production collections.
- Ignoring read/write concern and then being surprised by stale reads or rollbacks.
- Depending on multi-document transactions for every write instead of modeling aggregate boundaries.

## 60-90 Second Answer

"I use MongoDB when the domain fits aggregate-oriented documents and the main access paths can be served by indexed document reads and writes. I start by modeling the document boundary: embed bounded data that is read and written together, and reference unbounded or independently changing data. Then I name the hot queries and create only the compound indexes needed to avoid scans, because indexes improve reads but add write cost.

For reliability I usually run a replica set and choose read and write concern based on correctness needs. Majority-style writes and primary reads are safer for read-after-write flows; secondary reads are fine only where staleness is acceptable. Transactions exist for multi-document atomicity, including sharded clusters, but they are not a substitute for good schema design. If one replica set cannot handle the dataset or throughput, I shard, and the shard key becomes the design: it must distribute load evenly and support targeted queries. The main risks are bad shard keys, unbounded embedded arrays, over-indexing, stale reads, and broad aggregations on the operational database."

## Interview Rubric

| Score | Signal |
|---|---|
| 1 | Says "NoSQL is flexible" without access patterns, indexes, consistency, or shard-key reasoning |
| 3 | Correctly explains documents, indexes, replica sets, and basic embed/reference trade-offs |
| 5 | Designs from access patterns, states read/write concern choices, handles transactions narrowly, chooses a shard key with failure modes, and names operational metrics |

## Follow-up Questions

1. What document boundary would you choose for an order, cart, product, or social post?
2. Which fields are in your compound indexes, and why that order?
3. What reads can tolerate secondary lag?
4. Which invariants fit single-document atomicity, and which require transactions?
5. What shard key avoids hot shards while still supporting targeted queries?
6. How do you migrate a document schema without downtime?
7. What metrics tell you an index or shard-key decision is failing?

## 📊 Diagrams

- [Replica set election](./diagrams/replica-set-election.mmd): how the primary serves writes and replicates to secondaries in normal operation, and how the set elects a new primary when heartbeats fail while clients retry idempotently.
- [Write concern acknowledgement](./diagrams/write-concern-acknowledgement.mmd): how the chosen write concern (`w: 1` versus majority) decides when a write is acknowledged and how durable it stays across failover.

## Related Concepts And Projects

- [NoSQL Databases](../nosql-databases/)
- [Database Replication](../database-replication/)
- [Database Sharding](../database-sharding/)
- [Read Scaling](../read-scaling/)
- [Write Scaling](../write-scaling/)
- [Distributed Transactions](../distributed-transactions/)
- [Contention Control](../contention-control/)
- [Monitoring and Observability](../monitoring-observability/)
- [E-commerce Backend](../../04-hld-projects/ecommerce-backend/)
- [News Feed](../../04-hld-projects/news-feed/)
- [Social Post Search](../../04-hld-projects/social-post-search/)
- [Amazon Orders Case Study](../../case-studies/amazon-orders/)

## Short Source Notes

- MongoDB documents are field-value records whose values can include nested documents and arrays: <https://www.mongodb.com/docs/manual/core/document/>.
- MongoDB data modeling emphasizes flexible schema and document-model locality: <https://www.mongodb.com/docs/manual/data-modeling/>.
- MongoDB indexes reduce scanned documents for supported query shapes, but each index also affects write performance: <https://www.mongodb.com/docs/manual/indexes/>.
- Replica sets, read concern, write concern, transactions, sharding, shard keys, and aggregation behavior are summarized from MongoDB Database Manual pages: <https://www.mongodb.com/docs/manual/replication/>, <https://www.mongodb.com/docs/manual/reference/read-concern/>, <https://www.mongodb.com/docs/manual/reference/write-concern/>, <https://www.mongodb.com/docs/manual/core/transactions/>, <https://www.mongodb.com/docs/manual/sharding/>, <https://www.mongodb.com/docs/manual/core/sharding-shard-key/>, and <https://www.mongodb.com/docs/manual/aggregation/>.
