# Relational Databases — Interview Q&A

## 1) When would you choose a relational database over NoSQL?

Choose relational databases for transactional workloads requiring strong consistency, multi-row ACID transactions, and complex relational queries.

## 2) How do you scale relational databases?

- Vertical scaling (larger node)
- Read replicas for read-heavy traffic
- Partitioning/sharding for write and data growth
- Caching to reduce database load

## 3) What are common performance levers?

- Proper index design
- Query plan analysis (EXPLAIN)
- Avoiding N+1 and unnecessary full scans
- Denormalization where justified by read patterns

## 4) What are typical interview trade-offs?

- Consistency vs write scalability
- Normalization vs read performance
- Simplicity (single node) vs operational complexity (sharding)

## 5) How do transactions affect availability and throughput?

Stronger isolation and strict transactional guarantees improve correctness but can reduce throughput and increase contention under heavy concurrent writes.

## Deep Dives

- [PostgreSQL Interview Q&A](../postgresql/INTERVIEW-QA.md)

### 1. What is ACID?
ACID stands for Atomicity, Consistency, Isolation, and Durability.

### 2. What is MVCC?
Multi-Version Concurrency Control allows multiple transactions to view consistent states of the database without locking.

### 3. What is connection pooling?
It maintains a cache of database connections so they can be reused when future requests to the database are required.

### 4. What is a primary key?
A unique identifier for a record in a database table.

### 5. What is a foreign key?
A field that uniquely identifies a row in another table.

### 6. What is normalization?
Organizing data in a database to reduce redundancy and improve data integrity.

### 7. What is denormalization?
Adding redundant data to a database to improve read performance.

### 8. What is a transaction?
A single logical unit of work that accesses and possibly modifies the contents of a database.

### 9. What is a deadlock?
When two or more transactions are waiting for each other to release locks.

### 10. What is an index?
A data structure that improves the speed of data retrieval operations.
