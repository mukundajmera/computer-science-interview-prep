# Technology Selection Guide

Use this page to pick a component category first and name a concrete product second. Interviewers care far more about why a storage engine, queue, or cache matches your access pattern and failure tolerance than whether you memorize vendor features.

## How to Frame a Technology Choice Aloud

1. **Start with the workload and invariant** — state the dominant read/write shape, ordering need, and whether stale reads or duplicate work are acceptable.
2. **Name the category before the product** — say "a wide-column store such as Cassandra" rather than jumping straight to a brand name.
3. **State what you are giving up** — every choice trades away something such as joins, strong consistency, replayability, or operational simplicity.
4. **Justify every extra box** — start with one relational store and introduce a cache, search index, event log, or coordinator only when a concrete bottleneck demands it.

---

## 1. Primary Data Storage

If the storage paradigm itself is still unclear, review [SQL vs NoSQL](./sql-vs-nosql/THEORY.md) and [Storage Engine Internals](./storage-engine-internals/THEORY.md) first.

| Category (Product Examples) | When It Fits | When It Doesn't | Interview Trade-off to Say Aloud | Concept Guide |
|---|---|---|---|---|
| **Relational / OLTP** (PostgreSQL, MySQL) | Structured entities, multi-row ACID transactions, foreign keys, ad-hoc joins, and financial or inventory invariants. | Massive unstructured ingest where write volume outstrips a single primary and cross-shard joins would dominate. | "We get ACID invariants and flexible queries upfront, accepting that horizontal write scaling later requires sharding and careful schema migrations." | [Relational](./relational-databases/THEORY.md), [PostgreSQL](./postgresql/THEORY.md), [MySQL](./mysql/THEORY.md) |
| **Wide-column store** (Cassandra) | High-volume append-heavy writes, predictable partition-key plus clustering-key lookups, and multi-region availability. | Ad-hoc queries, joins, frequent updates/deletes across partitions, or strict cross-row transactions. | "We model tables strictly around known read queries and accept eventual consistency by default in exchange for leaderless write scale and high availability." | [NoSQL](./nosql-databases/THEORY.md), [Cassandra](./cassandra/THEORY.md) |
| **Document store** (MongoDB) | Aggregate-shaped records (profiles, catalogs, CMS items) with evolving optional fields read and updated mostly as one document. | Heavily normalized graphs with many-to-many joins or workflows needing frequent multi-collection transactions. | "Embedding keeps single-document reads fast and schema changes lightweight, at the cost of data duplication and careful shard-key planning later." | [NoSQL](./nosql-databases/THEORY.md), [MongoDB](./mongodb/THEORY.md) |
| **Key-value store** (DynamoDB, Redis) | Exact-match lookups by primary key (sessions, feature flags, cart state, metadata) where access paths are simple and fixed. | Complex filtering, ad-hoc range scans across arbitrary attributes, or relational reporting. | "Restricting access to key lookups gives predictable low-latency scaling, but every new query pattern requires a new index or denormalized table." | [NoSQL](./nosql-databases/THEORY.md), [DynamoDB](./dynamodb/THEORY.md), [Redis](./redis/THEORY.md) |
| **Time-series store** (TimescaleDB, InfluxDB, Prometheus) | Append-only timestamped metrics, IoT telemetry, and time-window aggregations with automatic retention rollups. | Random row updates, transactional business records, or high-cardinality user-ID tag explosions. | "Time-partitioned storage and specialized compression make range queries cheap, provided we bound tag cardinality and avoid mutating historical points." | [Time Series](./time-series-databases/THEORY.md) |
| **Object / blob store** (S3, GCS, MinIO) | Large immutable files (media, backups, exports, data-lake segments) paired with metadata in a database. | Low-latency small random reads/writes, in-place byte updates, or POSIX directory locking. | "We offload bulky binary payloads to durable, horizontally scalable buckets and keep only lightweight metadata and object keys in the primary database." | [Object Storage](./object-storage/THEORY.md), [Large Blobs](./large-blob-handling/THEORY.md) |

**Picking between PostgreSQL and MySQL:**
- Name **PostgreSQL** when you want rich indexing (GIN/GiST), native JSONB alongside relational tables, or strict standards-compliant MVCC semantics.
- Name **MySQL** when you want an InnoDB clustered primary-key layout with straightforward primary-replica operational tooling for classic OLTP web workloads.
- In most interviews either is a fine default; state why relational fits first, then mention one concrete reason for the engine you named.

---

## 2. Messaging: Queue vs. Log

Separate **task distribution** (work deleted once acknowledged) from **event streaming** (immutable log retained for replay and fan-out).

| Category (Product Examples) | When It Fits | When It Doesn't | Interview Trade-off to Say Aloud | Concept Guide |
|---|---|---|---|---|
| **Point-to-point message queue** (RabbitMQ, SQS) | Background jobs, competing worker pools, complex per-message routing, delayed retries, and dead-letter queues. | Replaying historical events, feeding many independent downstream consumers from one stream, or strict large-scale retention. | "A smart broker handles routing, retries, and per-message acknowledgments cleanly, but messages are ephemeral and deep backlogs hurt broker performance." | [Message Queues](./message-queues/THEORY.md), [Queue Evolution](./message-queue-evolution/THEORY.md) |
| **Distributed commit log** (Kafka) | High-throughput event ingestion, multiple independent consumer groups, ordered per-key streams, and time-based replay. | Simple fire-and-forget job queues needing per-message priority, selective ack/nack, or ad-hoc routing keys. | "Moving offset tracking to consumers unlocks sequential disk throughput and replayability, at the cost of partition-level ordering limits and rebalancing overhead." | [Kafka](./kafka/THEORY.md), [Queue Evolution](./message-queue-evolution/THEORY.md) |
| **Decoupled log and queue** (Pulsar) | Multi-tenant cloud workloads needing both queue and streaming semantics with independent compute and storage scaling. | Small teams or simple single-service pipelines where operating separate broker and storage tiers adds unnecessary complexity. | "Decoupling stateless brokers from segmented storage removes partition-rebalancing pain on scale-out, but adds an extra distributed storage layer to manage." | [Queue Evolution](./message-queue-evolution/THEORY.md) |

**Reliability guardrails to mention:**
- Assume **at-least-once** delivery and make consumers safe under retries with [Idempotency](./idempotency/THEORY.md).
- When a request must both commit to a database and emit an event, use the [Transactional Outbox](./distributed-transactions-saga-outbox/THEORY.md) instead of a fragile dual write.

---

## 3. Caching and Cache Patterns

A cache answer is incomplete if you only say "put Redis in front." State both the **cache tier** and the **read/write pattern**, then name the staleness boundary.

| Pattern / Tier (Product Examples) | When It Fits | When It Doesn't | Interview Trade-off to Say Aloud | Concept Guide |
|---|---|---|---|---|
| **Cache-aside / lazy loading** (Redis, Memcached) | General read-heavy workloads where only hot keys belong in memory and brief staleness is acceptable. | Strict read-your-writes paths where stale reads violate business correctness (balances, seat locks). | "The application stays in control and only caches requested data, but the first request pays a cache-miss penalty and concurrent updates can briefly go stale." | [Caching](./caching/THEORY.md), [Redis](./redis/THEORY.md) |
| **Read-through cache** (managed cache proxy) | Uniform key lookups where you want cache-fill logic hidden behind one data-access layer. | Complex multi-table queries or custom fallback logic per caller. | "Centralizing misses simplifies application code, though we still pay cold-miss latency and couple the cache provider to the backing store schema." | [Caching](./caching/THEORY.md) |
| **Write-through cache** (Redis + primary DB) | Read-heavy data that must stay fresh immediately after writes (configuration, session profiles). | Write-heavy workloads where most newly written keys are never read again. | "Every write updates cache and database synchronously to keep reads fresh, which adds write latency and wastes memory on cold writes." | [Caching](./caching/THEORY.md) |
| **Write-behind / write-back** (Redis / local buffer) | Burst-heavy counters, analytics, or telemetry where batching writes to the primary store is essential. | Durable financial or order writes where losing unflushed cache memory on a node crash is unacceptable. | "Acknowledging at the cache absorbs write spikes and batches disk I/O, trading away durability if the cache node fails before flushing." | [Caching](./caching/THEORY.md), [Write Scaling](./write-scaling/THEORY.md) |
| **CDN / edge cache** (CloudFront, Cloudflare, Fastly) | Static assets, media chunks, and publicly cacheable responses served to geographically distributed users. | Personalized, rapidly mutating, or sensitive per-user payloads that cannot be shared at the edge. | "Serving from edge points shrinks round-trip latency and shields origin servers, at the cost of coarse cache invalidation and propagation delay." | [CDN](./cdn/THEORY.md), [Read Scaling](./read-scaling/THEORY.md) |
| **In-process local cache** (local LRU cache) | Tiny, ultra-hot, rarely changing lookup tables (routing rules, feature flags) where even a network hop matters. | Large datasets or state that must stay strictly consistent across stateless app replicas. | "Keeping hot metadata in process eliminates network hops completely, but each instance holds its own copy so invalidation across the fleet is eventual." | [Caching](./caching/THEORY.md), [Cache Invalidation](./cache-invalidation-patterns/THEORY.md) |

**Cache failure modes worth naming:**
- **Penetration (missing keys):** guard with input validation, short-TTL negative caching, or a Bloom filter.
- **Breakdown (hot-key expiry):** coalesce misses with singleflight locking or background refresh.
- **Avalanche (mass expiry or outage):** add TTL jitter and keep fallback degradation ready — see [Cache Invalidation Patterns](./cache-invalidation-patterns/THEORY.md).

---

## 4. Search and Discovery

Add a dedicated search engine only when text relevance, tokenization, or faceted filtering outgrows your primary database.

| Category (Product Examples) | When It Fits | When It Doesn't | Interview Trade-off to Say Aloud | Concept Guide |
|---|---|---|---|---|
| **Inverted-index search engine** (Elasticsearch, OpenSearch) | Full-text search with relevance ranking (BM25), typo tolerance, synonyms, autocomplete, and faceted filtering at scale. | Primary source of truth, ACID transactions, frequent in-place row mutations, or simple exact-ID CRUD. | "An inverted index gives fast ranked text search and aggregations, but it is a derived, eventually consistent index that we sync asynchronously from the primary store." | [Search Systems](./search-systems/THEORY.md), [Elasticsearch](./elasticsearch/THEORY.md) |
| **Database-native search and indexes** (PostgreSQL B-tree / GIN full-text) | Moderate datasets needing exact filters, prefix search, or basic text matching without operating a second cluster. | Complex linguistic analysis, custom relevance tuning, or log/catalog search across huge document corpora. | "Keeping search inside the primary database avoids sync lag and dual-cluster ops, accepting weaker relevance scoring and shared resource contention with OLTP." | [Relational](./relational-databases/THEORY.md), [PostgreSQL](./postgresql/THEORY.md) |

**Sync and consistency guardrails:**
- Treat the search cluster as a **derived read view** fed asynchronously via change data capture (CDC) or an event log.
- State the freshness lag aloud: newly written records appear in search after indexing and refresh, never synchronously inside the OLTP transaction.

---

## 5. Stream Processing

Choose stream processing when low-latency stateful aggregation over continuous events matters; otherwise keep the pipeline stateless or batch-oriented.

| Category (Product Examples) | When It Fits | When It Doesn't | Interview Trade-off to Say Aloud | Concept Guide |
|---|---|---|---|---|
| **Stateful stream processor** (Flink, Kafka Streams) | Windowed aggregations, stream-to-stream joins, anomaly or fraud detection, and out-of-order event-time handling with watermarks. | Simple single-event transforms, stateless enrichment, or daily reports where hourly lag is fine. | "Checkpointed state and event-time watermarks give accurate low-latency aggregations over late data, at the cost of stateful cluster operations and backpressure tuning." | [Stream Processing](./stream-processing/THEORY.md), [Flink](./flink/THEORY.md) |
| **Stateless event consumers** (worker pool on Kafka or queue) | Independent per-event work such as notifications, indexing updates, webhook dispatch, or simple fan-out. | Cross-event windows, sessionization, or aggregations that must survive worker crashes without losing partial state. | "Stateless workers scale and redeploy effortlessly, because any state lives externally in a database or cache rather than inside the stream topology." | [Kafka](./kafka/THEORY.md), [Message Queues](./message-queues/THEORY.md) |
| **Batch / micro-batch pipeline** (Spark, scheduled SQL jobs) | Backfills, billing reconciliation, offline ML features, and historical analytics where minutes or hours of delay are acceptable. | Real-time alerting, live rate/abuse detection, or dashboards requiring continuous sub-minute updates. | "Batch processing simplifies correctness and reprocessing over bounded datasets, trading away freshness for higher throughput efficiency and simpler recovery." | [Stream Processing](./stream-processing/THEORY.md) |

**Semantics to clarify aloud:**
- Distinguish **event time** (when the action happened) from **processing time** (when the worker saw it) and explain how [Watermarks and Event Time](./stream-processing/watermarks-and-event-time.md) bound late arrivals.
- Clarify that [Exactly-Once Semantics](./stream-processing/exactly-once-semantics.md) inside the stream engine still require idempotent or transactional sinks downstream.

---

## 6. Distributed Coordination and Consensus

Coordination services protect small, critical cluster invariants. Keep them off the high-volume application data path.

| Category (Product Examples) | When It Fits | When It Doesn't | Interview Trade-off to Say Aloud | Concept Guide |
|---|---|---|---|---|
| **Consensus-backed coordinator** (ZooKeeper, etcd, Consul) | Leader election, service membership, shard/partition ownership metadata, and strongly consistent cluster configuration. | High-write application data, large payloads, or user-facing request paths. | "Quorum consensus gives linearizable metadata and safe leader election across partitions, but every write pays consensus overhead so we only store tiny coordination state." | [Distributed Coordination](./distributed-coordination/THEORY.md), [ZooKeeper](./zookeeper/THEORY.md), [Raft](./distributed-consensus-raft/THEORY.md) |
| **Database locks and conditional writes** (PostgreSQL row/advisory locks, DynamoDB conditional puts) | Correctness-critical business invariants (preventing double-booking, idempotent ledger writes, optimistic concurrency). | Cluster-wide service discovery or ephemeral node liveness watches with session heartbeats. | "Enforcing exclusivity right inside the system of record avoids adding a separate lock service and keeps the lock tied to the transaction boundary." | [Contention Control](./contention-control/THEORY.md), [Isolation Levels](./database-isolation-levels/THEORY.md) |
| **In-memory lease lock** (Redis `SET NX PX`) | Best-effort deduplication or efficiency locks (preventing duplicate background work) where occasional overlap is survivable. | Strict mutual exclusion for money or inventory without downstream fencing checks. | "In-memory TTL leases are fast for avoiding duplicate work, but failover or GC pauses can break exclusivity unless the downstream store validates a fencing token." | [Redis](./redis/THEORY.md), [Contention Control](./contention-control/THEORY.md) |

**Safety guardrails to mention:**
- Separate **efficiency locks** (avoiding duplicate work) from **correctness locks** (protecting money or inventory); correctness locks need monotonically increasing fencing tokens checked by the storage layer.
- For routing to healthy service instances, pair a registry with health checks and client/gateway discovery — see [Service Discovery](./service-discovery/THEORY.md).

---

## Common Over-Engineering Traps to Avoid

- **Naming Kafka when a simple queue suffices:** if only one worker pool consumes tasks and replay is unnecessary, a point-to-point queue is simpler.
- **Using Elasticsearch as the primary database:** keep a durable primary store as the source of truth and rebuild or sync the search index asynchronously.
- **Defaulting to NoSQL before knowing the query shape:** a relational database handles most early workloads well; switch to NoSQL when a concrete write-scale, schema, or partitioning bottleneck justifies losing joins and ACID guarantees.
- **Treating Redis as durable primary storage:** use it for caching, ephemeral coordination, or specialized data structures, and back critical state with a durable store.
- **Skipping fencing tokens on distributed locks:** a lock that expires during a pause only guarantees safety if the storage layer rejects stale tokens.
- **Adding a stream processor for stateless work:** if each event can be handled independently without windows or cross-event joins, a plain consumer group is far easier to operate.

## Related Guides

- [HLD Concept Catalog](./README.md) — full index of distributed systems building blocks
- [Pattern Selection](./pattern-selection/THEORY.md) — map system bottlenecks to architectural patterns
- [CAP Theorem](./cap-theorem/THEORY.md) and [PACELC Theorem](./pacelc-theorem/THEORY.md) — consistency, availability, and latency trade-offs
- [Distributed Transactions](./distributed-transactions/THEORY.md) — choosing sagas, outbox, or two-phase boundaries across services
- [Trade-offs Matrix](../resources/cheatsheets/trade-offs-matrix.md) — concise interview phrasing for core trade-offs
