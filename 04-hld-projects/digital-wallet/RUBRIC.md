# Digital Wallet & Transactional Ledger - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
|---|---|---|
| **Requirements** | 15% | Identifies strict consistency as paramount. Computes scale limits (e.g., why standard RDBMS won't hit 50k peak TPS) and deduces the need for event sourcing and sharding. |
| **Data Model** | 20% | Designs immutable ledger tables. Enforces double-entry bookkeeping constraints and explicitly separates "balance" from "held_balance" to handle asynchronous transaction phases. |
| **Transaction Strategy** | 30% | Deeply understands the failure modes of 2PC. Explicitly designs a symmetrical Saga or TC/C pattern with a strong inconsistency guard (both TRYs must succeed before any CONFIRM). |
| **Scalability & Sharding** | 20% | Explains Raft consensus for partition fault tolerance. Describes how to shard accounts while maintaining localized ACID properties where possible. |
| **Auditability & Replay** | 15% | Articulates how the Write-Ahead Log is the source of truth, allowing state machines to be rebuilt seamlessly in the event of corruption. |

## Performance bands

- **Hire:** The candidate immediately recognizes the distributed lock contention problem at 50k peak TPS. They propose a sharded event-sourcing or TC/C architecture, successfully walking through partial failure scenarios (e.g., node crash between TRY and CONFIRM).
- **No Hire:** The candidate assumes a single RDBMS can handle the load using standard transactions, or they design an eventually consistent system that is prone to double-spending or money creation.

## Cross-links
- [Problem](PROBLEM.md)
- [Design](DESIGN.md)
