# Distributed Systems Architecture Rubric

Staff/Principal evaluation rubric for assessing distributed systems design capability.

---

## Scoring Dimensions

| Dimension | Weight | Strong signal |
| :--- | :--- | :--- |
| **Consensus Safety** | 20% | Demonstrates deep understanding of split-brain prevention, quorum mathematics, and log consistency (e.g., Raft/Paxos). Can map these to practical infrastructure choices (ZooKeeper/etcd/Consul). |
| **Transactional Correctness** | 20% | Correctly applies Saga (orchestration vs. choreography) and Outbox/CDC patterns to guarantee atomicity and eventual consistency without resorting to distributed locks or 2PC. |
| **Live Sharding** | 20% | Designs zero-downtime data migrations using consistent hashing, logical/virtual routing tiers, and dual-write/CDC strategies. |
| **Time & Ordering** | 20% | Avoids relying on wall-clock time for causality. Uses logical clocks, vector clocks, or specialized APIs (Spanner TrueTime) appropriately to resolve concurrent updates. |
| **Overload Protection** | 20% | Implements robust distributed rate limiting, backpressure, and shedding algorithms (Sliding Window, Token Bucket) considering coordination overhead and race conditions. |

---

## Performance Bands

### Strong Hire (5)
- **Consensus**: Anticipates network partitions. Articulates the exact quorum conditions required for both reads and writes to guarantee linearizability.
- **Transactions**: Designs idempotent compensating transactions natively. Identifies the "dual-write" problem immediately and solves it with Outbox/CDC.
- **Sharding**: Details the exact switchover mechanics of a live shard migration, handling in-flight transactions and replication lag.
- **Time**: Explains how clock skew affects distributed systems and correctly designs mechanisms to track causality (e.g., vector clocks) or linearizability (TrueTime commit wait).
- **Protection**: Chooses the correct rate limiting algorithm (e.g., Sliding Window Counter) and addresses the Redis centralization bottleneck (e.g., local bucketing + async sync).

### Hire (3)
- **Consensus**: Knows when a system requires consensus (e.g., leader election) and can name the tools (etcd, ZK), but may lack depth on internal mechanics (terms, log matching).
- **Transactions**: Understands the Saga pattern but may struggle with edge cases like orchestrator failure or non-idempotent compensations.
- **Sharding**: Suggests consistent hashing and understands the concept of virtual nodes, but may gloss over the complexities of zero-downtime migration.
- **Time**: Acknowledges NTP limitations but might initially suggest relying on timestamps for conflict resolution before being guided to logical clocks.
- **Protection**: Can implement a basic Redis rate limiter but might miss race conditions (requiring Lua) or the thundering herd problem.

### No Hire (1)
- **Consensus**: Assumes relational databases will automatically handle split-brain or suggests arbitrary tie-breaking mechanisms without quorums.
- **Transactions**: Defaults to Two-Phase Commit (2PC) or distributed locks for microservice communication. Does not recognize the dual-write problem.
- **Sharding**: Suggests manual modulo hashing and requires planned downtime for any topology changes.
- **Time**: Relies entirely on `System.currentTimeMillis()` for ordering distributed events and assumes perfect clock synchronization.
- **Protection**: Misses rate limiting entirely or designs a naive, highly contended database counter that will collapse under load.
