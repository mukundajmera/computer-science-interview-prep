# Distributed Social Graph Engine - High-Level Design

## 1. System Architecture

The system is built on a Two-Tier Cache architecture backed by a horizontally sharded relational database, deeply integrated with an asynchronous replication and invalidation bus.

### Core Components

1. **Web Tier / API Gateway:** Handles client requests, authentication, and routing.
2. **Follower Caches (L1):** 
   - Deployed alongside web servers.
   - Serve 99% of read requests directly from RAM.
   - Do not connect to databases.
   - Route cache misses and all writes to the Leader Cache.
3. **Leader Caches (L2):** 
   - One Leader cluster per database shard per region.
   - Acts as a reverse proxy for the DB.
   - Collapses concurrent cache misses (solves Thundering Herd).
   - Coordinates writes to the DB.
4. **Persistent Storage (DB Tier):**
   - Horizontally sharded MySQL (or similar RDBMS).
   - Sharded primarily by `id1` (the origin node of an edge).
5. **Asynchronous Invalidation Bus (Wormhole):**
   - Tails the DB binary logs (binlogs).
   - Publishes state changes to a message broker (e.g., Kafka).
   - Follower caches subscribe to these streams to invalidate or update stale data.

## 2. Data Model

The data model strictly abstracts everything into Objects and Associations.

### Objects (Nodes)
Represent entities (Users, Posts, Comments, Pages).
- `id`: 64-bit globally unique integer.
- `otype`: Object type (e.g., USER, POST).
- `data`: Key-value payload (usually JSON).

### Associations (Directed Edges)
Represent relationships (Friendships, Likes, Authorship).
- `id1`: Origin Object ID.
- `atype`: Association type (e.g., LIKES, FRIEND_OF).
- `id2`: Destination Object ID.
- `time`: 32-bit timestamp (used for ordering edge lists).
- `data`: Optional edge payload.

*Note: Bidirectional relationships (like Friendship) are modeled as two separate directed edges: `(A, FRIEND, B)` and `(B, FRIEND, A)`.*

## 3. Storage Schema & Sharding

We use a relational database for persistent storage due to its durability, secondary index capabilities, and mature replication tools (binlog).

**Objects Table:**
```sql
CREATE TABLE objects (
    id BIGINT PRIMARY KEY,
    otype INT NOT NULL,
    data BLOB
);
```

**Associations Table:**
```sql
CREATE TABLE associations (
    id1 BIGINT,
    atype INT,
    id2 BIGINT,
    time INT,
    data BLOB,
    PRIMARY KEY (id1, atype, id2),
    INDEX (id1, atype, time DESC) -- Crucial for fetching recent edges
);
```

### Sharding Strategy
- The primary sharding key is `id1`.
- All objects and their outgoing associations reside on the same logical shard.
- `Shard_ID = hash(id) % Total_Shards`.
- This ensures that fetching an object and its immediate outgoing edges is a single-shard operation.

## 4. The Two-Tier Cache & Request Flow

### Read Flow (Cache Hit)
1. Web server queries Follower Cache for `(id1, atype)`.
2. Follower returns the cached association list (usually just the top N most recent edges).

### Read Flow (Cache Miss)
1. Web server queries Follower. Miss.
2. Follower forwards query to the designated Leader Cache for `id1`'s shard.
3. If Leader has it, it returns to Follower.
4. If Leader misses, Leader queries the DB.
   - *Optimization:* If 10,000 followers ask the leader for the same edge simultaneously, the Leader collapses these into a *single* DB query (Request Collapsing).
5. DB returns to Leader. Leader caches it. Leader returns to Follower. Follower caches it.

### Write Flow (e.g., User A likes Post B)
1. Web server sends `add_association(UserA, LIKES, PostB)` to Follower Cache.
2. Follower forwards to Leader Cache.
3. Leader writes synchronously to the DB shard.
4. DB confirms write.
5. Leader updates its own cache and returns success to the Follower.
6. Follower updates its local cache (Read-Your-Writes consistency for User A).
7. Background: DB Binlog is tailed. An invalidation message `(UserA, LIKES, PostB)` is broadcast.
8. Other Followers holding stale lists for `UserA` process the message and update/invalidate their caches.

## 5. Handling Supernodes (The Celebrity Problem)

When `id1` is a celebrity (e.g., 100 million followers), storing the `(id1, FOLLOWER, *)` edge list on a single shard creates a severe hotspot.

### Solution: Edge Sharding / Virtual Buckets
Instead of sharding purely by `id1`, we partition the association list itself for massive nodes.
- **Normal nodes:** `Shard_ID = hash(id1) % K`.
- **Supernodes:** The association list is split across $M$ virtual buckets.
  - Bucket placement: `hash(id1, id2) % M`.
- **Writes:** To add a follower, we hash `(CelebrityID, FollowerID)` to find the correct bucket, and write to that specific shard.
- **Reads (Point Lookup):** "Does UserX follow Celebrity?" -> Hash `(CelebrityID, UserX)` -> Query specific shard. $O(1)$.
- **Reads (Scatter-Gather):** "Get 50 random followers of Celebrity" -> The Leader sends parallel queries to all $M$ shards, merges the results, and returns them.

## 6. Back-of-the-Envelope Calculations

### Throughput
- Read QPS: 10,000,000
- Write QPS: 500,000

### Storage (Graph Metadata only)
- Objects: 3 Billion users * ~1KB data = 3 TB.
- Associations: 10 Trillion edges.
  - Each edge row is roughly 40 bytes (`id1`(8), `atype`(4), `id2`(8), `time`(4), overhead).
  - Total Edge Storage = 10 Trillion * 40 bytes = 400 TB.
- **Total DB Storage needed:** ~400 TB (pre-replication).

### Network Bandwidth
- Assuming average read response is 1KB (fetching top 10 edges).
- 10M QPS * 1KB = 10 GB/sec = 80 Gbps. (Easily handled by a distributed Follower tier).

## 7. API Design

### Internal Graph API
Used by web tier to communicate with Follower caches.

```protobuf
// Objects
Object obj_get(int64 id);
Object obj_add(int otype, bytes data);
void obj_update(int64 id, bytes data);
void obj_delete(int64 id);

// Associations
void assoc_add(int64 id1, int atype, int64 id2, int32 time, bytes data);
void assoc_delete(int64 id1, int atype, int64 id2);

// Traversals
// Returns up to 'limit' associations of 'atype' originating from 'id1'
AssociationList assoc_get(int64 id1, int atype, int high_time, int low_time, int limit);

// Counts
int assoc_count(int64 id1, int atype);
```

## 8. Cross-Region Replication

For global availability:
1. **Primary Region:** Holds the DB Masters.
2. **Replica Regions:** Hold DB Read Replicas, plus their own complete tier of Followers and Leaders.
3. **Writes in Replica Regions:** Followers in Region B forward writes to the Leader in Region B. The Leader in Region B *forwards the write cross-region* to the DB Master in Region A.
4. **Replication:** DB Master (Region A) asynchronously replicates to DB Replicas (Region B).
5. **Invalidation:** The Invalidation Bus (Wormhole) handles propagating cache updates from the local DB replicas to the local Follower caches.

## 9. Cross-Links
- [PROBLEM.md](./PROBLEM.md)
- [APPROACH.md](./APPROACH.md)
- [diagrams/architecture.mmd](./diagrams/architecture.mmd)

---
**Real-world reference**: See how LinkedIn solved this in the [LinkedIn case study](../../case-studies/linkedin-feed/)
