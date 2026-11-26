# Distributed Social Graph Engine - Comparison

## Architectural Approaches to Graph Storage

When designing a system to store and query a massive social graph, several architectural patterns emerge. The TAO-style architecture sits between generic graph databases and simple Key-Value caching.

### 1. The "TAO" Architecture (Custom Graph Cache + RDBMS)
This is the approach detailed in this project. It restricts the data model to Objects and Associations, using a two-tier cache to protect a horizontally sharded relational database.

### 2. Generic Graph Database (Neo4j, JanusGraph, TigerGraph)
Purpose-built databases designed to handle complex, deep traversals (N-hop) and execute advanced graph algorithms natively.

### 3. Look-Aside Cache + RDBMS (The Naive Approach)
The traditional web architecture where application servers manage cache population and invalidation explicitly, reading from DBs only on cache misses.

---

## Comparison Matrix

| Concern | TAO Architecture (Custom) | Generic Graph DB (Neo4j) | Look-Aside (Memcached+DB) |
| :--- | :--- | :--- | :--- |
| **Primary Use Case** | Real-time social feeds, shallow traversals (1-2 hop), extremely high read QPS. | Deep traversals, complex pattern matching, fraud detection, recommendation engines. | General purpose web applications with moderate read/write ratios. |
| **Horizontal Scalability** | **Excellent.** Sharding by `id1` is trivial. Supernodes handled via edge sharding. | **Difficult.** Partitioning highly connected graphs while maintaining ACID transactions across shards is notoriously hard. | **Good.** Sharding is standard, but the caching layer suffers from connection explosion. |
| **Read Latency (P99)** | **< 5ms.** 99% of reads hit RAM in the local data center. | **10ms - 100ms+**. Depends heavily on traversal depth and shard distribution. | **< 5ms (Hit) / > 50ms (Miss)**. Prone to severe latency spikes during cache evictions. |
| **Thundering Herd Protection** | **Yes.** Leader cache collapses concurrent requests. | **Varies.** Relies on internal query planners and caches. | **No.** Concurrent misses hit the DB simultaneously. |
| **Data Model Flexibility** | **Rigid.** Strictly Objects and directed Associations. | **Highly Flexible.** Complex properties on edges, multiple labels, schema-free options. | **Flexible.** Application dictates how SQL rows map to cached objects. |
| **Query Complexity** | **Low.** Point lookups, recent edge lists, basic intersections. | **High.** N-hop traversals, shortest path, clustering algorithms. | **Low to Medium.** Depends on SQL queries and application logic. |
| **Consistency** | **Eventual** (Global) + **Read-Your-Writes** (Local/Session). | **Strict (ACID)** often available, sacrificing availability/partition tolerance. | **Eventual/Inconsistent.** Application must carefully manage race conditions during cache updates. |

---

## Why choose TAO over a Graph DB for Social Networks?

It might seem counterintuitive not to use a Graph Database for a Social Graph. However, the requirements of rendering a social news feed are very specific:
1. **Shallow Depth:** You rarely need to know the 6th-degree connection between two random users in real-time. You need to know "Who did my friends just like?" (a 2-hop query).
2. **Read Volume:** 10 Million QPS requires data to be in memory.
3. **Write Volume:** 500k QPS requires shedding strict ACID properties across multiple nodes.

A Generic Graph DB pays a heavy performance penalty to support deep traversals and ACID guarantees—features a real-time social feed does not need. The TAO architecture trades away these complex features to guarantee sub-5ms P99 latencies for shallow lookups at petabyte scale.

## Cross-links
- [PROBLEM.md](./PROBLEM.md)
- [APPROACH.md](./APPROACH.md)
- [DESIGN.md](./DESIGN.md)