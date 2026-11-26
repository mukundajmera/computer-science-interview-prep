# Multi-Region Active-Active — Rubric

| Dimension | 1 (Weak) | 3 (Okay) | 5 (Strong) |
|---|---|---|---|
| Routing | Relies entirely on DNS. Doesn't handle DNS cache TTL issues during failover. | Uses GeoDNS and discusses failover latency. | Proposes Anycast BGP or edge PoP routing for immediate network-level failover. |
| Replication | Assumes database magically replicates. Mentions async but ignores conflict. | Proposes multi-master and mentions basic timestamps for conflict resolution. | Details CDC-based asynchronous multi-master replication with durable queues, explicitly defining CDC engine state ownership and exactly-once end-to-end guarantees. |
| Conflict Res | Doesn't understand split-brain or concurrent writes. | Uses NTP timestamps and acknowledges clock drift. | Clearly explains Hybrid Logical Clocks (HLC) or Vector Clocks to solve drift and causality. |
| Consistency | Ignores read-after-write anomalies during failover. | Mentions sticky sessions to pin users to a region. | Introduces client version tokens to guarantee read-after-write across any region. |
| Recovery | No plan for partition healing. | Suggests full data sync on recovery. | Describes anti-entropy mechanisms (Merkle trees) for efficient background reconciliation post-partition. |
