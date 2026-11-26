# Relational Databases

## Overview

Relational databases organize data into structured tables with predefined schemas, using SQL for querying and maintaining ACID properties for data consistency. They remain the foundation of most applications requiring transactional integrity and complex query support.

## Core Concepts

### ACID Properties
- **Atomicity**: Transactions complete fully or not at all
- **Consistency**: Data remains valid across all constraints
- **Isolation**: Concurrent transactions don't interfere with each other
- **Durability**: Committed changes survive system failures

### Normalization
Process of organizing data to reduce redundancy:
- **1NF**: Atomic values, no repeating groups
- **2NF**: No partial dependencies on composite keys
- **3NF**: No transitive dependencies
- **BCNF**: Every determinant is a candidate key

### Indexing Strategies
- **B-tree indexes**: General-purpose, range queries
- **Hash indexes**: Equality lookups only
- **Bitmap indexes**: Low-cardinality columns
- **Partial indexes**: Index subset of rows
- **Covering indexes**: Include all queried columns

## Coverage in This Section

| Technology | Status | Focus Areas |
|------------|--------|-------------|
| [**PostgreSQL**](../postgresql/THEORY.md) | ✅ Complete | Advanced features, MVCC, replication, partitioning |
| [MySQL](../mysql/THEORY.md) | ✅ Complete | InnoDB engine, clustering, replication |
| [SQL Fundamentals](../sql-fundamentals/THEORY.md) | ✅ Complete | Query optimization, execution plans, transactions |

## When to Use Relational Databases

✅ **Use when you need**:
- Strong consistency and ACID guarantees
- Complex queries with joins across multiple tables
- Transactions with rollback support
- Well-defined schema with relationships
- Mature tooling and broad expertise availability

❌ **Consider alternatives when**:
- Horizontal scaling to massive scale is primary requirement
- Schema changes are very frequent
- Data is unstructured or semi-structured
- Eventually consistent is acceptable

## Common Interview Questions

1. **Normalization vs Denormalization**: When to normalize and when to denormalize for performance?
2. **Index Design**: How to choose the right indexes? When do they hurt performance?
3. **Transaction Isolation Levels**: What are different isolation levels and their trade-offs?
4. **Scaling Patterns**: How to scale relational databases? (Read replicas, sharding, partitioning)
5. **MVCC vs Locking**: How do different concurrency control mechanisms work?

## Related Concepts

- [Database Sharding](../database-sharding/) - Horizontal partitioning strategies
- [Database Replication](../database-replication/) - Master-slave and multi-master patterns
- [Caching](../caching/) - Reducing database load with Redis/Memcached
- [SQL Fundamentals](../sql-fundamentals/THEORY.md) - Query shape, joins, isolation, and execution-plan reading
- [MySQL](../mysql/THEORY.md) - InnoDB-backed relational design and web workload scaling
- [NoSQL Databases](../nosql-databases/) - Alternative data models for different use cases

## Technology Comparison

| Feature | PostgreSQL | MySQL | SQLite |
|---------|-----------|-------|--------|
| **License** | Open source (PostgreSQL License) | Open source + Commercial | Public domain |
| **ACID** | Full support | Full (InnoDB) | Full |
| **Concurrency** | MVCC | MVCC (InnoDB) | Locking |
| **JSON Support** | Native JSONB | JSON type | JSON functions |
| **Full-text Search** | Built-in | Limited | FTS5 extension |
| **Replication** | Streaming, logical | Binary log, GTID | Not built-in |
| **Use Cases** | General-purpose, analytical | Web applications | Embedded, mobile |

## Learning Path

1. Start with [SQL Fundamentals](../sql-fundamentals/THEORY.md) for joins, transactions, and execution plans
2. Study [PostgreSQL Theory](../postgresql/THEORY.md) for comprehensive RDBMS concepts
3. Compare with [MySQL](../mysql/THEORY.md) for InnoDB, replica lag, and web workload trade-offs
4. Explore [Database Sharding](../database-sharding/) for scaling patterns
5. Compare with [NoSQL Databases](../nosql-databases/) to understand trade-offs

## Key Takeaways

- Relational databases excel at structured data with complex relationships
- ACID properties ensure data consistency but may limit horizontal scalability
- Proper indexing is critical for query performance
- MVCC enables high concurrency without locking readers
- Understanding when NOT to use RDBMS is as important as knowing when to use them
