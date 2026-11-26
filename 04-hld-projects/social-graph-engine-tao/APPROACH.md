# Distributed Social Graph Engine - Approach & Alternatives

## 1. Defining the Problem Space

We need to build a distributed datastore explicitly optimized for social graph operations. The core challenges are:

- **Extreme Read Volume:** 10 Million QPS.
- **Low Latency Traversals:** 2-hop BFS traversals (like finding mutual friends) must complete in under 5ms (P99).
- **Celebrity Supernodes:** Highly skewed degree distribution. Some nodes have billions of edges (e.g., popular pages/celebrities).
- **High Read/Write Skew:** Reads outnumber writes by 20:1 up to 500:1.
- **Consistency vs. Availability:** Strict consistency is impossible at this scale while maintaining 5ms read latency. We need high availability with eventual consistency, but with strong "read-your-writes" guarantees for individual users.

## 2. Approach 1: Generic Graph Database (e.g., Neo4j, JanusGraph)

### Description
Use a fully-fledged graph database designed specifically for complex traversals and ACID transactions.

### Pros
- Deep traversals (N-hop) are natively supported and optimized.
- Rich query languages (Cypher, Gremlin).
- Built-in algorithms (shortest path, connected components).

### Cons
- **Scaling:** Scaling generic graph DBs horizontally (sharding) while maintaining high performance for random subgraphs is notoriously difficult. Cross-shard joins dominate latency.
- **Overkill:** We don't need complex graph algorithms. We only need fast point lookups and 1-2 hop neighbor lookups.
- **Write Latency:** Maintaining strict ACID properties across a heavily interconnected distributed graph severely impacts write throughput.

## 3. Approach 2: Memcached/Redis cluster in front of Sharded RDBMS (Look-aside)

### Description
A standard architecture where web servers explicitly query a distributed cache (Memcached/Redis) first. On a miss, they query the DB, compute the result, and populate the cache.

### Pros
- Simple, well-understood pattern.
- High read throughput.
- Easy to scale cache and DB independently.

### Cons
- **Thundering Herd:** If a celebrity's edge list gets evicted, thousands of concurrent requests will miss the cache and overwhelm the DB simultaneously.
- **Thick Clients:** Web servers need to know the complex caching logic, invalidation rules, and DB sharding scheme.
- **Edge List Mutations:** Adding one edge requires invalidating or doing a complex Read-Modify-Write on a large cached edge list, leading to race conditions.
- **Connection Explosion:** Every web server needs a connection to every cache node and every DB shard, leading to massive connection pool overhead at Meta scale.

## 4. Selected Approach: Specialized Graph API with 2-Tier Cache (Meta TAO Architecture)

### Description
A custom-built API and caching layer (TAO - The Associations and Objects) placed between the web tier and the persistent storage (MySQL). It abstracts the graph model (Objects and Associations) and handles caching, sharding, and consistency internally.

### Core Mechanisms:

1. **Object and Association Model:** Restrict the data model.
    - Objects: Typed nodes with IDs.
    - Associations: Typed, directed edges between two IDs `(id1, atype, id2)`, with a timestamp.

2. **Two-Tier Cache Hierarchy:**
    - **Follower Caches (L1):** Deployed close to web servers (same datacenter). They serve reads. They do NOT talk to the DB directly.
    - **Leader Caches (L2):** One per DB shard per region. Followers forward cache misses and all writes to the Leader. The Leader is the only component that talks to the DB.
    - **Why?** Eliminates the thundering herd problem. The Leader collapses concurrent misses for the same key into a single DB query. It also drastically reduces DB connection overhead (only Leaders connect to DBs).

3. **Write-Through via Leader:**
    - Writes go to Follower -> Leader -> DB.
    - Leader updates the DB synchronously. Once successful, the Leader updates its own cache and replies to the Follower.
    - Follower updates its local cache immediately (providing read-your-writes).
    - Asynchronous invalidations (via DB binlog tailing) update other Followers.

4. **Edge List Caching Optimization:**
    - Caches store "Association Lists" (e.g., all `LIKE` edges for `Post_ID`).
    - Instead of caching the entire list, cache the most recent N edges (since temporal locality is high in social feeds). If a query needs older edges, it falls back to the DB via the Leader.

5. **Supernode Sharding Strategy:**
    - A standard hash (`hash(id1) % Num_Shards`) works for objects.
    - For edges originating from a supernode (e.g., millions of followers), the association list on a single shard becomes a bottleneck.
    - Use **Virtual Bucket Sharding / Edge Sharding**: Partition the association list itself across multiple shards. E.g., `hash(id1, id2) % Num_Shards`. Reads for "all followers" require a parallel scatter-gather query to all shards holding fragments of that list.

## 5. Summary of the Chosen Strategy

By restricting the data model to simple Objects and Associations, we can optimize the cache layer specifically for graph operations (like fetching the most recent edges). The Two-Tier cache solves the connection explosion and thundering herd problems of naive look-aside caching. Asynchronous DB binlog tailing ensures eventual consistency without blocking writes.

This is the exact approach pioneered by Meta with TAO, successfully scaling to handle billions of users and trillions of edges.