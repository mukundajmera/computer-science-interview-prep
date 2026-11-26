# 🏆 Coach Answer: Distributed Cache — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional

1. Set/get/delete key-value pairs.
2. Optional TTL.
3. LRU eviction.
4. Operations continue during node churn.

### Non-Functional

| Metric | Target |
|---|---|
| Latency | < 10ms P99 |
| Availability | 99.99% |
| Throughput | 100K+ req/s |
| Working set | ~1TB |

---

## Phase 2 — Capacity (5 min)

- Estimate nodes from both throughput and memory requirements.
- Use larger result + buffer as cluster baseline.

---

## Phase 3 — APIs (5 min)

```http
PUT /api/v1/cache/{key}
GET /api/v1/cache/{key}
DELETE /api/v1/cache/{key}
```

---

## Phase 4 — Data Model (5 min)

- `CacheEntry(key, value, expires_at, last_accessed)`
- `NodeMembership(node_id, state, last_heartbeat)`
- `ShardAssignment(token_range, primary, replicas)`

---

## Phase 5 — Architecture (10 min)

- Consistent-hash routing.
- Primary + replica writes.
- Controlled rebalance worker.

---

## Phase 6 — Deep Dives (10 min)

1. Hot-key mitigation strategies.
2. Node failure and replica promotion.
3. Rebalance with bounded miss amplification.

---

## Phase 7 — Trade-Off Wrap (5 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Routing | Consistent hashing | Modulo | Lower remap on node churn |
| Consistency | Eventual | Strong quorum | Better latency/availability |
| Eviction | LRU + TTL | LFU-only | Balanced default behavior |
