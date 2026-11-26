# URL Shortener — Common Interview Pitfalls

The top 7 mistakes candidates make in a URL Shortener system design interview, why each is a problem, and what the interviewer actually expects.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## 1. Not Estimating Scale Properly

### ❌ The Mistake

Skipping back-of-envelope math or giving hand-wavy numbers like "lots of traffic." Failing to derive reads/sec, writes/sec, or storage from the monthly figures.

### 🎯 What the Interviewer Expects

- Convert 100M URLs/month → ~40 writes/sec, 10B redirects/month → ~4,000 reads/sec.
- Estimate peak traffic at 2–3× average.
- Compute 5-year storage (~1 TB raw, 3–5 TB with indexes).
- Size the cache: 10M entries ≈ 1.6 GB in Redis.
- Use these numbers to justify architecture decisions (e.g., "4,000 reads/sec is why we need a cache layer").

### 💡 Tip

Write the math on the whiteboard as you go. Interviewers value the *process* of estimation as much as the result. Round aggressively — `30 days × 86,400 sec ≈ 2.6M sec/month` is fine as `~2.5M`.

---

## 2. Ignoring Hash Collision Handling

### ❌ The Mistake

Proposing `hash(longUrl)[:7]` for short code generation without addressing what happens when two different URLs produce the same 7-character prefix. Or worse, assuming collisions "won't happen."

### 🎯 What the Interviewer Expects

- Acknowledge that any hash-based approach has collision risk, especially when truncating.
- Present a mitigation: retry with a different salt, append a counter, or check-before-insert.
- Compare with collision-free alternatives: pre-generated keys (KGS) or a centralized counter with base62 encoding.
- Explain the trade-off: hash-based is coordination-free but needs collision handling; KGS is collision-free but adds a service.

### 💡 Tip

The strongest answer is to mention hashing as an option, explain its weakness, and then recommend KGS or counter-based generation as the preferred approach.

---

## 3. Not Addressing the 301 vs 302 Redirect Choice

### ❌ The Mistake

Defaulting to 301 or 302 without explaining the difference or acknowledging the trade-off. Many candidates never mention HTTP redirect semantics at all.

### 🎯 What the Interviewer Expects

| Redirect | Behavior | Implication |
|----------|----------|-------------|
| **301 Moved Permanently** | Browser caches the redirect; subsequent visits skip the server entirely | Better performance, better SEO; but analytics misses repeat visits from the same browser |
| **302 Found (Temporary)** | Browser always contacts the server | Every click is tracked (accurate analytics); higher server load |

- State the trade-off clearly.
- Recommend making it configurable per URL: 301 for general use, 302 for marketing campaigns that need precise click tracking.
- Mention that CDN behavior differs: a CDN can cache 301 responses aggressively, further reducing origin traffic.

### 💡 Tip

This is a favorite interviewer question precisely because it tests whether you think about the *user-facing behavior* of your system, not just the backend.

---

## 4. Overlooking Caching for Popular URLs

### ❌ The Mistake

Designing the redirect path as `API → Database` without a cache layer, or mentioning Redis in passing without explaining the caching pattern, eviction policy, or sizing.

### 🎯 What the Interviewer Expects

- Cache-aside (lazy loading) pattern: check Redis first → on miss, read from DB → populate cache.
- LRU eviction with a 24-hour TTL as a reasonable default.
- Sizing: 10M entries ≈ 1.6 GB fits easily in a single Redis node.
- Impact: an 80%+ cache hit rate reduces DB reads from 4,000/sec to ~800/sec.
- Cache invalidation: not a major concern here since URL mappings rarely change; TTL-based expiry is sufficient.

### 💡 Tip

Quantify the benefit. Saying "we add Redis" is average. Saying "Redis absorbs 80% of reads, dropping DB load from 4,000 to 800 QPS, which lets us defer sharding" is strong.

---

## 5. Missing the Hot Key Problem for Viral Links

### ❌ The Mistake

Treating all URLs as equally popular. Not considering what happens when a single short URL goes viral and receives millions of requests in minutes (e.g., a trending tweet or breaking news link).

### 🎯 What the Interviewer Expects

A layered defense against hot keys:

| Layer | Mechanism | Why |
|-------|-----------|-----|
| **CDN** | Cache 301 redirects at edge locations globally | Absorbs the vast majority of requests before they reach origin |
| **Redis replicas** | Replicate hot keys across multiple read nodes | Prevents a single cache node from becoming a bottleneck |
| **Local in-memory cache** | Each API server keeps a small LRU cache (TTL ~30–60 sec) | Eliminates even the Redis network round-trip for the hottest URLs |

- Explain *why* it's a problem: a single Redis key hashed to one slot can saturate that node's CPU/network.
- Mention detection: monitor per-key access rates; auto-promote keys above a threshold.

### 💡 Tip

This is one of the deepest signals in a URL Shortener interview. Candidates who proactively bring up hot keys demonstrate real-world systems thinking.

---

## 6. Not Discussing URL Expiration Cleanup

### ❌ The Mistake

Mentioning that URLs can have an `expires_at` field but never explaining how expired URLs are actually cleaned up. Leaving expired entries in the database and cache indefinitely.

### 🎯 What the Interviewer Expects

Two complementary strategies:

1. **Lazy deletion (on read):**
   - When a redirect request arrives, check `expires_at`.
   - If expired, return `410 Gone` instead of redirecting.
   - Optionally remove from cache immediately.
   - Pro: zero background overhead. Con: expired entries linger in storage.

2. **Background cleanup job:**
   - Periodic job scans for `expires_at < now()` and deletes in batches.
   - Run during off-peak hours to minimize DB load.
   - Reclaims storage and keeps indexes lean.

- Mention that expired short codes should **not** be immediately reused — a user who bookmarked the old link would get unexpected content.

### 💡 Tip

This demonstrates you think about operational concerns, not just the happy path. It also connects to storage estimation ("if we never clean up, storage grows unbounded").

---

## 7. Forgetting Custom Alias Collision Handling

### ❌ The Mistake

Supporting custom aliases (e.g., `short.ly/my-brand`) without explaining how to handle the case where the requested alias is already taken. Or worse, silently overwriting an existing URL.

### 🎯 What the Interviewer Expects

- **Check-before-insert:** Query the database for the requested alias before writing.
- **Return 409 Conflict** if the alias already exists, with a clear error message.
- **Atomicity:** Use a conditional write (e.g., DynamoDB `PutItem` with `attribute_not_exists(short_code)`) to prevent race conditions where two concurrent requests claim the same alias.
- **Validation:** Custom aliases should be validated for length, character set (alphanumeric + hyphens), and blocked words.
- **Namespace separation:** Ensure custom aliases don't collide with system-generated codes. One approach: system codes are always 7 random characters; custom aliases must be ≥ 3 characters and contain at least one non-alphanumeric character (like a hyphen).

### 💡 Tip

This is a small detail that reveals how carefully you think about edge cases and data integrity. Strong candidates handle it in one or two sentences without derailing the conversation.

---

## Summary Table

| # | Pitfall | What's Missing | Scoring Impact |
|---|---------|---------------|----------------|
| 1 | No estimation | Quantitative reasoning | Estimation dimension: -2 to -4 points |
| 2 | No collision handling | ID generation depth | Deep Dives dimension: -2 to -3 points |
| 3 | No 301 vs 302 discussion | User-facing behavior awareness | Trade-offs dimension: -1 to -2 points |
| 4 | No caching detail | Performance engineering | Architecture dimension: -2 to -3 points |
| 5 | No hot key handling | Real-world scale thinking | Deep Dives dimension: -2 to -3 points |
| 6 | No expiration cleanup | Operational maturity | Deep Dives dimension: -1 to -2 points |
| 7 | No alias collision logic | Edge case rigor | Data Model dimension: -1 to -2 points |

---

*See [RUBRIC](./RUBRIC.md) for full scoring criteria and [STRONG-ANSWER](./STRONG-ANSWER.md) for how to address each of these correctly.*

---

## 8. Choosing the Wrong Realtime Transport by Default

### ❌ The Mistake

Using one channel for all realtime scenarios (usually WebSocket) without validating whether communication is one-way, bidirectional, bursty, or mostly idle.

### 🎯 What the Interviewer Expects

- A transport decision matrix tied to product behavior and cost profile.
- Explicit fallback strategy and reconnect replay semantics.
- Ordering scope and deduplication plan for multi-device users.

### 💡 Tip

State channel selection as a requirement-driven decision, not a technology preference.

## 9. Over- or Under-Coordinating Contention Paths

### ❌ The Mistake

Either adding distributed locks too early or ignoring conflicts until oversell/double-assignment incidents appear.

### 🎯 What the Interviewer Expects

- An escalation ladder: optimistic -> pessimistic/serialized -> distributed coordination.
- Measurable triggers (conflict rate, retry depth, lock wait time).
- Idempotent retries, bounded backoff, and failure-mode handling.

### 💡 Tip

Show how you would isolate hot keys rather than globally locking the entire workload.

## 10. Missing Durable Workflow Boundaries for Multi-step Operations

### ❌ The Mistake

Treating multi-service flows as a single best-effort request chain without durable checkpoints, compensation, or idempotency.

### 🎯 What the Interviewer Expects

- Explicit step state machine and compensation strategy.
- Durable checkpointing and resume path after crash/redeploy.
- Idempotency requirements for every side-effecting step.
- Versioning plan for in-flight workflow upgrades.

### 💡 Tip

If a flow can partially succeed, describe how it recovers before describing happy-path latency.

