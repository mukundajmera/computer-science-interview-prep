# Distributed Cache — Interview Approach

## 1. Clarify Cache Scope

- Confirm cache is not a source-of-truth datastore.
- Lock core operations: set/get/delete + TTL.
- Confirm eventual consistency tolerance and availability preference.

## 2. Estimate Throughput and Capacity

- Convert traffic assumptions to per-node load.
- Estimate node count from both QPS and memory constraints.
- Use the larger node estimate as capacity baseline.

## 3. Define Entities and Interfaces

- Entities: `CacheEntry`, `NodeMembership`, `ShardAssignment`.
- Interface contracts: routing, replication, eviction, health checks.

## 4. Architecture

- Consistent-hash-based routing.
- Replication strategy and failure behavior.
- Rebalancing and warmup flow on node add/remove.

## 5. Deep Dives

1. Hot-key mitigation.
2. Node failure and replica promotion.
3. TTL + eviction interaction and memory protection.

## 6. Wrap-Up

- Re-state availability-first posture and fallback behavior when cache nodes fail.
