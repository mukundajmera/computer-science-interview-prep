# Distributed Social Graph Engine - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|---|---|---|
| **Data Modeling** | 15% | Explicitly defines Objects (nodes) and Associations (edges) with an optimal schema that avoids full RDBMS joins. Understands the importance of time-ordered edge lists. |
| **Caching Architecture** | 30% | Designs a Two-Tier Cache hierarchy. Clearly articulates the difference in responsibilities between Follower (read capacity) and Leader (DB protection, write coordination) caches. |
| **Thundering Herd Mitigation** | 15% | Uses the Leader cache to collapse concurrent DB requests for the same missing key into a single DB query. |
| **Consistency & Invalidation** | 20% | Designs a mechanism for Read-Your-Writes consistency (synchronous local cache update on write) combined with asynchronous global invalidation (DB binlog tailing). |
| **Supernode/Hotspot Handling** | 20% | Identifies the celebrity problem. Implements virtual bucket sharding / edge list partitioning and explains parallel scatter-gather reads for supernodes. |

---

## Performance Bands

### 🟢 Strong Hire
Candidate immediately recognizes the unsuitability of standard Graph DBs or naive Look-aside caches for this specific read/write ratio and latency requirement. They independently derive a TAO-like architecture, clearly separating the read-heavy Follower tier from the DB-protective Leader tier. They naturally address the "Thundering Herd" problem via request collapsing. They articulate a clean, asynchronous binlog-tailing invalidation strategy. They elegantly solve the supernode problem using edge partitioning without prompting.

### 🟡 Hire
Candidate designs a functional distributed graph system. They understand the need for heavy caching and DB sharding. They might start with a Look-aside cache but can be guided to understand connection explosion and thundering herd issues, eventually designing a reverse-proxy cache layer. They implement basic `id1` sharding but might need hints to handle the supernode hotspotting issue. Invalidation might rely heavily on synchronous TTLs rather than binlog tailing, but they understand the tradeoffs.

### 🟠 Weak Hire
Candidate proposes a generic distributed KV store or relational schema but struggles with graph traversal optimizations (e.g., retrieving time-ordered edge lists efficiently). They rely heavily on standard Memcached/Redis without addressing connection overhead or thundering herds. They struggle with eventual consistency implications and might attempt to use strict two-phase commits across shards, severely bottlenecking write throughput. They recognize supernodes as an issue but fail to provide a concrete sharding mitigation.

### 🔴 No Hire
Candidate attempts to use a single monolithic relational database with complex `JOIN`s, entirely ignoring the 10M QPS requirement. Alternatively, they propose a generic Graph DB but cannot explain how it scales horizontally. They fail to separate read and write paths or do not utilize caching effectively. They cannot articulate how a 2-hop traversal would be executed in their chosen architecture.

## Cross-links
- [PROBLEM.md](./PROBLEM.md)
- [DESIGN.md](./DESIGN.md)
- [PITFALLS.md](./PITFALLS.md)