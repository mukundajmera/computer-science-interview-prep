# 🏆 Coach Answer: URL Shortener — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional

1. Create short URL from long URL.
2. Redirect short URL to original URL.
3. Optional alias and expiry.
4. Basic click analytics.

### Non-Functional

| Metric | Target |
|---|---|
| Redirect latency | < 100 ms P99 |
| Create latency | < 200 ms P99 |
| Availability | 99.99% |
| Read:Write | ~100:1 |

### Out of Scope

- Advanced abuse/scam detection internals.
- Full campaign analytics suite.

---

## Phase 2 — Capacity (5 min)

- 100M links/month -> ~40 writes/sec average.
- 10B redirects/month -> ~4K reads/sec average (peak 3-5x).
- At 500 bytes/record and 5-year retention, storage remains manageable in TB range.

---

## Phase 3 — APIs (5 min)

```http
POST /api/v1/urls
GET /{shortCode}
GET /api/v1/urls/{shortCode}/stats
```

Add idempotency key for creation retries and clear alias conflict response (`409`).

---

## Phase 4 — Data Model (5 min)

Primary mapping table:

- `short_code` (PK)
- `long_url`
- `created_at`, `expires_at`, `status`
- `owner_id` (optional)

Analytics events are stored separately via async pipeline.

---

## Phase 5 — Architecture (10 min)

- API Gateway + rate limiter.
- URL Create Service.
- Redirect Service with cache-first lookup.
- NoSQL/KV primary mapping store.
- Event stream -> analytics workers -> analytics store.

Redirect path must not block on analytics writes.

---

## Phase 6 — Deep Dives (10 min)

1. **Key generation:** Range-allocated monotonic IDs + base62 to avoid collisions.
2. **Hot links:** Cache replication/local fallback for viral keys.
3. **Multi-region:** Region-partitioned key space + async replication.

---

## Phase 7 — Trade-Off Wrap (5 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Key generation | Range + base62 | Pure random | Predictable uniqueness under scale |
| Analytics path | Async events | Inline writes | Keeps redirect latency stable |
| Alias support | Optional, conflict-checked | No aliases | Product flexibility |

### Follow-Up Extensions

1. Vanity domains per tenant.
2. Deterministic shorten mode for same URL.
3. Security interstitial for flagged destinations.
