# 🌐 High-Level Design (HLD) Concepts

Core building blocks and concepts for designing distributed systems at scale.

---

## 📖 What is HLD?

High-Level Design focuses on:
- **System architecture** - Components and their interactions
- **Scalability** - Handling growth in users/data
- **Reliability** - Ensuring system availability
- **Trade-offs** - Balancing competing concerns (CAP theorem)

---

## 📚 Concept Catalog

### Core Infrastructure

| Concept | What It Solves | Related Concepts | Status |
|---------|---------------|------------------|--------|
| [Load Balancing](./load-balancing/) | Traffic distribution | Scaling, DNS | ✅ Complete |
| [Caching](./caching/) | Reduce latency & load | CDN, Redis | ✅ Complete |
| [Cache Invalidation Patterns](./cache-invalidation-patterns/) | Thundering herd, penetration, avalanche mitigations | Caching | ✅ Complete |
| [Redis](./redis/) | In-memory data structures & caching | Caching, Rate Limiting | ✅ Complete |
| [CDN](./cdn/) | Serve static content globally | Caching, DNS | ✅ Complete |
| [DNS](./dns/) | Domain name resolution | Load balancing, regional routing | ✅ Complete |
| [API Gateway](./api-gateway/) | Request routing & security | Load balancing | ✅ Complete |
| [Microservice Security](./microservice-security/) | Distributed authorization & mTLS | API Gateway | ✅ Complete |
| [Distributed Unique ID Generator](./distributed-unique-id/) | Generating sortable 64-bit distributed IDs | Databases, Sharding | ✅ Complete |

### Data Layer

| Concept | What It Solves | Related Concepts | Status |
|---------|---------------|------------------|--------|
| [Database Sharding](./database-sharding/) | Horizontal data scaling | Replication, Partitioning | ✅ Complete |
| [Database Replication](./database-replication/) | Read scaling & redundancy | Consistency | ✅ Complete |
| [Data Partitioning](./data-partitioning/) | Distribute data across shards while balancing locality and hotspots | Sharding, Consistent Hashing | ✅ Complete |
| [Database Live Re-sharding](./database-live-resharding/) | Zero-downtime cluster topology changes and database migration | Database Sharding, Data Partitioning | ✅ Complete |
| [Storage Engine Internals](./storage-engine-internals/) | B-Tree vs LSM-Tree, WAL, Compaction | Database Replication, NoSQL Databases | ✅ Complete |
| [Database Isolation Levels](./database-isolation-levels/) | Concurrency anomalies, MVCC, snapshot isolation, serializable | Relational Databases, Contention Control | ✅ Complete |
| [Relational Databases](./relational-databases/) | ACID schemas, joins, and transactional modeling | PostgreSQL, Replication | ✅ Complete |
| [SQL Fundamentals](./sql-fundamentals/) | Relational query language, constraints, transactions, and execution plans | Relational Databases, PostgreSQL, MySQL | ✅ Complete |
| [PostgreSQL](./postgresql/) | Transactional SQL primary store and scaling path | Relational Databases, Read Scaling | ✅ Complete |
| [MySQL](./mysql/) | InnoDB-backed OLTP core for orders, payments, inventory, and workflows | Relational Databases, Replication | ✅ Complete |
| [NoSQL Databases](./nosql-databases/) | Document, key-value, graph, and wide-column choices | Cassandra, DynamoDB, Redis | ✅ Complete |
| [SQL vs NoSQL](./sql-vs-nosql/) | Select storage by consistency, query shape, and scale constraints | Relational Databases, NoSQL Databases, CAP Theorem | ✅ Complete |
| [MongoDB](./mongodb/) | Document modeling, indexes, replica sets, and shard-key design | NoSQL Databases, Database Sharding | ✅ Complete |
| [Cassandra](./cassandra/) | High-write distributed NoSQL storage | CAP Theorem, Partitioning | ✅ Complete |
| [DynamoDB](./dynamodb/) | Managed key-value/document access at scale | API Design, Partitioning | ✅ Complete |
| [Time Series Databases](./time-series-databases/) | Metrics, IoT, time-indexed data | Monitoring, Compression | ✅ Complete |
| [Indexing Strategies](../00-theory/database-concepts/indexing.md) | Query performance | Database design | ✅ Complete |
| [Search Systems](./search-systems/) | Full-text search, relevance, and analytics | Elasticsearch, Indexing | ✅ Complete |
| [Elasticsearch](./elasticsearch/) | Full-text search & analytics | Sharding, Monitoring | ✅ Complete |
| [Read Scaling](./read-scaling/) | Fan-out readiness and cache amplification for read-heavy slabs | [Caching](./caching/), [Database Replication](./database-replication/), [CDN](./cdn/), [News Feed](../04-hld-projects/news-feed/), [Video Streaming](../04-hld-projects/video-streaming/), [Video Recommendations](../04-hld-projects/video-recommendations/) | ✅ Complete |
| [Write Scaling](./write-scaling/) | Partitioning, batching, and burst control for high-volume writes | [Database Sharding](./database-sharding/), [Message Queues](./message-queues/), [Database Replication](./database-replication/), [News Feed](../04-hld-projects/news-feed/), [Video Streaming](../04-hld-projects/video-streaming/) | ✅ Complete |
| [Large Blob Handling](./large-blob-handling/) | Chunked uploads, storage, and delivery for heavy media assets | [CDN](./cdn/), [Caching](./caching/), [Message Queues](./message-queues/), [File Storage](../04-hld-projects/file-storage/), [Video Streaming](../04-hld-projects/video-streaming/) | ✅ Complete |
| [Object Storage](./object-storage/) | S3-like blob/object storage | [Large Blob Handling](./large-blob-handling/), [CDN](./cdn/) | ✅ Complete |

### Communication

| Concept | What It Solves | Related Concepts | Status |
|---------|---------------|------------------|--------|
| [Message Queues](./message-queues/) | Async processing | Kafka, RabbitMQ | ✅ Complete |
| [Message Queue Evolution](./message-queue-evolution/) | Evolution from Smart Broker (RabbitMQ) to Dumb Broker (Kafka) to Decoupled (Pulsar) | Message Queues, Kafka | ✅ Complete |
| [Kafka](./kafka/) | Distributed event streaming | Message Queues, Monitoring | ✅ Complete |
| [Stream Processing](./stream-processing/) | Stateful real-time event processing | Kafka, Flink, Monitoring | ✅ Complete |
| [Flink](./flink/) | Low-latency stateful stream engine | Stream Processing, Kafka | ✅ Complete |
| [Microservices Communication](./microservices-communication/) | Service-to-service calls | Circuit Breaker, Retry | ✅ Complete |
| [API Design](./api-design/) | Service interfaces and API contracts | REST, gRPC, auth/rate limiting | ✅ Complete |
| [Real-time Updates](./real-time-updates/) | Choose channels for push/pull delivery | Message Queues, Load Balancing | ✅ Complete |
| [WebSockets](./websockets/) | Maintain bidirectional, low-latency client connections | Real-time Updates, Presence, Message Queues | ✅ Complete |
| [Network Protocol Evolution](./network-protocol-evolution/) | HTTP/1.1 vs HTTP/2 vs HTTP/3 QUIC, head-of-line blocking, gRPC | WebSockets, API Design | ✅ Complete |

### Reliability & Performance

| Concept | What It Solves | Related Concepts | Status |
|---------|---------------|------------------|--------|
| [Logical Clocks & TrueTime](./logical-clocks-truetime/) | Causality tracking and external consistency bounds | CAP Theorem, Distributed Transactions | ✅ Complete |
| [Rate Limiting](./rate-limiting/) | Protect from overload | API Gateway | ✅ Complete |
| [Distributed Rate Limiting](./distributed-rate-limiting-scale/) | Multi-node rate limiting state synchronization | Rate Limiting, API Gateway | ✅ Complete |
| [Idempotency](./idempotency/) | Retry-safe side effects | API Design, Queues, Workflows | ✅ Complete |
| [Distributed Transactions](./distributed-transactions/) | Cross-service correctness decisions | Idempotency, Sagas, Outbox | ✅ Complete |
| [Distributed Transactions: Saga Outbox](./distributed-transactions-saga-outbox/) | Distributed transaction compensations and deduplication | CDC, Outbox, Sagas | ✅ Complete |
| [CAP Theorem](./cap-theorem/) | Consistency vs Availability decisions under partition | Distributed systems, Replication | ✅ Complete |
| [PACELC Theorem](./pacelc-theorem/) | Consistency vs Latency extension of CAP | CAP Theorem, Distributed systems | ✅ Complete |
| [Consistent Hashing](./consistent-hashing/) | Balanced data distribution | Sharding | ✅ Complete |
| [Pattern Selection](./pattern-selection/) | Pick design patterns based on bottlenecks | Caching, Queues, Sharding | ✅ Complete |
| [Long-Running Tasks](./long-running-tasks/) | Coordinate background jobs, retries, and TTL-based workflows | [Message Queues](./message-queues/), [Workflow Orchestration](./workflow-orchestration/), [Database Sharding](./database-sharding/), [File Storage](../04-hld-projects/file-storage/), [Video Streaming](../04-hld-projects/video-streaming/) | ✅ Complete |
| [Contention Control](./contention-control/) | Coordinate writes under conflict | Transactions, Distributed locks | ✅ Complete |
| [Workflow Orchestration](./workflow-orchestration/) | Durable multi-step processing | Message Queues, Outbox, Sagas | ✅ Complete |
| [Resilience Patterns](./resilience-patterns/) | Handle cascading failures gracefully | Circuit Breakers, Bulkheads, Retries | ✅ Complete |
| [Multi-Region Active-Active](./multi-region-active-active/) | Global low-latency reads/writes, regional failover, and conflict resolution (LWW, CRDTs) | Database Replication, CAP Theorem, Logical Clocks & TrueTime | ✅ Complete |

### Observability & Operations

| Concept | What It Solves | Related Concepts | Status |
|---------|---------------|------------------|--------|
| [Monitoring & Observability](./monitoring-observability/) | System visibility | Metrics, Logs, Traces | ✅ Complete |
| [Service Discovery](./service-discovery/) | Finding service instances | Load Balancing | ✅ Complete |
| [Distributed Coordination](./distributed-coordination/) | Leader election, locks, and shared configuration | ZooKeeper, Service Discovery | ✅ Complete |
| [ZooKeeper](./zookeeper/) | Distributed coordination | Leader Election, Config Management | ✅ Complete |
| [Distributed Consensus Raft](./distributed-consensus-raft/) | State replication and partition tolerance | ZooKeeper, Distributed Coordination | ✅ Complete |

---

## 🗺️ Concept Dependency Map

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  Server  │  │  Server  │  │  Server  │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │             │             │
             └──────────┬──┴─────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
        ┌──────────┐        ┌──────────┐
        │   Cache  │        │ Message  │
        │  (Redis) │        │  Queue   │
        └────┬─────┘        └────┬─────┘
             │                   │
             ▼                   ▼
        ┌──────────────────────────────┐
        │         Databases            │
        │  ┌──────┐      ┌──────┐     │
        │  │Master│──────│Slave │     │
        │  └──────┘      └──────┘     │
        └──────────────────────────────┘
```

### Scaling Dependencies

- [Read Scaling](./read-scaling/) lives between caches and replicas, so practice tuning cache TTLs, stale reads, and CDN pushes before tuning this pathway.
- [Write Scaling](./write-scaling/) keeps write hotspots under control by pairing sharding keys with queues and replication pipelines, so study database partitioning and queue backpressure together.
- [Large Blob Handling](./large-blob-handling/) bridges upload/front-end storage tiers with CDN delivery, so focus on chunking, TTL cleanup, and caching layers.
- [Idempotency](./idempotency/) sits across APIs, queues, and workflows; use it before claiming retries, replay, or exactly-once behavior is safe.
- [Distributed Transactions](./distributed-transactions/) sits above idempotency and workflows; use it when one business invariant spans payments, inventory, ledgers, queues, or external providers.
- [Long-Running Tasks](./long-running-tasks/) gives visibility into background jobs used by File Storage and Video Streaming workflows; cross-check it with message queues, workflow orchestration, and monitoring patterns.

### Learning Dependencies

| Before Learning... | First Understand... |
|--------------------|---------------------|
| [Database Sharding](./database-sharding/) | SQL basics, partitioning |
| [SQL Fundamentals](./sql-fundamentals/) | [Relational Databases](./relational-databases/), [Indexing Strategies](../00-theory/database-concepts/indexing.md), transaction boundaries |
| [PostgreSQL](./postgresql/) | [Relational Databases](./relational-databases/), indexes, transactions |
| [MySQL](./mysql/) | [SQL Fundamentals](./sql-fundamentals/), [Database Replication](./database-replication/), [Read Scaling](./read-scaling/) |
| [NoSQL Databases](./nosql-databases/) | [CAP Theorem](./cap-theorem/), access patterns |
| [MongoDB](./mongodb/) | [NoSQL Databases](./nosql-databases/), document modeling, replica sets |
| [Cassandra](./cassandra/) / [DynamoDB](./dynamodb/) | [NoSQL Databases](./nosql-databases/), partition keys, consistency choices |
| [Search Systems](./search-systems/) / [Elasticsearch](./elasticsearch/) | [Indexing Strategies](../00-theory/database-concepts/indexing.md), query patterns |
| [Stream Processing](./stream-processing/) / [Flink](./flink/) | [Message Queues](./message-queues/), event ordering, late data |
| [Caching](./caching/) | Database concepts, latency |
| [Load Balancing](./load-balancing/) | HTTP, server concepts |
| [Message Queues](./message-queues/) | Async vs sync, decoupling |
| [Idempotency](./idempotency/) | [API Design](./api-design/), [Message Queues](./message-queues/), retry semantics |
| [Distributed Transactions](./distributed-transactions/) | [Idempotency](./idempotency/), [Workflow Orchestration](./workflow-orchestration/), [Message Queues](./message-queues/), [Contention Control](./contention-control/) |
| [CAP Theorem](./cap-theorem/) | [Database Replication](./database-replication/) |
| [Consistent Hashing](./consistent-hashing/) | Hash functions, distribution |
| [PACELC Theorem](./pacelc-theorem/) | CAP extension, [Database Replication](./database-replication/), consistency trade-offs |
| [Distributed Coordination](./distributed-coordination/) / [ZooKeeper](./zookeeper/) | Failure detection, consensus basics |
| [Pattern Selection](./pattern-selection/) | [Caching](./caching/), queues, sharding basics |
| [Read Scaling](./read-scaling/) | [Caching](./caching/), [Database Replication](./database-replication/), [CDN](./cdn/) |
| [Write Scaling](./write-scaling/) | [Database Sharding](./database-sharding/), [Message Queues](./message-queues/), [Database Replication](./database-replication/) |
| [Large Blob Handling](./large-blob-handling/) | [CDN](./cdn/), [Caching](./caching/), [Message Queues](./message-queues/) |
| [Object Storage](./object-storage/) | [Database Sharding](./database-sharding/), [Large Blob Handling](./large-blob-handling/) |
| [Long-Running Tasks](./long-running-tasks/) | [Message Queues](./message-queues/), [Workflow Orchestration](./workflow-orchestration/), [Monitoring & Observability](./monitoring-observability/) |
| Applied ML diagnostics | [ML Generalization](../06-genai-systems/00-concepts/ml-generalization/), [Monitoring & Observability](./monitoring-observability/) |

---

## 🛤️ Recommended Learning Order

### Foundation (Week 1)
```
1. CAP Theorem → Understand trade-offs
   ↓
2. Relational vs NoSQL Databases → Choose right storage
   ↓
3. Caching → Reduce latency
```

### Scaling (Week 2)
```
4. Load Balancing → Distribute traffic
   ↓
5. Database Replication → Read scaling
   ↓
6. Database Sharding → Write scaling
```

### Advanced (Week 3)
```
7. Message Queues → Async processing
   ↓
8. Consistent Hashing → Data distribution
   ↓
9. Rate Limiting → Protection
   ↓
10. Idempotency → Retry-safe mutations and replay
    ↓
11. Distributed Transactions → Choose saga, outbox, TCC, 2PC, or reconciliation boundaries
    ↓
12. Pattern Selection → Fast architecture decisions
    ↓
13. Read Scaling → Align caches, replicas, and CDN tails
    ↓
14. Write Scaling → Partition, batch, and throttle high-write spikes
    ↓
15. Large Blob Handling → Chunk uploads, cache CDN edges, enforce TTL cleanup
    ↓
15.5 Object Storage → Distributed blob storage with S3 architecture
    ↓
16. Long-Running Tasks → Track background jobs with heartbeats and retries
```

---

## 📖 Each Concept Includes

1. **📚 Theory**
   - What is it?
   - Why do we need it?
   - How does it work?

2. **🎯 When to Use**
   - Use cases
   - Trade-offs
   - Alternatives

3. **🏗️ Implementation**
   - Common technologies
   - Configuration examples
   - Best practices

4. **🔗 Cross-References**
   - Related concepts
   - HLD projects using this concept

5. **❓ Interview Q&A**
   - Common questions
   - Deep-dive topics

---

## 🔗 Concept → Project Mapping

| Concept | Used In These Projects |
|---------|----------------------|
| [Load Balancing](./load-balancing/) | All HLD projects |
| [Caching](./caching/) | Twitter, URL Shortener, Instagram, Distributed Cache |
| [Cache Invalidation Patterns](./cache-invalidation-patterns/) | Twitter, Distributed Cache, High-traffic read paths |
| [Message Queues](./message-queues/) | Twitter, Notification system |
| [Redis](./redis/) | API Gateway, Social feeds, caching layers |
| [Storage Engine Internals](./storage-engine-internals/) | Relational Databases, NoSQL Databases, Time Series Databases |
| [Message Queue Evolution](./message-queue-evolution/) | System design decisions regarding scale, throughput, retention, and cloud-native deployments |
| [Kafka](./kafka/) | Event pipelines, notifications, analytics ingestion |
| [Stream Processing](./stream-processing/) | Realtime Metrics Platform, fraud detection, analytics pipelines |
| [Flink](./flink/) | Realtime Metrics Platform, event-time aggregation, anomaly detection |
| [Relational Databases](./relational-databases/) | Payment systems, booking flows, user/account metadata |
| [SQL Fundamentals](./sql-fundamentals/) | Payment systems, booking flows, inventory, workflows, reporting queries |
| [PostgreSQL](./postgresql/) | Orders, workflows, relational metadata, transactional APIs |
| [MySQL](./mysql/) | OLTP source of truth for users, orders, inventory, payments, and workflows |
| [NoSQL Databases](./nosql-databases/) | Feed storage, profile documents, large-scale key-value access |
| [MongoDB](./mongodb/) | Profile documents, catalog aggregates, content metadata, flexible product shapes |
| [Elasticsearch](./elasticsearch/) | Search-heavy systems, log analytics |
| [Search Systems](./search-systems/) | E-commerce search, log analytics, content discovery |
| [Cassandra](./cassandra/) | Feed/timeline storage, write-heavy event pipelines |
| [DynamoDB](./dynamodb/) | Key-value workloads, metadata and lookup-heavy APIs |
| [Database Sharding](./database-sharding/) | Twitter, Chat app |
| [Database Replication](./database-replication/) | Chat Service, News Feed, Payment System, multi-region read paths |
| [Data Partitioning](./data-partitioning/) | URL Shortener, Chat Service, News Feed |
| [Database Live Re-sharding](./database-live-resharding/) | Twitter, Chat app, URL Shortener, systems requiring zero-downtime |
| [SQL vs NoSQL](./sql-vs-nosql/) | Chat Service, News Feed, Ecommerce Backend |
| [Read Scaling](./read-scaling/) | News Feed, Video Streaming, File Storage, Social Post Search |
| [Write Scaling](./write-scaling/) | News Feed, Ad Click Aggregator, Job Scheduler, File Storage |
| [Large Blob Handling](./large-blob-handling/) | File Storage, Video Streaming, News Feed rich media uploads |
| [Object Storage](./object-storage/) | File Storage, Video Streaming |
| [Time Series Databases](./time-series-databases/) | Metrics Monitoring, Realtime Metrics Platform, Price Tracking Service |
| [Real-time Updates](./real-time-updates/) | Chat app, collaborative editing, live dashboards |
| [WebSockets](./websockets/) | Chat Service, Brokerage Platform, Collaborative Document Editor |
| [CDN](./cdn/) | YouTube, Instagram, Netflix |
| [DNS](./dns/) | Video Streaming, Ride Sharing, globally distributed systems |
| [API Gateway](./api-gateway/) | API front doors, request routing, auth, throttling, protocol mediation |
| [API Design](./api-design/) | All HLD projects (interface contracts, pagination, idempotency) |
| [Microservice Security](./microservice-security/) | Any highly distributed microservice system |
| [Microservices Communication](./microservices-communication/) | Payment System, E-commerce Backend, Ride Sharing, Notification Service |
| [Idempotency](./idempotency/) | Payment System, Ad Click Aggregator, Job Scheduler, Web Crawler, Agentic tool workflows |
| [Distributed Transactions](./distributed-transactions/) | Payment System, E-commerce Backend, Ticketing Platform, Brokerage Platform |
| [Distributed Transactions: Saga Outbox](./distributed-transactions-saga-outbox/) | Payment System, E-commerce Backend, Ticketing Platform |
| [Rate Limiting](./rate-limiting/) | API Gateway, URL Shortener |
| [Distributed Rate Limiting](./distributed-rate-limiting-scale/) | API Gateway, Distributed Rate Limiter |
| [Consistent Hashing](./consistent-hashing/) | Distributed Cache, sharding, collaborative session routing |
| [CAP Theorem](./cap-theorem/) | Payment/booking consistency paths, multi-region degraded modes |
| [PACELC Theorem](./pacelc-theorem/) | DynamoDB, Cassandra, CockroachDB design trade-offs |
| [Pattern Selection](./pattern-selection/) | Interview decomposition across HLD projects |
| [Long-Running Tasks](./long-running-tasks/) | File Storage cleanup, News Feed ranking, Video Streaming processing |
| [Contention Control](./contention-control/) | Online Auction, Brokerage Platform, Ride Sharing, News Feed |
| [Workflow Orchestration](./workflow-orchestration/) | E-commerce Backend, Payment System, File Storage, Brokerage Platform |
| [Logical Clocks & TrueTime](./logical-clocks-truetime/) | DynamoDB, Cassandra, Relational Databases, multi-region setups |
| [Resilience Patterns](./resilience-patterns/) | Microservices, API Gateway, Distributed Systems |
| [Multi-Region Active-Active](./multi-region-active-active/) | Multi-Region Active-Active, File Storage, Distributed Cache, URL Shortener, Ad Click Aggregator |
| [Distributed Unique ID Generator](./distributed-unique-id/) | URL Shortener, Twitter, Instagram, Ticket Servers |
| [Database Isolation Levels](./database-isolation-levels/) | Financial Ledger, Digital Wallet, E-commerce Checkout, Booking System |
| [Network Protocol Evolution](./network-protocol-evolution/) | Video Streaming, Live Chat, Real-Time Gaming, API Gateway |
| [Distributed Coordination](./distributed-coordination/) | Service discovery, leader election, distributed locks |
| [Service Discovery](./service-discovery/) | Microservice fleets, dynamic routing, health-aware load balancing |
| [Monitoring & Observability](./monitoring-observability/) | Realtime Metrics Platform, Content Moderation, Bot Detection, Video Recommendations |
| [Distributed Consensus Raft](./distributed-consensus-raft/) | Distributed databases (CockroachDB, MySQL Raft), replicated logs, strict consistency under partition |
| [ZooKeeper](./zookeeper/) | Leader election, distributed locks, service coordination metadata |

---

## ✅ Completion Checklist

### Infrastructure
- [x] Load Balancing
- [x] Caching
- [x] Cache Invalidation Patterns
- [x] Distributed Unique ID Generator
- [x] Redis
- [x] CDN
- [x] DNS
- [x] API Gateway
- [x] Microservice Security

### Data Layer
- [x] Storage Engine Internals
- [x] Database Isolation Levels
- [x] Database Sharding
- [x] Database Replication
- [x] Data Partitioning
- [x] Database Live Re-sharding
- [x] Relational Databases
- [x] SQL Fundamentals
- [x] PostgreSQL
- [x] MySQL
- [x] NoSQL Databases
- [x] SQL vs NoSQL
- [x] MongoDB
- [x] Cassandra
- [x] DynamoDB
- [x] Time Series Databases
- [x] Search Systems
- [x] Elasticsearch
- [x] Indexing Strategies
- [x] Read Scaling
- [x] Write Scaling
- [x] Large Blob Handling
- [x] Object Storage
- [x] Stream Processing
- [x] Flink

### Communication
- [x] Message Queues
- [x] Message Queue Evolution
- [x] Kafka
- [x] Microservices Communication
- [x] API Design
- [x] Real-time Updates
- [x] WebSockets
- [x] Network Protocol Evolution

### Reliability & Operations
- [x] Logical Clocks & TrueTime
- [x] Rate Limiting
- [x] Distributed Rate Limiting
- [x] Idempotency
- [x] Distributed Transactions
- [x] Distributed Transactions: Saga Outbox
- [x] Consistent Hashing
- [x] Pattern Selection
- [x] Long-Running Tasks
- [x] Contention Control
- [x] Workflow Orchestration
- [x] Resilience Patterns
- [x] Multi-Region Active-Active
- [x] Monitoring & Observability
- [x] Service Discovery
- [x] Distributed Coordination
- [x] Distributed Consensus Raft
- [x] ZooKeeper
- [x] CAP Theorem
- [x] PACELC Theorem

---

## 🧭 Section Navigation

| | |
|---|---|
| **Prerequisites** | [Theory ←](../00-theory/) — networking, databases, system fundamentals |
| **What's Next** | [HLD Projects →](../04-hld-projects/) — apply concepts to full system designs |
| **Related** | [Case Studies](../case-studies/) · [Cheatsheets](../resources/cheatsheets/) |

---

## 📌 Study Tips

1. **Visualize** - Draw diagrams to understand data flow
2. **Think about failures** - What happens when a component fails?
3. **Know the numbers** - Latency, throughput, capacity
4. **Compare options** - Redis vs Memcached, Kafka vs RabbitMQ
5. **Practice estimation** - Back-of-envelope calculations

---

*🌐 Concept deep-dives are continuously expanded; use each concept folder for latest theory + interview packs.*
