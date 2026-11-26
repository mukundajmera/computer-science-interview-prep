# Real-Time Gaming Leaderboard - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|---|---|---|
| Requirements & Constraints | 15% | Actively identifies the need for tie-breakers (timestamp). Asks about tournament lifecycle and archiving requirements. |
| Memory & Sizing Estimation | 15% | Correctly estimates memory footprint for Redis (including SkipList overhead). Identifies when a single node becomes bottlenecked by memory or QPS. |
| Architecture & Read/Write Paths | 25% | Cleary separates the fast in-memory path (Redis) from the durable path (MySQL/Kafka). Addresses how to rebuild Redis in case of failure. |
| Data Structures & Deep Dives | 25% | Explains *how* a Sorted Set works (SkipList + Hash map). Proposes a mathematical solution for composite scores to handle tie-breakers. Understands score-range sharding vs hash sharding. |
| Trade-offs & Communication | 20% | Clearly articulates why RDBMS is rejected for read paths. Explains the downside of score-range sharding (hotspots) and proposes mitigations. |

## Performance Bands

### 1 - Needs Improvement (Weak)
- Proposes a purely relational database solution (e.g., `SELECT COUNT(*) WHERE score > X`) and fails to recognize the $O(N)$ performance bottleneck.
- Uses Redis but does not account for durability, leaving the system vulnerable to catastrophic data loss.
- Ignores the tie-breaker requirement entirely.

### 3 - Meets Expectations (Solid)
- Chooses Redis Sorted Sets as the primary engine.
- Implements an async write path to a durable store (MySQL) for recovery.
- Recognizes the memory limits of a single node but struggles to articulate a viable sharding strategy for 500M users.
- Addresses the tie-breaker using a composite score but may fumble the exact floating-point math implementation.

### 5 - Exceeds Expectations (Strong)
- Clearly outlines the memory vs. compute limitations of a single Redis instance using precise math (e.g., 2.5x pointer overhead).
- Articulates a clear score-range sharding strategy for massive scale, including how to dynamically rebalance hot score buckets.
- Explains the exact mathematical composition of the Redis 64-bit float score to guarantee strictly monotonic timestamp tie-breakers.
- Proposes a robust rebuild mechanism for Redis using the Kafka offset and MySQL state.

## 🔗 Cross-links
- [Problem Statement](PROBLEM.md)
- [Design](DESIGN.md)
- [Pitfalls](PITFALLS.md)
