# Caching

Caching stores high-reuse data in a fast tier to reduce latency and shield slower backends.

## What problem it solves

- Repeated reads on hot keys overload databases/services.
- Tail latency rises as backend utilization approaches saturation.
- Expensive computations are recomputed on every request.

## Recognition cues

Reach for caching when the interviewer says "hot reads," "expensive recomputation," "p95/p99 read latency," "protect the database," "serve global static content," or "many users repeatedly ask for the same object." Do not lead with Redis or CDN first; lead with the bottleneck, stale-read tolerance, and invalidation boundary.

## Concrete interview example

Suppose a product page serves `40K metadata reads/sec` at peak, while checkout correctness depends on source-of-truth price and inventory. Cache display metadata under `product:{id}:v3` with a `5 minute` TTL, but revalidate price and inventory during checkout/reservation or use a shorter explicitly invalidated cache for display-only hints. If metadata hit rate reaches `90%`, metadata reads to the database fall toward `4K/sec`, but correctness-sensitive price/inventory paths still need authoritative validation.

## Cache placement options

1. Client-side cache (browser/mobile/local SDK cache)
2. CDN edge cache for static and cacheable public content
3. Service-level distributed cache (Redis/Memcached)
4. In-process cache for extremely hot small objects

## Cache write/read patterns

- Cache-aside (default): app reads cache first, fills on miss.
- Write-through: writes update cache and backing store synchronously.
- Write-behind: writes acknowledged at cache, flushed asynchronously.
- Read-through: cache layer fetches source on miss.

## Eviction and expiry

- `LRU`: robust default for general workloads.
- `LFU`: better when popularity is stable over long windows.
- `TTL`: required freshness control; combine with LRU/LFU.

## Failure modes

- Stampede/thundering herd on synchronized expiry.
- Consistency gaps between cache and source-of-truth.
- Hot-key concentration overloading a single shard.

---

## Requirements and constraints

- Define cache ownership per data domain and explicit invalidation policy.
- Bound stale-read tolerance per endpoint class.
- Include fallback behavior when cache tier is degraded.
- Set memory budgets and eviction strategy upfront.

## Observability and rollout

Track hit ratio, miss penalty latency, backend offload percentage, eviction rate, hot-key skew, stale-read complaints, cache errors, and fallback rate. Roll out by endpoint or tenant, start with read-only cache-aside, add TTL jitter before launch, and keep a kill switch that bypasses cache without overloading the source store.

## Scoring rubric

| Dimension | Points | Strong signal | Weak signal |
|-----------|---:|---------------|-------------|
| Bottleneck framing | 5 | Quantifies read QPS, hit-rate target, miss penalty, and backend offload | Adds cache preemptively |
| Data classification | 4 | Separates display-only, correctness-sensitive, private, and global/static data | Uses one cache policy for everything |
| Pattern selection | 5 | Chooses cache-aside/write-through/read-through/write-behind by consistency need | Uses pattern names without reason |
| Freshness and invalidation | 5 | Defines TTL, jitter, explicit invalidation, versioned keys, and stale-read tolerance | No freshness policy |
| Failure handling | 6 | Covers stampede, hot key, cache outage, backend overload, and fallback mode | Ignores failure path |
| Capacity and sharding | 4 | Estimates memory budget, key size, eviction pressure, and shard hot spots | Assumes cache is infinite |
| Observability and rollout | 6 | Tracks hit ratio, miss latency, stale reads, evictions, hot-key skew, fallback rate, and kill-switch impact | Only monitors cache uptime |

Score out of `35`. A strong interview answer usually reaches `29+` because it ties the cache to a concrete bottleneck, an explicit freshness contract, and a failure plan.

## Common pitfalls

- Caching everything instead of high-reuse/high-cost paths.
- Using long TTL on correctness-sensitive data.
- Missing single-flight/request-coalescing for hot misses.
- Assuming high hit-rate forever without monitoring.

## Redis as Cache Implementation

For a concrete implementation of caching patterns, see [Redis](../redis/) which provides:

**Key features for caching:**
```
├─ In-memory data structures (strings, hashes, lists, sets)
├─ TTL (time-to-live) for automatic expiration
├─ LRU/LFU eviction policies
├─ Persistence options (RDB/AOF) for durability
└─ Cluster mode for horizontal scaling
```

**Common caching patterns with Redis:**

1. **Cache-Aside Pattern**
```python
# Check cache first
value = redis.get(cache_key)
if not value:
    # Cache miss - fetch from DB
    value = database.query(key)
    # Store in cache with TTL
    redis.setex(cache_key, ttl=300, value=value)
return value
```

2. **Session Storage**
```python
# Store user session
redis.setex(f"session:{session_id}", ttl=3600, value=session_data)

# Common fit: short-lived session or auth context with explicit expiry
```

3. **Rate Limiting**
```python
# Token bucket rate limiter
count = redis.incr(f"ratelimit:{user_id}:{window}")
if count == 1:
    redis.expire(f"ratelimit:{user_id}:{window}", window_seconds)

# Used for API rate limiting (see Rate Limiting concept)
```

4. **Leaderboards**
```python
# Sorted sets for rankings
redis.zadd("leaderboard", {player_id: score})
top_10 = redis.zrevrange("leaderboard", 0, 9, withscores=True)

# Common fit: ranked scores, counters, and real-time analytics views
```

**When to use Redis for caching:**
- Need low-latency reads from an in-memory shared tier
- Rich data structures beyond key-value
- Pub/sub messaging for cache invalidation
- Built-in atomic operations (INCR, DECR)
- Distributed caching with Redis Cluster

See [Redis](../redis/) for detailed deployment patterns, data structures, and production examples.

---

## Follow-up questions

- How do you prevent stampedes on top 1% keys?
- What is your stale-data budget for each endpoint type?
- How do you migrate cache key schema safely?
- What happens to DB load when cache is unavailable?

## 60-90 second answer

Say: "I would add caching only after naming the hot read or expensive compute path. First I define the cache boundary, key, TTL, and stale-read budget. For a product page, I might use cache-aside with Redis for metadata, short TTL or write invalidation for price/inventory, TTL jitter and single-flight to prevent stampedes, and a circuit breaker so a cache outage does not take down the database. I would judge the design by hit ratio, miss penalty, backend offload, eviction rate, hot-key skew, and stale-read incidents. The main trade-off is lower latency and lower database load in exchange for invalidation complexity and possible stale reads."

## Variants and extensions

- Stale-while-revalidate for low-latency read UX.
- Tiered caching (in-process + distributed + CDN).
- Per-tenant namespace isolation and quota-aware eviction.
- Distributed-cache cluster mode: consistent hashing, replica promotion, and progressive rebalance.

## 📊 Diagrams

- [Cache-aside read path](./diagrams/cache-aside-read-path.mmd) - the default read flow: check the cache first, and on a miss read the backing store, fill the cache with a TTL, then return.
- [Write-through vs write-behind](./diagrams/write-patterns-comparison.mmd) - compares the synchronous write-through path, acknowledged after both stores are updated, with the asynchronous write-behind path, acknowledged at the cache and flushed later.

## Related concepts

- [Redis](../redis/) - Primary implementation for distributed caching
- [CDN](../cdn/) - Edge caching for static content
- [Consistent Hashing](../consistent-hashing/) - Distributing cache across nodes (Redis Cluster)
- [Load Balancing](../load-balancing/) - Routing to cache nodes
- [Rate Limiting](../rate-limiting/) - Redis-based rate limiting patterns
- [Indexing Strategies](../../00-theory/database-concepts/indexing.md)
- [News Feed HLD](../../04-hld-projects/news-feed/)
- [Distributed Cache HLD](../../04-hld-projects/distributed-cache/)
