# NoSQL Databases

## Overview

NoSQL (Not Only SQL) databases are non-relational data stores designed for specific data models and access patterns that require flexible schemas, horizontal scalability, and high performance. They sacrifice some ACID guarantees for availability and partition tolerance.

## Why NoSQL?

**Problems traditional RDBMS struggle with**:
- Horizontal scalability to thousands of nodes
- Handling massive write throughput (millions of writes/sec)
- Flexible schema for rapidly evolving data models
- Geographic distribution with local latency
- Specific data models (documents, graphs, time-series)

## NoSQL Database Types

### Document Stores
**Examples**: MongoDB, Couchbase
- Store data as JSON-like documents
- Flexible schema per document
- Good for: Content management, user profiles, catalogs

### Wide-Column Stores
**Examples**: Cassandra, HBase, ScyllaDB
- Data organized into column families
- Excellent write performance
- Good for: Time-series, IoT, messaging, activity feeds

### Key-Value Stores
**Examples**: Redis, DynamoDB, Riak
- Simple key-value pairs
- Extremely fast lookups
- Good for: Caching, session storage, real-time data

### Graph Databases
**Examples**: Neo4j, Amazon Neptune
- Nodes and edges represent relationships
- Efficient traversal queries
- Good for: Social networks, recommendation engines, fraud detection

## Coverage in This Section

| Database | Type | Status | Focus Areas |
|----------|------|--------|-------------|
| **Cassandra** | Wide-Column | ✅ Complete | Masterless architecture, LSM trees, tunable consistency |
| **DynamoDB** | Key-Value/Document | ✅ Complete | AWS managed, partition keys, global tables |
| [MongoDB](../mongodb/THEORY.md) | Document | ✅ Complete | Document model, aggregation pipeline, replica sets, sharding |

## CAP Theorem Positioning

```
        Consistency (C)
              △
             ╱ ╲
            ╱   ╲
           ╱     ╲
          ╱  CA   ╲
         ╱  (RDBMS)╲
        ╱___________╲
       ╱ CP       AP ╲
      ╱  (MongoDB) (Cassandra,
     ╱              DynamoDB)
    ╱_____________________╲
Partition         Availability (A)
Tolerance (P)
```

**Trade-offs**:
- **CP Systems**: Sacrifice availability during network partitions for consistency
  - MongoDB (in certain configurations), HBase
- **AP Systems**: Sacrifice strong consistency for availability and partition tolerance
  - Cassandra, DynamoDB, Riak
- **CA Systems**: Cannot tolerate partitions (not suitable for distributed systems)
  - Single-node RDBMS

## When to Use NoSQL

✅ **Use NoSQL when you need**:
- Horizontal scalability to handle massive data volumes
- High write throughput (millions of writes/sec)
- Flexible, evolving schemas
- Geographic distribution with local reads/writes
- Specific data models (documents, graphs, key-value)
- Eventually consistent is acceptable

❌ **Stick with SQL when you need**:
- Complex queries with JOINs across multiple entities
- Strong consistency and ACID transactions
- Mature tooling and broader expertise
- Well-defined, stable schema with relationships
- Secondary indexes on multiple columns

## SQL vs NoSQL Comparison

| Feature | Relational (SQL) | NoSQL |
|---------|-----------------|-------|
| **Schema** | Fixed, predefined | Flexible, schema-less |
| **Scaling** | Vertical (scale-up) | Horizontal (scale-out) |
| **Consistency** | Strong ACID | Eventual consistency (tunable) |
| **Joins** | Supported | Limited or none |
| **Transactions** | Multi-row ACID | Limited (single partition/document) |
| **Query Language** | SQL (standard) | Database-specific APIs |
| **Use Cases** | Transactional systems, complex queries | Big data, real-time, flexible schemas |
| **Examples** | PostgreSQL, MySQL | Cassandra, MongoDB, DynamoDB |

## Consistency Models

### Strong Consistency
```
Write(x=1) → All reads return 1 immediately
```
**Databases**: MongoDB (with WriteConcern=majority), DynamoDB (strongly consistent reads)

### Eventual Consistency
```
Write(x=1) → Some reads return 0, eventually all return 1
```
**Databases**: Cassandra (default), DynamoDB (eventually consistent reads), Riak

### Causal Consistency
```
If operation A causes B, all processes see A before B
```
**Databases**: Cassandra (with SERIAL consistency), CosmosDB

### Tunable Consistency (Cassandra, DynamoDB)
```sql
-- Cassandra: Choose per-query
SELECT * FROM users WHERE id = 123 USING CONSISTENCY QUORUM;

-- DynamoDB: Choose per-request
GetItem(ConsistentRead=true)  // Strong consistency
GetItem(ConsistentRead=false) // Eventual consistency (cheaper, faster)
```

## Common Patterns

### 1. Denormalization
NoSQL favors denormalization for read performance:

```json
// Normalized (SQL approach)
users: { id: 1, name: "Alice" }
orders: { id: 101, user_id: 1, total: 50 }

// Denormalized (NoSQL approach)
orders: {
  id: 101,
  user_id: 1,
  user_name: "Alice",  // Duplicated
  total: 50
}
```

**Trade-off**: Faster reads, but updates must modify multiple records

### 2. Partition Key Design
Critical for performance in distributed NoSQL databases:

```
Good: user_id as partition key (evenly distributed)
Bad: country as partition key (hot partitions for popular countries)
```

### 3. Composite Keys
```sql
-- Cassandra: Partition key + clustering key
PRIMARY KEY ((user_id), created_at)

-- DynamoDB: Partition key + sort key
PK: user_id, SK: timestamp
```

**Benefit**: Range queries within a partition

## Interview Questions to Prepare

1. **CAP Theorem**: Explain CAP theorem and how Cassandra/DynamoDB fit into it
2. **Consistency Levels**: What are different consistency levels in Cassandra?
3. **Partition Key Design**: How do you choose a partition key in DynamoDB?
4. **SQL vs NoSQL**: When would you choose NoSQL over SQL?
5. **Eventual Consistency**: What are the implications of eventual consistency?
6. **Scaling Patterns**: How does NoSQL achieve horizontal scalability?
7. **Data Modeling**: How is data modeling different in NoSQL vs SQL?

## Related Concepts

- [Consistent Hashing](../consistent-hashing/) - How NoSQL databases distribute data
- [Database Sharding](../database-sharding/) - Horizontal partitioning patterns
- [Database Replication](../database-replication/) - Replication strategies
- [Caching](../caching/) - Redis as a NoSQL key-value cache
- [MongoDB](../mongodb/THEORY.md) - Document modeling, replica sets, aggregation, and sharding
- [Relational Databases](../relational-databases/) - When to use SQL instead

## Learning Path

1. **Start with CAP theorem**: Understand trade-offs between consistency, availability, partition tolerance
2. **Study MongoDB**: Learn document modeling, indexes, aggregation, replica sets, and sharding
3. **Study Cassandra**: Learn wide-column model, tunable consistency, masterless architecture
4. **Study DynamoDB**: Learn key-value model, partition/sort keys, AWS-specific features
5. **Compare approaches**: Understand when to use each database type
6. **Practice data modeling**: Design schemas for common use cases (messaging, IoT, e-commerce)

## Key Takeaways

- NoSQL databases trade ACID guarantees for scalability and availability
- Choose database type based on access patterns (document, key-value, wide-column, graph)
- Partition key design is critical for performance in distributed NoSQL
- Denormalization is standard practice in NoSQL for read performance
- Eventual consistency requires application-level handling
- NoSQL is not a replacement for SQL - use the right tool for the job
