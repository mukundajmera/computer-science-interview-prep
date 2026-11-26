# Distributed Cache — Common Interview Pitfalls

## 1. Using Modulo Routing for Dynamic Clusters
Adding/removing nodes remaps most keys and causes large cache miss storms.

## 2. Treating Cache as Source of Truth
Cache data can be stale or evicted; strong business correctness should remain in backing stores.

## 3. No Hot-Key Strategy
One hot key can overload one shard even when average load looks healthy.

## 4. Ignoring Membership Propagation Lag
Routers using stale ring metadata create transient inconsistency and elevated miss rates.

## 5. No Controlled Rebalance
Bulk key movement during scale events creates latency spikes and backend amplification.

## 6. TTL and Eviction Ambiguity
Unclear precedence between expiry and memory eviction causes non-deterministic behavior.

## 7. No Failure-Degraded Mode
Without fallback behavior, cache outages cascade into backend overload.

---

## Quick Self-Check

- Did I explain routing under node changes?
- Did I include hot-key and rebalance controls?
- Did I define cache-miss fallback under failures?
