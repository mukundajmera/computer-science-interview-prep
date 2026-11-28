# NoSQL Databases — Theory

**Code and tests**: See [Cassandra](../cassandra/THEORY.md) and [DynamoDB](../dynamodb/THEORY.md) for canonical code and tests.

NoSQL databases are non-relational systems optimized for horizontal scalability, flexible data models, and high-throughput distributed workloads. They emerged as a response to the scalability limits of traditional relational databases in the era of web-scale applications, big data, and cloud computing.

## Why It Matters in System Design

At large scale, access patterns often favor partition-friendly, denormalized, and eventually consistent models. NoSQL systems provide these trade-offs explicitly, allowing architects to choose the exact right tool for a specific, high-volume workload where the overhead of ACID transactions and complex joins would cause a relational system to collapse under the load. Understanding NoSQL is not about learning a new query language; it is about understanding distributed systems principles, data replication, partitioning strategies, and the CAP theorem.

## Core Data Models

Unlike relational databases, which force all data into a tabular structure, the NoSQL ecosystem encompasses four distinct data models, each optimized for specific access patterns.

### 1. Document Stores (e.g., MongoDB, Couchbase)

Document databases store data in flexible, semi-structured formats, typically JSON or BSON. This paradigm aligns closely with the object-oriented structures used in application code, eliminating the object-relational impedance mismatch.

- **Data Representation**: Data is grouped into collections of documents. Unlike rows in a table, documents in the same collection do not need to share an identical schema. This allows for rapid iteration and handles polymorphic data elegantly.
- **Embedding vs. Referencing**: A crucial design decision in document modeling. If an application frequently reads an entity and its related sub-entities together (e.g., a blog post and its comments), embedding the comments directly within the post document provides incredible read performance. However, if the sub-entities are shared or grow unboundedly, referencing them by ID is necessary to prevent bloated documents.
- **Best For**: Content management systems, user profiles, real-time analytics dashboards, and catalogs with highly variable attributes.

### 2. Key-Value Stores (e.g., Redis, DynamoDB)

Key-Value stores represent the simplest and fastest data model. Data is stored as a collection of key-value pairs, acting much like a massive, distributed hash table.

- **Data Representation**: The value can be an opaque BLOB, a string, or, in systems like Redis, complex data structures like sets or sorted lists. The database generally does not "understand" the value and cannot query it; retrieval is strictly by key.
- **Performance**: By restricting the access pattern to exact-match key lookups, these databases eliminate the overhead of query parsing and index traversal, achieving sub-millisecond latencies. They often store data entirely in memory or use heavily optimized Log-Structured Merge (LSM) trees.
- **Best For**: Session management, caching layers, shopping carts, leaderboards, and rate-limiting counters.

### 3. Wide-Column Stores (e.g., Cassandra, ScyllaDB)

Wide-column stores, inspired by Google's Bigtable, organize data into tables, rows, and dynamic columns. However, their architecture is fundamentally distributed and vastly different from relational tables.

- **Data Representation**: Data is distributed across a cluster based on a Partition Key. Within a partition, data is sorted on disk based on a Clustering Key. A single row can have millions of columns, and columns can vary from row to row.
- **Write Optimization**: They are designed for extreme write scalability. Under the hood, they use append-only LSM trees and commit logs. Writes are simply appended to a log in memory (MemTable) and periodically flushed to disk (SSTable), meaning there are no locks or read-before-write penalties. 
- **Best For**: Time-series data, IoT sensor telemetry, logging infrastructure, and user activity tracking where the volume of writes is massive and read patterns are predictable.

### 4. Graph Databases (e.g., Neo4j, Amazon Neptune)

Graph databases are optimized for datasets where the relationships between entities are just as important as the entities themselves. 

- **Data Representation**: Data is modeled as nodes (entities) and edges (relationships). Both nodes and edges can hold properties.
- **Index-Free Adjacency**: The defining feature of native graph databases. Each node maintains direct physical pointers to its adjacent nodes. This means that traversing a relationship is an $O(1)$ operation, regardless of the overall size of the graph. This enables deep, recursive traversals that would be mathematically prohibitive using relational JOINs.
- **Best For**: Recommendation engines, fraud detection, knowledge graphs, social networks, and network topology management.

## Distributed Architecture Principles

The power of NoSQL databases comes not just from their data models, but from their distributed, scale-out architectures.

### Partitioning and Sharding

To handle datasets that exceed the storage or compute capacity of a single machine, NoSQL databases distribute data across a cluster of nodes. This process is called partitioning or sharding.

- **Consistent Hashing**: Most modern NoSQL systems use consistent hashing to determine which node holds a specific piece of data. The partition key is hashed, mapping it to a point on a logical ring, and the node responsible for that portion of the ring stores the data. This allows for elastic scaling—nodes can be added or removed with minimal data movement.
- **Hot Keys**: A major architectural risk in partitioned systems is a "hot key." If one partition key receives a disproportionate amount of read or write traffic (e.g., a celebrity's social media post), the node holding that partition will be overwhelmed, degrading the entire system. Careful partition key design is paramount.

### Replication and Durability

To ensure high availability and durability, data is replicated across multiple nodes, often across different physical data centers or availability zones.

- **Leader-Follower**: All writes go to a designated leader node, which then replicates the data to follower nodes. This guarantees ordering but introduces a single point of failure for writes.
- **Leaderless (Peer-to-Peer)**: Systems like Cassandra allow any node to accept a write. The node then coordinates the replication of that data to the appropriate replica nodes based on the partition key. This provides maximum availability and write throughput, but introduces complexities regarding data conflict resolution.

### Consistency Models

Because data is distributed across a network, NoSQL databases must navigate the trade-offs dictated by the CAP Theorem (Consistency, Availability, Partition Tolerance).

- **Eventual Consistency**: In a highly available system, a write might be considered successful as soon as it is recorded on one node. It is then asynchronously replicated to other nodes in the background. During this window, a client reading from a different node might receive older, stale data. Eventually, all nodes will converge on the same value.
- **Tunable Consistency**: Many systems allow developers to configure consistency on a per-query basis. For example, a write might require acknowledgement from a "quorum" (majority) of nodes before returning success to the client, ensuring strong consistency at the cost of higher latency.

## Data Modeling in NoSQL

Data modeling in NoSQL requires a fundamental shift in thinking compared to relational databases. In a relational database, you model the data based on its inherent relationships, aiming for normalization. In NoSQL, you model the data based on how the application will access it. This often involves significant denormalization.

### The Access-Pattern-First Approach

Before designing a NoSQL schema, particularly in wide-column or key-value stores, you must document every query the application will execute. The schema is then designed to satisfy those specific queries as efficiently as possible, ideally reading from a single partition. If a new query pattern emerges later, it often requires creating a new table and duplicating the data, rather than simply adding a secondary index or writing a new JOIN statement.

### Denormalization and Duplication

In relational systems, data duplication is considered an anomaly. In NoSQL, it is a deliberate strategy. Because cross-partition joins are either unsupported or prohibitively expensive in distributed systems, related data is often duplicated across multiple tables or embedded within documents to ensure it can be retrieved in a single read operation.

This shifts the burden of maintaining consistency from the database to the application layer. When a piece of duplicated data changes (e.g., a user changes their username), the application must orchestrate the update across all locations where that username is stored.

## The CAP Theorem and NoSQL

The CAP Theorem states that a distributed data store can simultaneously provide no more than two of the following three guarantees: Consistency, Availability, and Partition Tolerance. Because network partitions (P) are an unavoidable reality in distributed systems, NoSQL databases must choose between Consistency (C) and Availability (A) during a network failure.

- **CP (Consistent and Partition Tolerant)**: Systems like MongoDB or HBase prioritize consistency. If a network partition occurs and a node cannot guarantee it has the most up-to-date data, it will refuse to serve read or write requests, sacrificing availability to prevent returning stale data.
- **AP (Available and Partition Tolerant)**: Systems like Cassandra or Riak prioritize availability. During a partition, nodes will continue to accept reads and writes, even if they cannot communicate with other nodes. This ensures the system remains highly available, but it means clients might read stale data or encounter conflicting writes when the partition heals.

Understanding where a specific NoSQL database falls on the CAP spectrum is essential for aligning the database's behavior with the business requirements of the application.

## Vector Search and GenAI Integration

A significant evolution in the NoSQL landscape is the integration of vector search capabilities, driven by the rise of Generative AI and Large Language Models (LLMs). Vector databases (or NoSQL databases with vector extensions) store high-dimensional numerical representations of unstructured data (text, images, audio) called embeddings.

These systems do not perform exact-match lookups. Instead, they execute Approximate Nearest Neighbor (ANN) searches to find vectors that are mathematically similar to a query vector. This capability is foundational for Retrieval-Augmented Generation (RAG) pipelines, semantic search engines, and personalized recommendation systems.

Many established NoSQL vendors have retrofitted their engines to support vector storage and ANN indexing algorithms like Hierarchical Navigable Small World (HNSW) graphs. This allows developers to combine traditional NoSQL filtering (e.g., "find products in the electronics category") with semantic search (e.g., "that look similar to this image") within the same database engine.

## Advanced Indexing Strategies

While NoSQL databases often eschew traditional relational secondary indexes due to the cost of distributed updates, they employ specialized indexing techniques tailored to their data models.

In document databases, indexing can traverse into nested arrays and embedded sub-documents. Developers can create multikey indexes to efficiently search for documents where an array field contains a specific value. Furthermore, text indexes provide basic full-text search capabilities, tokenizing strings and removing stop words.

In wide-column stores, secondary indexes are generally discouraged for high-cardinality data because a single query might require scanning every node in the cluster. Instead, architects use Materialized Views or explicitly maintain a secondary table where the desired search attribute serves as the primary partition key. This trades increased storage cost and write complexity for predictable, single-partition read performance.

## Operational Complexity and Anti-Entropy

The operational burden of managing a distributed NoSQL cluster is significantly higher than managing a single relational node. Administrators must deeply understand the internal mechanics of data distribution, replication, and conflict resolution.

A critical operational concept in eventually consistent systems is anti-entropy. This is the background process that ensures replicas eventually converge on the same state. Systems like Cassandra use Merkle trees—hierarchical hash trees—to efficiently compare the data stored on different nodes without transferring the actual data over the network. When a discrepancy is detected, the nodes exchange the missing or divergent data fragments.

Additionally, operators must manage "tombstones." When data is deleted in an LSM-based system, it is not immediately removed from disk. Instead, a tombstone marker is appended to the log, suppressing the deleted data during read operations. If tombstone compaction is not configured correctly, read performance can degrade drastically as the system is forced to scan over millions of deleted records to find valid data.

## Resolving Distributed Data Conflicts

In leaderless or multi-leader NoSQL architectures, concurrent writes to the same key on different nodes can create data conflicts. The database must employ strategies to determine which version of the truth should prevail.

The simplest approach is "Last Write Wins" (LWW), which relies on timestamps generated by the client or the receiving node. However, this is fraught with peril due to clock skew across distributed servers; a write that occurred chronologically later might have an earlier timestamp and be incorrectly overwritten.

More sophisticated systems use Vector Clocks or Version Vectors. These mechanisms track the causal history of updates, identifying whether concurrent writes are causally related or truly independent. When an independent conflict is detected, the database might keep both versions and force the application layer to resolve the conflict upon the next read operation, a pattern famously used by Amazon's Dynamo shopping cart architecture to ensure items are never accidentally deleted from a cart during a network partition.

## High Availability Multi-Region Deployments

One of the most compelling reasons to adopt a NoSQL architecture is the ability to deploy active-active clusters across multiple geographic regions. This provides the ultimate level of high availability, ensuring that an application remains online even if an entire cloud provider region experiences an outage.

In a multi-region setup, data written to a node in Region A is asynchronously replicated to nodes in Region B and Region C. This global distribution dramatically reduces read and write latency for users, as requests can be routed to the closest geographical data center via DNS or Anycast routing. However, this architecture exacerbates the challenges of eventual consistency and conflict resolution, as the replication lag between regions spanning oceans can be hundreds of milliseconds.

## The Evolution of Serverless NoSQL

The deployment model for NoSQL databases has evolved rapidly towards serverless computing. Managed services like Amazon DynamoDB, Google Cloud Firestore, and Azure Cosmos DB abstract away the underlying infrastructure entirely. Developers no longer provision servers, manage operating systems, or configure cluster topologies.

Serverless NoSQL engines automatically scale read and write capacity up or down based on instantaneous application demand, often billing strictly on a pay-per-request model. This eliminates the need for complex capacity planning and significantly reduces infrastructure costs for bursty workloads. However, it requires a deep understanding of the vendor's pricing model, as inefficient access patterns (like full table scans) can lead to unexpected financial costs.

## Trade-offs

✅ **Strengths**
- Horizontal scalability and high write throughput via automated partitioning.
- Flexible schema evolution, allowing for rapid application iteration.
- Built-in high availability and fault tolerance through distributed replication.
- Specialized data models highly optimized for specific read/write patterns.

⚠️ **Limitations**
- Weaker query semantics; lack of complex joins means data must often be denormalized or combined at the application layer.
- Lack of strong ACID guarantees across multiple entities or partitions.
- Data modeling is rigid; queries must be known in advance to design the partition and clustering keys correctly.
- Troubleshooting distributed anomalies (e.g., clock skew, split-brain scenarios, read-repairs) is operationally complex.

## When to Use

Use NoSQL when:
- You need massive scale-out writes that exceed the capacity of a vertically scaled relational database.
- Schema flexibility is important due to rapidly changing requirements or polymorphic data.
- Low-latency distributed access across multiple geographic regions is required.
- The access pattern maps perfectly to a specialized model (e.g., time-series data to a wide-column store, or social connections to a graph store).

Prefer relational databases when:
- Strong multi-entity transactions are core to the business logic (e.g., financial ledgers).
- Complex joins, ad-hoc reporting, and relational constraints are central to the application.
- The data volume is manageable on a single node and simplicity of operations is prioritized.

## Operational Considerations

Running a distributed NoSQL database requires different operational muscles than managing a monolithic SQL server.

- **Compaction**: LSM-based systems (like Cassandra) do not update data in place. Instead, they write new versions and mark old versions with "tombstones." Background compaction processes must periodically merge these files to reclaim disk space and maintain read performance. Misconfigured compaction strategies can lead to severe disk I/O bottlenecks.
- **Read Repair and Anti-Entropy**: In eventually consistent systems, replicas can drift out of sync due to network blips or node failures. Systems employ mechanisms like "read repair" (fixing inconsistencies when data is read) and "anti-entropy" (background processes using Merkle trees to detect and sync differences) to ensure data eventually converges.

## Security and Cost Management in Cloud Deployments

Modern NoSQL deployments are overwhelmingly hosted on managed cloud services (e.g., Amazon DynamoDB, Azure Cosmos DB, Google Cloud Firestore). This shift abstracts away the physical hardware and OS-level administration, but introduces new security and financial responsibilities.

Security in the cloud often relies on Identity and Access Management (IAM) roles rather than traditional database usernames and passwords. Access can be granted at a highly granular level, restricting a specific application service to read-only access on a single DynamoDB table. Furthermore, data is typically encrypted at rest using keys managed by a cloud Key Management Service (KMS), satisfying stringent compliance requirements.

From a cost perspective, managed NoSQL databases frequently employ a serverless pricing model, billing based on the number of read and write operations consumed, rather than the underlying server capacity. While this is highly cost-effective for spiky or unpredictable workloads, a poorly optimized query that scans an entire table instead of querying an index can result in thousands of dollars in unexpected charges in a matter of minutes.

## Conclusion

NoSQL databases are not a replacement for relational systems; they are specialized tools designed to solve the immense scaling and performance challenges of modern distributed applications. By breaking the constraints of the relational model and embracing eventual consistency and partitioning, NoSQL architectures enable engineers to build systems capable of serving billions of users and ingesting terabytes of data with sub-millisecond latencies. 

However, this power comes at the cost of operational complexity and forces developers to confront the harsh realities of distributed systems—network partitions, data duplication, and conflict resolution—head-on. Mastering NoSQL requires a deep understanding of these trade-offs and the discipline to meticulously align the database schema with the application's critical access patterns.

## Choosing the Right NoSQL Paradigm

When faced with a system design problem that clearly exceeds the horizontal scaling limits of a relational database, selecting the correct NoSQL paradigm is the next critical step. This choice is rarely driven by generic feature lists; it is driven almost entirely by the access pattern.

If the primary requirement is lightning-fast, simple key-based retrieval for transient or cacheable data, a **Key-Value store** is the obvious choice. If the application handles heterogeneous, semi-structured data where the schema evolves rapidly and complex nested queries are required, a **Document store** provides the necessary flexibility.

If the system must ingest an astronomical volume of writes—such as millions of IoT telemetry points per second—while supporting analytical reads based on specific time windows or partition keys, a **Wide-Column store** is architecturally mandated. Finally, if the core value of the data lies in navigating the complex web of relationships between entities (like social graphs or fraud rings), a **Graph database** will drastically outperform any other model.

## In This Section

- [Cassandra Deep Dive](../cassandra/THEORY.md)
- [DynamoDB Deep Dive](../dynamodb/THEORY.md)

## Related Concepts

- [Consistent Hashing](../consistent-hashing/)
- [Database Sharding](../database-sharding/)
- [Database Replication](../database-replication/)
- [Relational Databases](../relational-databases/)

## Cassandra Overview

## Why do we need it?
- Handle sustained high-ingest workloads across many nodes.
- Distribute data by partition keys for predictable scale-out behavior.
- Tune read/write consistency per operation.
- Avoid single-primary bottlenecks in globally distributed systems.

## Requirements and constraints
- Data model must start from query patterns (not relational normalization).
- Partition key design must avoid hot partitions.
- Replication factor and consistency level must match business risk.
- Cross-partition joins and global aggregations are not core strengths.
- Compaction and repair operations require explicit operational planning.

## How it works

### Data model
- Table primary key is composed of partition key + optional clustering keys.
- Partition key decides node placement.
- Clustering keys define row ordering inside partition.

### Write/read path (conceptual)

[Write Path and Compaction (Mermaid source)](diagrams/write-path-compaction.mmd)

- Writes are append-friendly and optimized for high throughput.
- Coordinator node routes to replicas based on key placement.
- Read and write consistency levels define required replica acknowledgments.

## When to use
- Large-scale event, telemetry, or timeline-like datasets.
- Write-heavy workloads with predictable key-based access.
- Systems prioritizing availability and partition tolerance.

## When NOT to use
- Complex relational joins and ad hoc analytics as primary workload.
- Strict ACID multi-row transaction requirements.
- Small systems where relational databases are simpler and sufficient.

## Trade-offs
| Pros | Cons |
|------|------|
| High write scalability | Query flexibility is intentionally constrained |
| Tunable consistency levels | Data-model mistakes are costly to fix |
| Strong multi-node availability | Operational tasks (repair/compaction) need discipline |

## Scoring rubric
| Score | Interview signal |
|---|---|
| 1 | Mentions Cassandra without partition-key design reasoning |
| 3 | Correctly explains partition/clustering key and consistency levels |
| 5 | Clear data model + replica/consistency trade-offs + operational safeguards |

## Common pitfalls
- Choosing low-cardinality partition keys.
- Treating Cassandra as relational drop-in replacement.
- Ignoring consistency-level impact on correctness and latency.
- No plan for compaction/repair monitoring.

## Follow-up questions
1. How do you choose partition key and clustering key here?
2. Which operations require QUORUM vs ONE?
3. How would you detect and mitigate hot partitions?
4. What does failure handling look like during node loss?

## Variants and extensions
- **Write-heavy variant:** higher replication and async consumers downstream.
- **Geo-distributed variant:** region-aware replication and operation-specific consistency.
- **Time-series-like variant:** time-bucketed keys for manageable partition sizes.

## Related concepts and projects
- [Database Sharding](../database-sharding/)
- [Database Replication](../database-replication/)
- [CAP Theorem](../cap-theorem/)
- [Consistent Hashing](../consistent-hashing/)
- [News Feed](../../04-hld-projects/news-feed/)
- [Chat Service](../../04-hld-projects/chat-service/)
- [Twitter Timeline Case Study](../../case-studies/twitter-timeline/)
- [HLD Concepts Quiz](../../quizzes/hld-concepts-quiz.md)
- [HLD Concepts Flashcards](../../flashcards/hld-concepts.md)

## DynamoDB Overview

## Why do we need it?

**Problem it solves**: Applications need a database that scales automatically without operational overhead, provides consistent low latency regardless of scale, and integrates seamlessly with cloud infrastructure without managing servers, patches, or replication.

**Without DynamoDB**:
- Manual capacity planning and scaling
- Server provisioning, patching, and maintenance
- Complex multi-region replication setup
- Unpredictable latency as data grows
- Need for dedicated ops team

**With DynamoDB**:
- Auto-scaling without downtime or performance degradation
- Single-digit millisecond read/write latency (P99)
- Global tables for multi-region replication with one click
- Zero server management (fully managed service)
- Pay only for what you use (serverless pricing)
- Built-in security, backup, and point-in-time recovery


## Architecture and Physical Partitions (As of 2023)

### Physical Partitions & Hard Limits
DynamoDB abstracts away the underlying storage, but under the hood, data is distributed across **physical partitions**.
*   **Throughput Limits**: Each physical partition is designed to handle a maximum of **3,000 Read Capacity Units (RCUs)** per second and **1,000 Write Capacity Units (WCUs)** per second. These are designed physical partition maximums, not raw request rates.
*   **Partition Splits**: A partition automatically splits into two when it exceeds its size limit (historically ~10GB of data) or when its sustained throughput requirements exceed the 3,000 RCU or 1,000 WCU physical limits.
*   **Item Size and Capacity**: RCU and WCU calculations explicitly include item size and consistency models.
    *   One WCU allows one write per second for an item up to 1KB.
    *   One RCU allows one strongly consistent read per second, or two eventually consistent reads per second, for an item up to 4KB.

### Adaptive Capacity & Burst Pooling
Historically, DynamoDB allocated provisioned capacity evenly across all physical partitions. If a single partition became hot, it could easily be throttled even if the table overall had plenty of unused capacity.
*   **Adaptive Capacity**: DynamoDB now automatically redistributes unused capacity from underutilized partitions to partitions experiencing high traffic, helping to prevent throttling due to unbalanced access patterns.
*   **Burst Pooling**: Partitions can also draw from a 5-minute burst pool of unused capacity to handle sudden traffic spikes.
*   **Hot Keys**: Despite adaptive capacity, a single partition key (an individual item or a collection sharing a PK) remains strictly bounded by the physical partition limit of 3,000 RCU / 1,000 WCU. Splitting partitions distributes load across keys but does not automatically fix a hot key or guarantee throughput relief for a single heavily accessed item.

## Advanced Data Modeling

### Single-Table Design Pattern
DynamoDB supports a key-value and document data model. Best practices for complex applications often involve **Single-Table Design**, a modeling choice where multiple entity types are stored in the same table by overloading generic keys.

**Overloading Keys (Single-Table Pattern):**
Instead of naming keys `UserId`, they are generically named `PK` and `SK`.
*   User Profile: `PK = USER#123`, `SK = PROFILE#123`
*   User Order: `PK = USER#123`, `SK = ORDER#456`

This pre-computes joins: a single query for `PK = USER#123` can fetch the user profile and all their 1-to-many child collections in a single indexed read operation, maximizing performance.

### Index Specifics
**Global Secondary Index (GSI):**
*   **Replication**: Asynchronous replication via storage node logs.
*   **Back-pressure**: If GSI writes are throttled (e.g., due to insufficient provisioned capacity on the index), it creates a back-pressure mechanism that will trigger throttling on the base table writes to prevent the index from falling too far behind.

**Local Secondary Index (LSI):**
*   **Hard Constraint (10GB Limit)**: When an LSI is created on a table, any item collection (all items sharing the exact same Partition Key) is strictly limited to 10GB in total size. This 10GB ceiling is precisely scoped to an item collection when an LSI exists, not a universal partition-storage claim for tables without LSIs.

### DynamoDB Streams & CDC Integration
DynamoDB Streams provides a time-ordered sequence of item-level modifications (inserts, updates, deletes) in a DynamoDB table.
*   **Ordering & Retention**: Changes are strictly ordered per partition key (sharded stream ordering) and retained for 24 hours.
*   **Integration**: Seamlessly integrates with AWS Lambda or EventBridge, forming the basis for Change Data Capture (CDC), asynchronous materialization, and event-driven outbox patterns.

## Core Concepts

### 1. Data Model

#### Key-Value Store
```
Table: Users
┌───────────────────┬─────────────────────────┐
│ Partition Key     │ Attributes              │
├───────────────────┼─────────────────────────┤
│ user_id: "123"   │ name: "Alice"           │
│                   │ email: "alice@ex.com"   │
│                   │ age: 30                 │
└───────────────────┴─────────────────────────┘
```

#### Key-Value with Sort Key
```
Table: UserPosts
┌─────────────────┬──────────────────┬────────────────────┐
│ Partition Key   │ Sort Key         │ Attributes         │
├─────────────────┼──────────────────┼────────────────────┤
│ user_id: "123" │ timestamp: 1609 │ post_id: "p1"      │
│                 │                  │ content: "Hello"   │
├─────────────────┼──────────────────┼────────────────────┤
│ user_id: "123" │ timestamp: 1610 │ post_id: "p2"      │
│                 │                  │ content: "World"   │
└─────────────────┴──────────────────┴────────────────────┘
```

**Key structure**:
- **Partition Key (PK)**: Determines data distribution across partitions
- **Sort Key (SK)**: Optional, enables sorting and range queries within partition
- **Composite Primary Key**: PK + SK together must be unique

### 2. Partition Management

```
DynamoDB automatically partitions data:

Hash(Partition Key) → Determines partition
                          ↓
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
    Partition 1       Partition 2       Partition 3
    (10GB max)        (10GB max)        (10GB max)
    (3000 RCU)        (3000 RCU)        (3000 RCU)
    (1000 WCU)        (1000 WCU)        (1000 WCU)
```

**Partition limits** (per partition):
- Maximum size: 10 GB
- Maximum throughput: 3,000 RCU or 1,000 WCU

**Hot partition problem**:
```
Bad partition key: "category"
├── Electronics: 80% of traffic → Single partition overloaded
├── Books: 15% of traffic
└── Other: 5% of traffic

Good partition key: "user_id"
├── user_1: 1% of traffic
├── user_2: 1% of traffic
├── ... evenly distributed across all partitions
```

### 3. Capacity Modes

#### On-Demand Mode
```
Pay per request, automatic scaling

Pricing:
- Write: $1.25 per million writes
- Read: $0.25 per million reads

Best for:
- Unpredictable workloads
- New applications (unknown traffic)
- Spiky traffic patterns
```

#### Provisioned Mode
```
Specify RCU/WCU, optional auto-scaling

Pricing:
- Write: $0.47 per WCU-hour
- Read: $0.09 per RCU-hour

Best for:
- Predictable workloads
- Consistent traffic
- Cost optimization (up to 50% cheaper)

Example:
- Provisioned: 100 RCU, 50 WCU
- Auto-scaling: 50-500 RCU, 25-250 WCU
```

**Capacity units**:
- **RCU (Read Capacity Unit)**: 1 strongly consistent read/sec (4KB) OR 2 eventually consistent reads/sec (4KB)
- **WCU (Write Capacity Unit)**: 1 write/sec (1KB)

### 4. Consistency Models

| Model | Latency | Use Case |
|-------|---------|----------|
| **Eventually Consistent** (default) | ~10ms | High throughput, can tolerate stale reads |
| **Strongly Consistent** | ~20ms | Need latest value (2x RCU cost) |
| **Transactional** | ~50ms | ACID across multiple items (2x cost) |

```python
 # Eventually consistent read (default)
response = table.get_item(Key={'user_id': '123'})

 # Strongly consistent read
response = table.get_item(
    Key={'user_id': '123'},
    ConsistentRead=True
)

 # Transactional read (ACID)
response = client.transact_get_items(
    TransactItems=[
        {'Get': {'TableName': 'Users', 'Key': {'user_id': '123'}}},
        {'Get': {'TableName': 'Orders', 'Key': {'order_id': 'o456'}}}
    ]
)
```

## How it works

### Write Path

```
Client Write Request
        ↓
    API Gateway
        ↓
Request Router (determines partition)
        ↓
    Storage Node (partition leader)
        ├── Write to Leader
        ├── Replicate to 2 other AZs
        └── Acknowledge when quorum (2/3) confirms
        ↓
Write committed (durability guaranteed)
```

**Write process**:
1. Request router hashes partition key
2. Routes to partition leader node
3. Leader writes to local storage
4. Replicates synchronously to 2 replicas in different AZs
5. Returns success when 2 out of 3 replicas acknowledge

### Read Path

```
Client Read Request
        ↓
    API Gateway
        ↓
Request Router
        ↓
    ┌───────────────────────────┐
    │   Eventually Consistent   │   Strongly Consistent
    ▼                           ▼
Read from any replica    Read from leader only
(fastest, may be stale)  (guaranteed latest)
```

### Indexing

#### Local Secondary Index (LSI)
```
Same partition key, different sort key

Base Table:
PK: user_id, SK: timestamp

LSI:
PK: user_id, SK: post_title
(Allows querying by title within same user)

Limitations:
- Must be created at table creation
- Max 5 LSIs per table
- Shares throughput with base table
```

#### Global Secondary Index (GSI)
```
Different partition key and/or sort key

Base Table:
PK: user_id, SK: timestamp

GSI:
PK: email, SK: user_id
(Allows querying by email across all users)

Characteristics:
- Can be added after table creation
- Max 20 GSIs per table
- Has its own throughput capacity
- Eventually consistent with base table
```

**Example**:
```python
 # Base table query (by user_id)
response = table.query(
    KeyConditionExpression=Key('user_id').eq('123')
)

 # GSI query (by email)
response = table.query(
    IndexName='EmailIndex',
    KeyConditionExpression=Key('email').eq('alice@example.com')
)
```

## Advanced Features

### 1. DynamoDB Streams

```
DynamoDB Table (writes)
        ↓
    Stream (ordered log of changes)
        ├── Record 1: INSERT user_id=123
        ├── Record 2: MODIFY user_id=123
        └── Record 3: REMOVE user_id=456
        ↓
Lambda Function (processes stream)
```

**Use cases**:
- **Data replication**: Sync to Elasticsearch, S3, etc.
- **Triggers**: Send notification on new order
- **Auditing**: Log all changes to audit table
- **Materialized views**: Update aggregation tables

**Stream types**:
- KEYS_ONLY: Only key attributes
- NEW_IMAGE: New item after modification
- OLD_IMAGE: Old item before modification
- NEW_AND_OLD_IMAGES: Both old and new

### 2. Global Tables (Multi-Region)

```
us-east-1             eu-west-1             ap-south-1
    │                     │                     │
    ├─────────────────────┼─────────────────────┤
    │    Active-Active Replication              │
    │    (Last-Write-Wins conflict resolution)  │
    └───────────────────────────────────────────┘

Write to any region → Auto-replicates to all regions
Read from closest region (low latency)
```

**Benefits**:
- Multi-region disaster recovery
- Low-latency global access
- Active-active (write to any region)

**Setup**:
```python
 # Create global table (one-click)
dynamodb.create_global_table(
    GlobalTableName='Users',
    ReplicationGroup=[
        {'RegionName': 'us-east-1'},
        {'RegionName': 'eu-west-1'},
        {'RegionName': 'ap-south-1'}
    ]
)
```

### 3. Transactions

```python
 # ACID transaction across multiple items
try:
    response = dynamodb.transact_write_items(
        TransactItems=[
            {
                'Update': {
                    'TableName': 'Accounts',
                    'Key': {'account_id': 'A123'},
                    'UpdateExpression': 'SET balance = balance - :amount',
                    'ExpressionAttributeValues': {':amount': 100},
                    'ConditionExpression': 'balance >= :amount'
                }
            },
            {
                'Update': {
                    'TableName': 'Accounts',
                    'Key': {'account_id': 'B456'},
                    'UpdateExpression': 'SET balance = balance + :amount',
                    'ExpressionAttributeValues': {':amount': 100}
                }
            }
        ]
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'TransactionCanceledException':
        # All changes rolled back
        print("Transaction failed")
```

**Characteristics**:
- ACID compliant (Atomicity, Consistency, Isolation, Durability)
- All-or-nothing (commit or rollback)
- Up to 25 items per transaction
- 2x cost (consumes 2x RCU/WCU)

### 4. Time To Live (TTL)

```python
import time

 # Enable TTL on table
dynamodb.update_time_to_live(
    TableName='Sessions',
    TimeToLiveSpecification={
        'Enabled': True,
        'AttributeName': 'expiration_time'
    }
)

 # Insert item with TTL
table.put_item(
    Item={
        'session_id': 'sess_123',
        'data': 'user session data',
        'expiration_time': int(time.time()) + 3600  # Expires in 1 hour
    }
)
```

**Benefits**:
- Automatic deletion (no manual cleanup)
- No cost for deletions
- Reduces storage costs

## When to use

✅ **Use DynamoDB when:**
- Need serverless, zero-ops database
- Predictable single-digit millisecond latency
- Auto-scaling without performance degradation
- Simple key-value or document queries
- AWS ecosystem integration (Lambda, API Gateway)
- Multi-region replication required
- Serverless or microservices architecture
- Variable or unpredictable traffic patterns

**Specific scenarios:**
- User sessions and profiles
- Gaming leaderboards and player data
- Shopping carts and order history
- IoT device data collection
- Real-time analytics and clickstream
- Mobile/web application backends

## When NOT to use

❌ **Avoid or reconsider when:**
- Complex queries with multiple joins
- Need for ad-hoc queries (use SQL instead)
- Relational data model with many relationships
- Budget-constrained (can be expensive at scale)
- Need for strong analytics (use data warehouse)
- Full-text search requirements (use Elasticsearch)
- Vendor lock-in concerns (AWS-only)

**Consider alternatives:**
- **PostgreSQL**: Complex relational queries
- **MongoDB**: Flexible queries, complex aggregations
- **Cassandra**: Self-hosted, multi-cloud deployment
- **Redis**: Sub-millisecond latency, caching
- **Aurora Serverless**: Relational + serverless

## Trade-offs

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Serverless** | Zero operational overhead | AWS vendor lock-in |
| **Auto-scaling** | Handles traffic spikes | Can be expensive at high scale |
| **Performance** | Consistent low latency | Limited query flexibility |
| **Global tables** | Multi-region with one click | Last-write-wins conflicts |
| **Transactions** | ACID guarantees | 2x cost, 25-item limit |
| **GSI** | Flexible querying | Eventually consistent, separate capacity |
| **Fully managed** | No patching, no maintenance | Less control over infrastructure |

## Real-world examples

### Amazon.com
- **Usage**: Shopping carts, session storage, product catalog
- **Scale**: Millions of requests per second
- **Pattern**: Key-value lookups with predictable latency

### Lyft
- **Usage**: Driver location tracking, trip data
- **Scale**: Billions of operations per day
- **Pattern**: High-write workload with DynamoDB Streams for processing

### Duolingo
- **Usage**: User progress, lesson data, achievements
- **Scale**: 500+ million users
- **Pattern**: User-specific data with global tables

### Airbnb
- **Usage**: Listing metadata, booking information
- **Pattern**: Read-heavy with GSIs for flexible queries

## Complexity Analysis

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| **GetItem** | O(1) | Direct key lookup |
| **PutItem** | O(1) | Direct write |
| **Query** | O(log N + M) | N=items, M=results returned |
| **Scan** | O(N) | Full table scan, avoid! |
| **BatchGetItem** | O(K) | K=number of items |

### Cost Analysis (Approximate)

**On-Demand pricing (us-east-1)**:
```
Writes: $1.25 per million writes (1KB)
Reads:  $0.25 per million reads (4KB, eventually consistent)

Example: 10M requests/month
- 7M reads (eventually consistent)
- 3M writes
Cost: (7 × $0.25) + (3 × $1.25) = $1.75 + $3.75 = $5.50/month
```

**Provisioned pricing**:
```
WCU: $0.00065 per hour per WCU
RCU: $0.00013 per hour per RCU

Example: 100 RCU, 50 WCU
Cost: (100 × $0.00013 × 730) + (50 × $0.00065 × 730)
    = $9.49 + $23.73 = $33.22/month

Storage: $0.25 per GB-month
```

## Common Problems and Solutions

### 1. Hot Partitions
**Problem**: Single partition key receives most traffic

**Solutions**:
```python
 # Bad: Status as partition key
table = {
    'PK': 'status',  # Only 3 values: active/pending/inactive
    'SK': 'user_id',
    ...
}
 # 90% of users are "active" → Hot partition

 # Good: Add shard suffix
import hashlib

def get_partition_key(user_id, shard_count=10):
    shard = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % shard_count
    return f"active#{shard}"

table = {
    'PK': 'active#7',  # Distributed across 10 partitions
    'SK': 'user_id',
    ...
}
```

### 2. Large Items
**Problem**: Items exceeding 400KB limit or causing high costs

**Solutions**:
```python
 # Store large attributes in S3
item = {
    'user_id': '123',
    'name': 'Alice',
    'profile_image_url': 's3://bucket/images/123.jpg',  # Not in DynamoDB
    'metadata': {...}  # Keep small data in DynamoDB
}

 # Compress large attributes
import gzip, base64

def compress(data):
    return base64.b64encode(gzip.compress(data.encode())).decode()

item = {
    'user_id': '123',
    'large_field': compress(large_data)
}
```

### 3. Expensive Scans
**Problem**: Scan operations costly and slow

**Solutions**:
```python
 # Bad: Full table scan
response = table.scan(
    FilterExpression=Attr('age').gt(25)
)
 # Scans entire table, charges for all items read

 # Good: Use GSI
 # Create GSI with age as sort key, query instead
response = table.query(
    IndexName='AgeIndex',
    KeyConditionExpression=Key('status').eq('active') & Key('age').gt(25)
)

 # Or use parallel scans for analytics (not real-time)
def parallel_scan(segment, total_segments):
    return table.scan(
        Segment=segment,
        TotalSegments=total_segments
    )
```

### 4. GSI Throttling
**Problem**: GSI has insufficient capacity

**Solutions**:
```python
 # Monitor GSI capacity separately
cloudwatch.get_metric_statistics(
    Namespace='AWS/DynamoDB',
    MetricName='UserErrors',
    Dimensions=[
        {'Name': 'TableName', 'Value': 'Users'},
        {'Name': 'GlobalSecondaryIndexName', 'Value': 'EmailIndex'}
    ]
)

 # Set GSI capacity higher than base table if needed
table.update(
    GlobalSecondaryIndexUpdates=[{
        'Update': {
            'IndexName': 'EmailIndex',
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 200,  # Higher than base table
                'WriteCapacityUnits': 100
            }
        }
    }]
)
```

## Key Takeaways

1. **Serverless and fully managed**: Zero operational overhead, but AWS lock-in

2. **Partition key is critical**: Determines data distribution; poor choice leads to hot partitions

3. **Single-digit millisecond latency**: Consistent performance at any scale

4. **Flexible consistency**: Eventually consistent (default, faster) vs strongly consistent (2x cost)

5. **GSIs enable flexible queries**: But have separate capacity and eventual consistency

6. **Global tables for multi-region**: One-click setup for global disaster recovery and low latency

7. **Cost optimization**: On-demand for unpredictable traffic, provisioned for predictable workloads

8. **DynamoDB Streams for event-driven**: Process changes with Lambda for real-time pipelines

---

