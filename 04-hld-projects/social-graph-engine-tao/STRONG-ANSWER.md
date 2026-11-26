# Distributed Social Graph Engine - Strong Candidate Response

This document provides an example of a strong candidate response for the Distributed Social Graph Engine problem. It demonstrates how to drive the design, justify architectural choices, and speak clearly to the interviewer.

---

## 1. Requirements & Data Model

> **Say:** "To handle 10 million read QPS and a 10 trillion edge graph with strict sub-5ms latencies, we cannot use a standard relational DB with complex `JOIN`s, nor can we use a generic Graph DB, which struggles to scale horizontally for simple, high-throughput queries. Instead, I'll design a system heavily optimized for shallow traversals using a constrained data model. Let's model everything as **Objects** (nodes) and **Associations** (directed edges). An object is just an ID and a type. An association is `(id1, atype, id2, timestamp)`. If Alice and Bob are friends, that's two associations: Alice->Bob and Bob->Alice."

## 2. The Two-Tier Cache Architecture

> **Say:** "Given the massive 20:1 read-to-write skew, this system will be entirely cache-driven. However, a standard look-aside cache where web servers query Redis, miss, and then query the DB will fail catastrophically here due to connection explosion and the Thundering Herd problem on hot keys. Therefore, I propose a **Two-Tier Cache** architecture acting as a reverse proxy."

**Candidate details the tiers:**
1. **Follower Caches (L1):** Deployed right next to the web servers. They hold the hottest objects and the most recent N edges for an association list. They serve 99% of reads and never talk to the DB.
2. **Leader Caches (L2):** One per DB shard. Followers send cache misses to the Leader. The Leader queries the DB.

> **Say:** "The critical benefit here is **Request Collapsing**. If Lady Gaga posts a photo and 10,000 followers' caches miss simultaneously, the Follower tiers forward this to the single Leader responsible for that photo. The Leader collapses these 10,000 requests into exactly *one* database query, caches the result, and fans it back out. This protects the DB from melting."

## 3. Storage and Sharding Strategy

> **Say:** "For persistent storage, I'll use horizontally sharded MySQL. It provides durability and excellent secondary indexing on the `timestamp` column, which we need for fetching recent edges."

**Candidate details sharding:**
- Data is sharded by `hash(id1) % Num_Shards`.
- This ensures an object and all of its outgoing associations live on the exact same physical DB node.

> **Say:** "This solves 99% of nodes. But what about supernodes? If an account has 100 million followers, the `(CelebrityID, FOLLOWED_BY, *)` edge list cannot fit on one shard, creating a massive write hotspot. To solve this, I'll use **Virtual Bucket Sharding** for the edge lists. Instead of sharding just by `id1`, we shard the associations by `hash(id1, id2) % K`. To read the list, the Leader cache issues a parallel scatter-gather query to all K shards, merges the results by timestamp, and returns them."

## 4. Consistency & Invalidation (The Write Path)

> **Say:** "We need high availability, so strict ACID across regions is out. We will use Eventual Consistency globally, but we must provide **Read-Your-Writes** locally so users don't get confused."

**Candidate walks through a write (Alice likes a Post):**
1. The web tier sends the write to the local Follower cache.
2. The Follower forwards it to the Leader.
3. The Leader synchronously writes to the DB.
4. Once the DB commits, the Leader updates its own cache and returns success.
5. The Follower immediately updates its cache.
> **Say:** "At this point, Alice sees her 'Like' immediately. But Bob, in another region, does not."

**Candidate details asynchronous invalidation:**
> **Say:** "To update everyone else without blocking the write path, we will tail the DB's binary log (binlog). A system like Kafka (or Meta's Wormhole) reads the binlog, packages the `(Alice, LIKES, Post)` event, and asynchronously broadcasts it to all other Follower caches globally so they can update their local edge lists."

## 5. Handling 2-Hop Traversals

> **Say:** "Let's bring it back to the core requirement: calculating Mutual Friends (a 2-hop BFS) in under 5ms. To find mutual friends between Alice and Bob:
> 1. The web server asks the Follower cache for Alice's friend list. (Usually an in-memory hit).
> 2. The web server asks the Follower cache for Bob's friend list. (Usually an in-memory hit).
> 3. The web server simply intersects the two lists in memory.
> Because the cache tier is so efficient and data is localized, this entire operation avoids complex DB joins entirely and completes in a millisecond."

## Cross-links
- [PROBLEM.md](./PROBLEM.md)
- [APPROACH.md](./APPROACH.md)
- [DESIGN.md](./DESIGN.md)
- [RUBRIC.md](./RUBRIC.md)