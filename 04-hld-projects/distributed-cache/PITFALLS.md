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

## 8. Ignoring Cache Stampedes When Popular Keys Expire
When a hot key's TTL expires under 100K QPS, thousands of concurrent misses bypass the cache and hammer the primary database simultaneously. Combine probabilistic early refresh (XFetch), process-local request coalescing (singleflight), and short-TTL distributed leases so only one caller recomputes the value.

## 9. Sizing Cluster RAM From Raw Logical Data Without Allocator Overhead
Estimating node count from the 1 TB logical working set alone ignores key/metadata bytes, jemalloc bin rounding (1094 B rounded to 1280 B), OS headroom, and R=3 replication, leading to premature eviction storms. Compute physical capacity from measured allocator entry sizes (~1.28 TB) and size both RAM (~50 GB usable per 64 GB node) and NIC offered load separately from successful QPS.

## 10. Assuming Synchronous Quorum Replication for Sub-Millisecond Caching
Requiring synchronous cross-node consensus on every `SET` violates the <10 ms P99 end-to-end SLO and couples write availability to replica latency. Use asynchronous primary-to-replica replication, accept at-most-once write durability on primary crash, and hedge read requests to replicas only when tail latency spikes.

## 11. Using Pure LRU Without Guarding Against Scan Poisoning
A single batch scan or cold backfill evicts the hot working set from a pure LRU cache, collapsing the 95% target hit ratio. Prefer frequency-aware eviction such as W-TinyLFU (with a Count-Min Sketch) alongside TTLs so one-off scans do not displace frequently accessed keys.

## 12. Ignoring Lock Contention in Multi-Threaded Cache Execution or Unfenced Skew
Sharing a global hash table across worker threads with coarse locks degrades throughput well before NIC limits, while unverified virtual-node counts can leave key skew across shards. Adopt Redis 6+ multi-threaded I/O with single-threaded command execution and empirically validate vnode counts (150–250) against staging key skew.

---

## Quick Self-Check

- Did I explain routing under node changes?
- Did I include hot-key and rebalance controls?
- Did I define cache-miss fallback under failures?
- Did I prevent cache stampedes using XFetch, singleflight, or distributed leases?
- Did I account for allocator overhead, OS headroom, replication (R=3), and offered-load NIC sizing?
- Did I explicitly justify async replication and eventual consistency for sub-10 ms P99 latency?
- Did I address scan poisoning with frequency-aware eviction (e.g., W-TinyLFU) instead of pure LRU?
- Did I explain threading/lock-contention trade-offs and empirical vnode skew tuning?
