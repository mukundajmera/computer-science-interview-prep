# Digital Wallet & Transactional Ledger - Comparison

## Architectural Approaches

| Concern | 2-Phase Commit (2PC) | Sagas / TC/C with Event Sourcing |
|---|---|---|
| **Consistency** | Strict ACID via database engine | Strong (Raft) at shard level, eventual across shards during flight |
| **Throughput Capacity** | Low (< 1,000 TPS) | Massive (50,000+ TPS via partitioning) |
| **Locking Mechanism** | Distributed database locks | Application-level holds (`held_balance`) |
| **Failure Handling** | Managed by DB transaction manager | Managed by application orchestrator / state machine |
| **Auditability** | Poor (unless CDC is heavily configured) | Perfect (immutable WAL is native) |

## Related Systems

| System | Similarity | Key difference |
|---|---|---|
| **E-commerce Backend** | Handles payment intent and inventory deduction | E-commerce focuses on state machines for physical fulfillment; Wallet focuses purely on atomic financial ledger entries. |
| **Payment Gateway** | Routes money | Gateways mostly act as proxies to external networks (Visa/Mastercard); the Wallet is the internal authoritative ledger. |

## Migration / Reuse
- **Idempotency Store:** The idempotency layer designed here is directly reusable in any high-stakes transactional system (e.g., Ticket Booking, Ride Sharing payments).
- **Consensus Layer:** The Raft-partitioned RocksDB architecture can be generalized to build high-throughput distributed message queues or key-value stores.

## Cross-links
- [Problem](PROBLEM.md)
- [Design](DESIGN.md)
