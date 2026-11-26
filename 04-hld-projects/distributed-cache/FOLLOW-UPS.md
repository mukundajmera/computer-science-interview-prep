# Distributed Cache — Follow-Up Questions

## 1. How do you handle hot read keys?
Apply adaptive replication, local in-process cache, and read throttling for abusive callers.

## 2. How do you handle hot write keys?
Use write coalescing, partitioned counters, or key bucketing where semantics allow.

## 3. How do you rebalance safely?
Move token ranges gradually with backpressure and miss-rate guardrails.

## 4. What if membership service is unavailable?
Freeze ring updates, continue with last-good metadata, and shorten router TTL.

## 5. How do you reduce tail latency in multi-tenant workloads?
Isolate noisy tenants with quotas and separate shard pools for critical tenants.

## 6. What changes for multi-region deployment?
Use read-local caches with asynchronous replication and region-aware invalidation policies.
