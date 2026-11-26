# 🏆 Coach Answer: News Feed / Aggregated Feed — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional

1. Create or ingest content.
2. Build personalized/publisher feed.
3. Support cursor pagination and freshness.

### Non-Functional

| Metric | Target |
|---|---|
| Feed latency | < 200 ms P99 |
| Availability | 99.9% |
| Freshness | Seconds-level propagation |
| Consistency | Eventual acceptable |

### Variant Support

- Social follow-based feed.
- Publisher-aggregated news feed by region/topic.

---

## Phase 2 — Capacity (5 min)

- Very high read amplification relative to writes.
- Celebrity/publisher skew dominates tail behavior.
- Estimate fan-out impact before committing design.

---

## Phase 3 — APIs (5 min)

```http
POST /api/v1/posts
POST /api/v1/follows
GET /api/v1/feed?cursor=...&limit=...
GET /api/v1/feed/news?region=...&cursor=...
```

---

## Phase 4 — Data Model (5 min)

- `Post`/`Content` entities.
- Graph/subscription relationships.
- Feed materialization cache entries.
- Ranking metadata and engagement features.

---

## Phase 5 — Architecture (10 min)

- Write path: ingest -> queue -> fanout workers.
- Read path: cache-first feed retrieval + merge + ranking.
- Hybrid strategy: write fanout for normal accounts, read merge for high-follower sources.

---

## Phase 6 — Deep Dives (10 min)

1. Hybrid fanout thresholds and operations.
2. Pagination consistency under concurrent writes.
3. Ranking fallback when model service degrades.

---

## Phase 7 — Trade-Off Wrap (5 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Fanout strategy | Hybrid | Pure write/pure read | Handles skew while keeping latency low |
| Pagination | Cursor | Offset | Stable at high write velocity |
| Freshness | Eventual + bounded lag | Strong immediate consistency | Better availability and throughput |

### Follow-Up Extensions

1. Explore/trending feed.
2. Real-time push for active sessions.
3. Multi-feed tabs with independent ranking policies.

---

## Instagram Variant Notes

- Include media-heavy feed behavior and blob-delivery separation.
- Keep hybrid fan-out for creator skew.
- Add media derivative registration and CDN lifecycle mentions in deep dives.
