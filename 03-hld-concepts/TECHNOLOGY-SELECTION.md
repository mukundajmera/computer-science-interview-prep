# Technology Selection Guide

| Need | Technology | Why | When Not To Use | Link |
|---|---|---|---|---|
| In-memory caching, fast key-value | Redis | Extremely low latency, rich data structures | Need durable storage as primary DB | [Redis](./redis/) |
| High-throughput event streaming | Kafka | Distributed, fault-tolerant log, replayable | Simple queues without replay needs | [Kafka](./kafka/) |
| Wide-column NoSQL, high writes | Cassandra | Masterless architecture, highly available | ACID transactions with joins needed | [Cassandra](./cassandra/) |
| Managed NoSQL, predictable scaling | DynamoDB | Fully managed, auto-scaling, strong AWS integration | Multi-cloud or complex queries needed | [DynamoDB](./dynamodb/) |
| Full-text search and analytics | Elasticsearch | Inverted index, powerful text search capabilities | Simple CRUD ops on primary data | [Elasticsearch](./elasticsearch/) |
| Relational DB, complex queries | PostgreSQL | Strong consistency, JSONB support, extensible | Highly unstructured data without schema | [PostgreSQL](./postgresql/) |
| Relational DB, standard ACID | MySQL | Widely supported, proven replication | Need extremely high write scalability | [MySQL](./mysql/) |
| Document NoSQL, flexible schema | MongoDB | BSON documents, horizontal scaling via sharding | Strict relational constraints needed | [MongoDB](./mongodb/) |
| Distributed coordination, consensus | ZooKeeper | Strongly consistent configuration and locks | High write throughput data storage | [ZooKeeper](./zookeeper/) |
| Real-time stream processing | Flink | Stateful computations over data streams | Simple batch processing is sufficient | [Flink](./flink/) |
