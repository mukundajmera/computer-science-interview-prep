# Architecture Comparisons

## Active-Active vs. Active-Passive

| Feature | Active-Active (Multi-Master) | Active-Passive (Single-Leader) |
|---|---|---|
| Write Latency | Low (local to region) | High for distant users |
| Consistency | Eventual / Causal | Strong (if sync replication) |
| Conflict Resolution | Complex (HLC, CRDTs) | Trivial (serialized at leader) |
| Failover Speed | Near-instant (traffic shift) | Slower (requires leader election) |
| Resource Utilization | High (all regions take writes) | Lower (passive region is mostly read or idle) |
