# Distributed Cache — Strong Interview Answer (45 Minutes)

Say: "I will first define the consistency and eviction expectations, then choose sharding, replication, and failure behavior that keep hot reads fast without hiding stale-data risk."

## 0-5 min: Requirements
- Lock scope to get/set/delete, TTL, LRU.
- Confirm availability and latency priority with eventual consistency tolerance.

## 5-10 min: Estimates
- Convert 100K req/s and 1 TB data into per-node requirements.
- Size cluster by larger of memory-driven and throughput-driven calculations.

## 10-15 min: API + Entities
- Show key-value API with TTL semantics.
- Define entry, membership, and assignment entities.

## 15-30 min: Architecture
- Draw consistent-hash routing, replication, and membership updates.
- Explain failover and rebalance path.

## 30-40 min: Deep Dives
1. Hot-key mitigation.
2. Safe rebalance strategy.
3. Backend protection during cache outages.

## 40-45 min: Trade-offs + Wrap
- Chosen now: eventual consistency with replication for availability.
- Revisit trigger: tail latency/miss-rate regression during node churn.
