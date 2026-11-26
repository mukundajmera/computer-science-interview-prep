# Distributed Social Graph Engine (Meta TAO)

## Problem Statement

Design a distributed, highly-available, read-optimized social graph engine capable of handling extreme read/write volumes. This system models the underlying graph data of a massive social network (users, posts, comments, likes, friendship associations) using an Objects (Nodes) and Associations (Directed Edges) data model, inspired by Meta's TAO.

---

## Requirements and Constraints

### Functional Requirements

1. **Objects & Associations:** Support creation, retrieval, updating, and deletion of objects (nodes) and associations (directed edges).
2. **Graph Traversal:** Support efficient point lookups and local graph traversals, specifically 2-hop BFS traversals (e.g., mutual friends, friends-of-friends).
3. **Consistency:** Eventual consistency for reads across replicas; read-your-writes consistency for the originating user/client where possible.
4. **Resiliency:** Highly available for reads, even during network partitions or regional failovers.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Read Latency | P99 < 5ms |
| Write Latency | P99 < 50ms |
| Availability | 99.999% |
| Read QPS | 10 Million |
| Write QPS | 500,000 |
| Read/Write Ratio | Extremely high (e.g., 20:1 to 500:1 depending on the object) |

### Capacity Assumptions

- **Users:** 3 Billion users.
- **Edges:** 100 Billion friend associations; 10 Trillion total graph edges (including interactions, group memberships, etc.).
- **Read QPS:** 10 Million.
- **Write QPS:** 500,000.
- **Total Data:** Petabytes of graph structure metadata.

### Out of Scope

- Core user authentication pipelines.
- Heavy offline analytical graph processing (e.g., PageRank, global shortest path) - this system is for real-time transactional read/write workloads.
- Media storage (photos/videos) - the graph stores metadata and pointers to blob storage.

---

## High-Level Design Outline

### Core Components

- **Data Model:** Objects (Nodes) mapped to integer IDs; Associations (Edges) mapped as `(id1, atype, id2)`.
- **Cache Architecture:** Two-Tier Cache hierarchy (Leader/Follower).
    - **Follower Caches:** Serve the vast majority of read requests directly. Close to web tiers.
    - **Leader Caches:** Coordinate writes to the underlying DB and broadcast invalidations.
- **Storage Tier:** Horizontally sharded persistent storage (typically MySQL or similar RDBMS configured for high availability).
- **Asynchronous Invalidation:** A cache invalidation bus (Wormhole pattern) tailing DB binary logs to propagate cache updates/invalidations globally.
- **Sharding & Routing:** Supernode celebrity virtual bucket sharding (id1_hash % K) with parallel scatter-gather for aggregations.

### API Surface (Illustrative)

```http
// Object APIs
GET /api/v1/objects/{id}
POST /api/v1/objects
PUT /api/v1/objects/{id}
DELETE /api/v1/objects/{id}

// Association APIs
GET /api/v1/associations/{id1}/{atype}
POST /api/v1/associations
DELETE /api/v1/associations/{id1}/{atype}/{id2}

// Graph APIs
GET /api/v1/graph/mutual-friends/{id1}/{id2}
```

---

## Scoring Rubric

Strong answers explicitly cover:

1. Two-tier cache architecture balancing latency, hit rate, and connection overhead to databases.
2. Read-your-writes handling via synchronous local cache updates on write.
3. Supernode management (celebrity problem) using smart sharding and caching strategies.
4. Asynchronous, ordered cache invalidation (DB binlog tailing) across regions.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Designing a purely distributed KV store without edge-list optimizations (which destroys 2-hop traversal latency).
- Failing to handle the "thundering herd" problem on cache misses for popular objects.
- Attempting strict ACID transactions across multiple shards for edge creation.
- Using synchronous, blocking cache invalidations across regions.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How do you handle an association query that returns millions of edges (e.g., Lady Gaga's followers)?
- How do you handle disaster recovery and cross-region replication?
- What happens if the asynchronous invalidation bus lags behind?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
