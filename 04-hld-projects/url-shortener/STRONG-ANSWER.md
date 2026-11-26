# URL Shortener — Model Answer (Time-Boxed)

Say: "I will optimize the redirect path for extremely low latency, while keeping short-code generation, abuse controls, and analytics out of the critical redirect path where possible."

A strong-answer outline for a 40-minute URL Shortener system design interview. Each section includes target timing and the key points an interviewer expects to hear.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## ⏱️ Time Allocation

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Requirements & Clarification | 5 min | Scope the problem |
| 2. Estimation | 5 min | Quantify scale |
| 3. API + Data Model + High-Level Design | 10 min | Core architecture |
| 4. Deep Dives | 15 min | Key technical challenges |
| 5. Trade-offs & Wrap-up | 5 min | Justify decisions, summarize |

---

## Phase 1 — Requirements & Clarification (5 min)

### Clarifying Questions to Ask

1. "What's the expected scale — URL creations per day and redirects per day?"
2. "Should the same long URL always produce the same short URL, or a new one each time?"
3. "Do we need custom aliases?"
4. "What analytics are required — just click counts or breakdowns by geography/device?"
5. "Should URLs expire? What's the default retention?"
6. "What's the acceptable latency for redirects?"

### Functional Requirements (confirm with interviewer)

- **Core:** Shorten a long URL → unique 7-character short code; redirect short URL → original URL.
- **Optional:** Custom aliases, link expiration, basic click analytics.

### Non-Functional Requirements (state explicitly)

- **Availability:** 99.99% — this is a read-heavy service; downtime means broken links everywhere.
- **Latency:** < 100 ms for redirects, < 200 ms for creation.
- **Read/Write ratio:** 100:1 — overwhelmingly reads (redirects).
- **Durability:** Once a URL is created, it must never be lost.
- **Consistency:** Eventually consistent is acceptable (a new URL can take a few seconds to propagate).

### Scope Boundaries

- **In scope:** Shortening, redirect, custom alias, expiration, basic analytics.
- **Out of scope:** Spam/malware detection, authentication system, payment tiers.

---

## Phase 2 — Estimation (5 min)

### Traffic

```
Writes:  100M URLs/month ÷ (30 × 86,400) ≈ 40 URLs/sec (peak ~120/sec)
Reads:   10B redirects/month ÷ (30 × 86,400) ≈ 4,000 req/sec (peak ~12,000/sec)
Ratio:   100:1 read-heavy
```

### Storage (5-year horizon)

```
Total URLs:    100M/month × 60 months = 6 billion
Per record:    ~160 bytes (short_code 7B + long_url 100B + metadata 53B)
Raw storage:   6B × 160B ≈ 960 GB ≈ 1 TB
With indexes:  ~3–5 TB
```

### Cache

```
Hot set:       10 million URLs (covers top-accessed entries)
Memory:        10M × 160B ≈ 1.6 GB (easily fits in Redis)
Target hit rate: 80%+ to keep DB load manageable
```

### Key Space

```
Base62 with 7 characters: 62⁷ = 3.5 trillion unique codes
Need only 6 billion over 5 years — enormous headroom
```

---

## Phase 3 — API + Data Model + High-Level Design (10 min)

### API Endpoints

| Method | Endpoint | Purpose | Key Response |
|--------|----------|---------|--------------|
| `POST` | `/api/v1/urls` | Create short URL | `201` with `shortUrl`, `shortCode` |
| `GET` | `/{shortCode}` | Redirect | `301` with `Location` header |
| `GET` | `/api/v1/urls/{shortCode}/stats` | Analytics | `200` with click count |
| `DELETE` | `/api/v1/urls/{shortCode}` | Remove URL | `204` No Content |

**Error codes to mention:** `400` (bad URL), `404` (not found), `409` (alias taken), `410` (expired), `429` (rate limited).

### Data Model

```
Table: urls
─────────────────────────────────────────
short_code   STRING   (Partition Key)
long_url     STRING
created_at   TIMESTAMP
expires_at   TIMESTAMP  (nullable)
user_id      STRING     (nullable)
click_count  NUMBER
is_custom    BOOLEAN
```

- **Database choice:** NoSQL (DynamoDB/Cassandra) — simple key-value lookups, no joins, horizontal scaling.
- **Index:** GSI on `user_id` for listing a user's URLs.
- **Cache:** Redis — key = `short_code`, value = `long_url`, TTL = 24 hours.

### High-Level Architecture

```
Clients → CDN (edge-cached redirects)
       → Load Balancer (L7, rate limiting)
       → Stateless API Servers (N instances)
            ├→ Redis Cache (read-through, LRU)
            ├→ Key Generation Service (pre-generated codes)
            ├→ NoSQL Database (sharded by short_code)
            └→ Kafka → Analytics Aggregator → Analytics DB
```

**Read path:** Client → CDN (hit?) → LB → API → Redis (hit?) → DB → cache result → return 301.

**Write path:** Client → LB → API → validate → get key from KGS → write DB → populate cache → return 201.

---

## Phase 4 — Deep Dives (15 min)

### 4a. Unique Key Generation (~4 min)

Present three options and recommend one:

| Strategy | How It Works | Pros | Cons |
|----------|-------------|------|------|
| **Counter + Base62** | Auto-increment counter → convert to base62 | Guaranteed unique, compact | Single point of failure, sequential codes predictable |
| **Hash (MD5/SHA)** | `hash(longUrl + salt)`, take first 7 chars | No coordination needed | Collisions possible, need retry logic |
| **Pre-generated KGS** ✅ | Separate service pre-generates millions of 7-char codes; API servers fetch batches | Fast (no collision check at write time), distributed | Must manage key pool; KGS is an extra service |

**Recommendation:** KGS with batch allocation.
- KGS pre-generates keys into a `key_pool` table (unused keys).
- Each API server requests a batch of 1,000 keys and caches them locally.
- When a key is allocated, KGS marks it `used` atomically.
- If an API server crashes, its unused keys are simply lost — negligible waste given 3.5T total.

### 4b. Caching Strategy with Redis (~4 min)

**Pattern:** Cache-aside (lazy loading).

```
Read:
  1. GET short_code from Redis
  2. Cache MISS → query DB → SET into Redis with 24h TTL
  3. Return long_url

Write:
  1. Insert into DB
  2. SET into Redis (write-through for immediate availability)
```

**Configuration:**
- Eviction: LRU when memory limit is reached.
- TTL: 24 hours (general URLs); no TTL for the top ~1,000 most-accessed URLs.
- Cluster: 3 masters + 3 replicas for high availability.

**Why this matters:** With an 80%+ cache hit rate, only ~800 reads/sec hit the database instead of 4,000.

### 4c. Database Choice & Sharding (~4 min)

**Why NoSQL (DynamoDB/Cassandra):**
- Access pattern is single-key lookups (`short_code → long_url`) — no joins, no complex queries.
- Horizontal scaling via consistent hashing built in.
- Eventually consistent reads are acceptable for this use case.

**Sharding:**
```
shard_id = hash(short_code) % num_shards
```
- Random short codes distribute evenly — no hot partitions.
- Start with 10 shards; add more by rebalancing (consistent hashing minimizes data movement).

**Replication:** 3 replicas per shard, quorum writes (2/3), single-replica reads for speed.

### 4d. Handling Hot URLs (~3 min)

**Problem:** A viral link (e.g., trending tweet) might receive millions of requests per minute, overwhelming a single cache node or DB shard.

**Layered mitigation:**

| Layer | Mechanism | Effect |
|-------|-----------|--------|
| **CDN** | Cache the 301 redirect at edge PoPs | Absorbs the majority of traffic before it reaches origin |
| **Redis replicas** | Replicate hot keys across multiple read replicas | Spreads load across nodes |
| **Local cache** | API servers keep an in-memory LRU cache (TTL ~60 sec) | Eliminates even the Redis round-trip for the hottest keys |
| **Rate limiting** | Per-IP rate limits on redirect endpoint | Prevents bot-driven abuse of a single URL |

---

## Phase 5 — Trade-offs & Wrap-up (5 min)

### Key Trade-offs to Surface

| Decision | Choice | Trade-off |
|----------|--------|-----------|
| Consistency vs Availability | AP (availability) | A newly created URL may take seconds to propagate; acceptable |
| 301 vs 302 redirect | 301 by default | Better performance (browser caches), but analytics misses repeat visits; make configurable |
| Pre-generated keys vs on-demand | KGS | Extra service to manage, but eliminates write-time collisions |
| NoSQL vs SQL | NoSQL | Gives up complex queries and ACID transactions; gains horizontal scale |
| CDN caching redirects | Yes | Reduces origin load dramatically; trade-off is stale redirects if a URL is updated (rare) |

### Evolution Narrative

| Version | What Changes | Handles |
|---------|-------------|---------|
| **v1-basic** | Single server, single DB, counter-based IDs | ~100 req/s |
| **v2-scaled** | LB + multiple API servers, Redis cache, KGS, read replicas | ~10K req/s |
| **v3-distributed** | CDN, sharded DB, multi-region active-active, Kafka analytics | ~1M req/s globally |

### Closing Statement (say this to the interviewer)

> "To summarize: we've designed a read-heavy URL shortener with a 100:1 read/write ratio. The core path is CDN → cache → sharded NoSQL. We use a dedicated Key Generation Service for collision-free short codes, Redis for sub-millisecond redirects, and a Kafka pipeline for async analytics. The main trade-off is choosing availability over strict consistency, which is appropriate since a short delay in URL propagation is acceptable. The system scales from a single server MVP to a globally distributed service handling millions of requests per second."

---

*See [RUBRIC](./RUBRIC.md) for how this answer maps to scoring criteria, and [PITFALLS](./PITFALLS.md) for common mistakes to avoid.*
