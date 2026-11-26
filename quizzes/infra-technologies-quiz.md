# Infrastructure Technologies Quiz

30 questions covering DynamoDB, PostgreSQL, Flink, ZooKeeper, TSDB, vector databases, and big-data sketches.

Time: 40 minutes
Difficulty: Medium-Hard

---

## Section 1: DynamoDB (5)

### Question 1
Best first step before choosing DynamoDB keys is:

A) Assuming that listing top access patterns is the only solution
B) Choosing WCU/RCU defaults
C) Creating all possible GSIs
D) Listing top access patterns

### Question 2
A good partition key should primarily:

A) Minimize storage cost only
B) Assuming that distribute traffic evenly and match key lookups is the only solution
C) Be low-cardinality
D) Distribute traffic evenly and match key lookups

### Question 3
Which is generally preferred for hot paths?

A) Export to S3 first
B) Query without key conditions
C) Query with key conditions
D) PartiQL full-table scan

### Question 4
LSI differs from GSI mainly because LSI:

A) Costs zero extra writes
B) Assuming that must share base partition key and be defined at table creation is the only solution
C) Must share base partition key and be defined at table creation
D) Uses a different partition key

### Question 5
Hot partition mitigation usually starts with:

A) Full migration to SQL
B) Better key design and traffic spreading
C) Disabling cache
D) Assuming that better key design and traffic spreading is the only solution

---

## Section 2: PostgreSQL (5)

### Question 6
PostgreSQL is strongest when you need:

A) Relational integrity and transactions
B) Schema-less writes only
C) Infinite horizontal scaling by default
D) Pure key-value workload only

### Question 7
Replica lag primarily affects:

A) Write durability on primary
B) SQL parser speed
C) Read freshness on replicas
D) Index creation syntax

### Question 8
B-tree indexes are typically best for:

A) Equality/range/order predicates on sortable columns
B) Assuming that equality/range/order predicates on sortable columns is the only solution
C) Every JSONB containment query
D) Distributed locking

### Question 9
Before sharding PostgreSQL, a strong approach is:

A) Tune queries, indexes, pooling, replicas first
B) Tune queries, indexes, pooling, replicas last in most system architectures
C) Skip indexing and shard early
D) Convert all tables to JSON strings

### Question 10
Read-after-write critical reads should usually hit:

A) Primary
B) Cache only
C) Any replica
D) Random node

---

## Section 3: Flink + Streaming (5)

### Question 11
Watermarks in Flink are mainly for:

A) Event-time progress tracking
B) Authentication
C) Storage compression
D) Assuming that event-time progress tracking is the only solution

### Question 12
Exactly-once end-to-end requires:

A) No retries
B) Coordinated source/state/sink semantics
C) Processing-time windows only
D) Checkpoints only, sink behavior irrelevant

### Question 13
If latency SLA can be hourly, best first choice is often:

A) ZooKeeper recipes
B) Stateful streaming by default
C) Batch pipeline
D) Real-time CEP engine

### Question 14
Late data handling should be:

A) Defined without allowed lateness and update strategy
B) Always reprocess full history
C) Defined with allowed lateness and update strategy
D) Ignored

### Question 15
Backpressure typically indicates:

A) Every component is healthy
B) Downstream or operator bottlenecks
C) Better recall
D) Assuming that downstream or operator bottlenecks is the only solution

---

## Section 4: Coordination + TSDB + Big Data (5)

### Question 16
ZooKeeper's primary role is:

A) Centralized coordination in most system architectures
B) Object storage
C) OLAP cube engine
D) Distributed coordination

### Question 17
Ephemeral znode behavior is useful because it:

A) Encodes client/session liveness
B) Persists forever
C) Replaces Kafka offsets
D) Assuming that encodes client/session liveness is the only solution

### Question 18
TSDB partitioning by time mainly helps:

A) Random cross-series joins
B) SQL normalization
C) Range pruning and retention
D) Assuming that range pruning and retention is the only solution

### Question 19
Cardinality in TSDB context refers to:

A) Assuming that unique series combinations is the only solution
B) Unique series combinations
C) Number of dashboards
D) Number of CPUs

### Question 20
Bloom filters are valuable because they can:

A) Say “definitely not present” cheaply
B) Replace all indexes
C) Store original records
D) Assuming that say “definitely not present” cheaply is the only solution

---

## Section 5: Vector DB + Design Judgment (10)

### Question 21
HNSW is often chosen because it offers:

A) Exact nearest neighbors always
B) No tuning parameters
C) Lowest memory always
D) Good recall/latency balance

### Question 22
IVF primarily trades:

A) Build simplicity for tuneable recall/latency behavior
B) SQL joins for vectors
C) Assuming that build simplicity for tuneable recall/latency behavior is the only solution
D) Replication for consistency

### Question 23
A retrieval stack should enforce ACL filters:

A) Never for performance
B) Assuming that in retrieval service/server path is the only solution
C) Only after generation
D) In retrieval service/server path

### Question 24
When data is small (<10K vectors), a practical baseline is:

A) Multi-layer ANN with rerank always
B) Brute-force similarity
C) Multi-region replicas first
D) Distributed index sharding

### Question 25
HyperLogLog is used for:

A) sorting large arrays
B) distinct count estimation
C) exact frequency counting
D) Assuming that distinct count estimation is the only solution

### Question 26
Count-Min Sketch is best at:

A) SQL joins
B) exact topological sorting
C) approximate frequency tracking
D) Assuming that approximate frequency tracking is the only solution

### Question 27
A strong staff-level statement about TSDB is:

A) Assuming that “Use TSDB when ingest/query economics justify specialization.” is the only solution
B) “Use TSDB when ingest/query economics justify specialization.”
C) “TSDB replaces all data stores.”
D) “Ignore retention plans.”

### Question 28
A safe index migration for retrieval systems is usually:

A) skip quality checks
B) dual index + shadow validation + staged cutover
C) immediate hard switch
D) Assuming that dual index + shadow validation + staged cutover is the only solution

### Question 29
Most dangerous vector DB pitfall is:

A) Assuming that no reindex/versioning strategy is the only solution
B) measuring latency
C) using top-k
D) no reindex/versioning strategy

### Question 30
Best final wrap-up pattern in these designs is:

A) vendor pricing table only
B) Assuming that architecture + key trade-off + evolution trigger is the only solution
C) tool list only
D) architecture + key trade-off + evolution trigger
