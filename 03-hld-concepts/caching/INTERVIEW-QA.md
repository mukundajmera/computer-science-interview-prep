# Interview Questions: Caching

## Core questions

### 1) When should you introduce caching?
Introduce caching after identifying a concrete read or compute bottleneck (latency, CPU, or QPS pressure), not by default.

### 2) Which cache pattern is the default in interviews?
Cache-aside is usually the safest default because it keeps source-of-truth in the primary store and avoids mandatory cache coupling.

### 3) How do you choose TTL?
Use business freshness tolerance + update frequency + failure risk. Shorter TTL for correctness-sensitive data, longer TTL for stable high-reuse data.

### 4) How do you prevent cache stampede?
Use request coalescing/single-flight, jittered TTL, and proactive refresh for top hot keys.

### 5) What is your fallback when cache is down?
Protect the source store with circuit breakers, admission control, and possibly degraded responses to avoid cascading failure.

## Scenario questions

### 6) A single hot key overloads one Redis shard. What do you do?
Replicate/bucket hot keys, add in-process fallback cache, and rate-limit abusive traffic paths.

### 7) How do you keep cache and DB consistent on writes?
Typical approach: write DB first, then invalidate cache key. For stricter guarantees, consider write-through with careful failure semantics.

### 8) When is write-behind acceptable?
For analytics/event pipelines where eventual persistence is acceptable and throughput is prioritized over immediate durability.

### 9) What metrics prove cache health?
Hit ratio, miss penalty latency, eviction rate, hot-key skew, backend offload percentage, and error/fallback rate.

### 10) Why not cache every endpoint?
Low reuse and highly volatile data can add invalidation complexity without meaningful latency gain.

---

## Requirements and constraints

- Answers should state cache boundary, key format, and invalidation trigger.
- Must include one failure-path defense for outages.
- Must quantify expected backend offload or latency improvement.
- Must state stale-read tolerance explicitly.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Bottleneck reasoning | Uses concrete traffic/latency argument | "Caching is always faster" |
| Correctness | Explains stale/read-after-write behavior | Ignores consistency implications |
| Resilience | Includes outage and stampede handling | No failure path |
| Operability | Mentions metrics and tuning loop | No observability plan |

## Common pitfalls

- Equating high hit-rate with correctness.
- Ignoring cache-key cardinality and namespace design.
- Missing fallback limits when cache tier fails.
- Conflating TTL with invalidation strategy.

## Follow-up questions

- How would this cache design change at 10x QPS?
- Which endpoints should bypass cache?
- How do you do safe key migration with zero downtime?

## Variants and extensions

- CDN + service cache split by content type.
- Tenant-aware cache partitions.
- Regional cache topology for global products.
- Consistent-hash ring rebalancing with bounded key migration windows.

## Related concepts

- [Caching Theory](./THEORY.md)
- [Redis](../redis/)
- [CDN](../cdn/)
- [API Gateway](../api-gateway/)
- [URL Shortener HLD](../../04-hld-projects/url-shortener/)
- [Distributed Cache HLD](../../04-hld-projects/distributed-cache/)
