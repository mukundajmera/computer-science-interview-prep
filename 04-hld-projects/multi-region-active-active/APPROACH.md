# Approach: Multi-Region Active-Active

## Interview flow (45-50 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify requirements | 5 min | Confirm regions, RTO/RPO expectations, and consistency needs. |
| Capacity estimation | 5 min | Traffic distribution, storage, replication bandwidth overhead, and tail-latency assumptions. |
| API + Data model | 10 min | Version vectors, vector clocks, or HLC timestamps in records. |
| Architecture | 15 min | GeoDNS/Anycast, Multi-master topology, replication queues. |
| Deep dives | 7 min | Conflict resolution (CRDTs/LWW-HLC), Split-brain fencing. |
| Wrap-up | 3 min | Failover automation, cross-region state reconciliation. |

## Suggested execution order

1. **Routing Layer:** Discuss how traffic enters the system. GeoDNS provides rough geographic routing, but Anycast BGP allows faster automated failover and more precise network-level routing.
2. **Replication Strategy:** Propose asynchronous multi-master replication to achieve low write latency. Acknowledge the trade-off: concurrent writes to the same key will conflict.
3. **Conflict Resolution Mechanism:** Choose Last-Write-Wins (LWW) with Hybrid Logical Clocks (HLC) for general data, or CRDTs for specific mergeable data structures (like counters or sets).
4. **Consistency Guarantees:** Implement read-after-write consistency using client-side version tokens or sticky session pinning to a "home" region.
5. **Partition Handling:** Explain how split-brain scenarios are handled using strict fencing or eventual consistency with background anti-entropy reconciliation.
