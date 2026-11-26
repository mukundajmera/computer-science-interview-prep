# Notification Service — Model Answer (Time-Boxed)

Say: "I will make notification delivery durable and preference-aware, then handle provider retries, dedupe, and quiet hours before optimizing channel-specific throughput."

A strong-answer outline for a 40-minute Notification Service system design interview. Each section includes target timing and the key points an interviewer expects to hear.

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

1. "What channels do we need to support — email, SMS, push, in-app?"
2. "What's the expected scale — how many notifications per day and how many registered users?"
3. "Are there priority levels? Should a password-reset OTP always beat a marketing email?"
4. "What delivery guarantee do we need — at-most-once, at-least-once, or exactly-once?"
5. "Do users have preferences — opt-out per channel, per category, quiet hours?"
6. "Do we need delivery tracking — should callers be able to check if a notification was delivered?"

### Functional Requirements (confirm with interviewer)

- **Core:** Accept notification requests, route to the correct channel (email/SMS/push), deliver via provider APIs, track delivery status.
- **Preferences:** Respect user opt-out settings, channel preferences, and quiet hours.
- **Priority:** Support at least 3 tiers (critical, high, normal/low) with isolation between tiers.
- **Templates:** Render notifications from templates with dynamic variables.

### Non-Functional Requirements (state explicitly)

- **Throughput:** 100M notifications/day (~1,150/sec average, ~5,000/sec peak).
- **Users:** 500M registered users, each with preference settings.
- **Latency:** Critical notifications delivered in < 3 seconds; normal within minutes; marketing within hours.
- **Availability:** 99.99% — notification failures directly impact user trust and security (OTPs, alerts).
- **Delivery guarantee:** At-least-once with application-level deduplication for effectively-once.
- **Durability:** Every notification request and its outcome must be logged and queryable.

### Scope Boundaries

- **In scope:** Multi-channel delivery, priority queues, preferences, templates, retry/DLQ, status tracking.
- **Out of scope:** Notification content creation, billing/metering, marketing campaign management UI, A/B testing.

---

## Phase 2 — Estimation (5 min)

### Traffic

```
Daily volume:    100M notifications/day
Per second:      100M / 86,400 ≈ 1,150 notifications/sec (average)
Peak (3–5×):     ~5,000 notifications/sec (Black Friday, incident alerts)

Channel breakdown (typical):
  Email: 60% → 690/sec avg, ~3,000/sec peak
  Push:  30% → 345/sec avg, ~1,500/sec peak
  SMS:   10% → 115/sec avg, ~500/sec peak
```

### Storage (1-year horizon)

```
Notification records:
  Per record:    ~500 bytes (id, user_id, channel, status, template_id, payload ref, timestamps)
  Daily:         100M × 500B = 50 GB/day
  Yearly:        50 GB × 365 = ~18 TB
  With indexes:  ~25–30 TB

User preferences:
  500M users × 200 bytes = 100 GB (fits in a single DB instance)

Templates:
  ~10K templates × 5 KB avg = 50 MB (trivial, cached in memory)
```

### Queue Sizing

```
At peak 5,000/sec, if consumers lag by 60 seconds:
  Queue depth = 5,000 × 60 = 300K messages buffered
  At ~500 bytes each = 150 MB — well within Kafka/SQS capacity

Kafka partition count:
  Target 5,000/sec with ~500/sec per partition → 10 partitions per priority topic
```

### Provider Capacity

```
Email (SendGrid):    ~1,000/sec per connection → need 3 connections at peak
SMS (Twilio):        ~200/sec per connection → need 3 connections at peak
Push (APNS/FCM):     ~10,000/sec batch → single connection sufficient
```

---

## Phase 3 — API + Data Model + High-Level Design (10 min)

### API Endpoints

| Method | Endpoint | Purpose | Key Response |
|--------|----------|---------|--------------|
| `POST` | `/api/v1/notifications` | Send a notification | `201` with `notification_id` |
| `POST` | `/api/v1/notifications/bulk` | Send bulk notifications | `202 Accepted` with `job_id` |
| `GET` | `/api/v1/notifications/{id}/status` | Check delivery status | `200` with per-channel status |
| `GET` | `/api/v1/users/{user_id}/preferences` | Get user preferences | `200` with channel/category settings |
| `PUT` | `/api/v1/users/{user_id}/preferences` | Update preferences | `200` with updated settings |

**Error codes to mention:** `400` (invalid payload), `404` (notification not found), `409` (duplicate idempotency key), `429` (rate limited).

**Idempotency:** Callers include an `Idempotency-Key` header. The API server checks a Redis key (`idemp:{key}`) before processing — if it exists, return the cached response.

### Data Model

```
Table: notifications
─────────────────────────────────────────────────────
id               UUID         (Partition Key)
user_id          STRING       (GSI)
channel          ENUM         (email | sms | push | in_app)
priority         ENUM         (critical | high | normal | low)
status           ENUM         (PENDING | QUEUED | SENDING | DELIVERED | FAILED)
template_id      STRING
payload          JSON         (template variables)
idempotency_key  STRING       (unique index)
created_at       TIMESTAMP
updated_at       TIMESTAMP
delivered_at     TIMESTAMP    (nullable)
failure_reason   STRING       (nullable)

Table: user_preferences
─────────────────────────────────────────────────────
user_id          STRING       (Partition Key)
email_enabled    BOOLEAN
sms_enabled      BOOLEAN
push_enabled     BOOLEAN
quiet_hours_start  TIME       (nullable, in user's timezone)
quiet_hours_end    TIME       (nullable)
timezone         STRING
category_settings  JSON       (per-category opt-in/out)
updated_at       TIMESTAMP

Table: templates
─────────────────────────────────────────────────────
template_id      STRING       (Partition Key)
channel          ENUM
locale           STRING
subject          STRING       (nullable, for email)
body             TEXT         (with {{variable}} placeholders)
version          INT
updated_at       TIMESTAMP
```

- **Notification logs:** NoSQL (DynamoDB/Cassandra) — high write throughput, time-series access pattern, no joins needed.
- **User preferences:** PostgreSQL — complex queries (e.g., "all users who opted into SMS for category X"), strong consistency for preference updates.
- **Templates:** Cached in memory (< 50 MB total); PostgreSQL as backing store.

### High-Level Architecture

```
                          ┌──────────────────────────────────────────────────────┐
                          │                   Notification Service               │
                          │                                                      │
  Callers ──► API Gateway ──► Validation Service                                 │
  (internal     (auth,        ├─ check idempotency key (Redis)                   │
   services)    rate limit)   ├─ check user preferences (Preference Svc / cache) │
                              ├─ resolve template (Template Svc / cache)         │
                              └─ assign priority → publish to Kafka              │
                          │                                                      │
                          │   Kafka Topics (per priority)                        │
                          │   ┌──────────┬──────────┬──────────┬──────────┐      │
                          │   │ critical │   high   │  normal  │   low    │      │
                          │   └────┬─────┴────┬─────┴────┬─────┴────┬─────┘      │
                          │        │          │          │          │             │
                          │   Channel Router (consumer groups per priority)       │
                          │   ┌─────────┐ ┌─────────┐ ┌─────────┐               │
                          │   │  Email  │ │   SMS   │ │  Push   │               │
                          │   │ Workers │ │ Workers │ │ Workers │               │
                          │   └────┬────┘ └────┬────┘ └────┬────┘               │
                          │        │           │           │                     │
                          │   Rate Limiter (token bucket per provider)            │
                          │        │           │           │                     │
                          │   Provider Adapters                                  │
                          │   ┌─────────┐ ┌─────────┐ ┌─────────┐               │
                          │   │SendGrid │ │ Twilio  │ │APNS/FCM │               │
                          │   │   SES   │ │ Vonage  │ │         │               │
                          │   └────┬────┘ └────┬────┘ └────┬────┘               │
                          │        │           │           │                     │
                          │   Status Callbacks ──► Notification Status Store      │
                          │                                                      │
                          │   DLQ (failed after retries)                         │
                          └──────────────────────────────────────────────────────┘
```

**Ingestion path:** Caller → API Gateway → Validation Service → preference check → template resolve → publish to priority Kafka topic.

**Delivery path:** Kafka consumer → Channel Router → render template → rate limiter → Provider Adapter → external provider → status callback → update notification status.

**Failure path:** Provider error → retry with exponential backoff (3 attempts) → if still failing → DLQ.

---

## Phase 4 — Deep Dives (15 min)

### 4a. Fan-Out Strategy (~4 min)

**Problem:** How do we route 100M notifications/day to the right channel, at the right priority, without one category blocking another?

**Design: Priority-partitioned Kafka topics with per-channel consumer groups.**

```
Topic: notifications.critical    (10 partitions)
Topic: notifications.high        (10 partitions)
Topic: notifications.normal      (10 partitions)
Topic: notifications.low         (10 partitions)

Consumer groups per channel:
  email-workers  → consume from all 4 topics, weighted allocation
  sms-workers    → consume from all 4 topics, weighted allocation
  push-workers   → consume from all 4 topics, weighted allocation
```

**Why not topic-per-channel?** A single email topic would mix critical OTPs with marketing blasts. A bulk campaign could fill the topic and delay an OTP by minutes.

**Why not a single priority queue with sorting?** Kafka doesn't support priority within a partition. Separate topics give true isolation — critical consumers are never blocked by normal-queue backlog.

**Consumer allocation:**
- Critical queue: 60% of worker capacity (over-provisioned to ensure < 3 sec delivery).
- High queue: 25% of capacity.
- Normal queue: 10% of capacity.
- Low queue: 5% of capacity (starvation prevention — never fully starved).

**Bulk campaign fan-out:** A campaign to 10M users publishes to the low-priority topic at a throttled rate (~500/sec). The campaign takes ~5.5 hours to complete but never impacts transactional notifications.

### 4b. Delivery Guarantees (~4 min)

**Target:** At-least-once delivery at the queue level, effectively-once to the user.

**At-least-once mechanism:**

```
1. Kafka consumer reads message (auto-commit OFF)
2. Worker processes message: render template → send to provider
3. Provider returns ACK (HTTP 200/202)
4. Worker commits Kafka offset
5. Worker updates notification status to DELIVERED

If worker crashes between step 3 and 4:
  → Kafka redelivers the message (offset not committed)
  → Message is processed again → potential duplicate
```

**Deduplication for effectively-once:**

```
Before step 2, check Redis dedup store:
  Key:   dedup:{notification_id}:{channel}
  TTL:   24 hours

  If key EXISTS → skip send, commit offset (already delivered)
  If key MISSING → proceed with send → SET key after provider ACK
```

**Why not exactly-once?** Kafka supports exactly-once semantics (EOS) within its ecosystem, but our "consumer" is an external API call (SendGrid, Twilio). There's no way to atomically commit a Kafka offset and send an HTTP request in one transaction. At-least-once + dedup is the pragmatic answer.

**Edge case: provider ACK lost.** If the provider received and delivered the message but the ACK was lost (network timeout), the dedup key was never set. On retry, we send a duplicate. Mitigation: providers like FCM support `collapse_key` (dedup on their side); for email/SMS, accept rare duplicates as the lesser evil vs missed notifications.

### 4c. Priority Queue Handling (~3 min)

**Priority tiers and SLAs:**

| Priority | Use Cases | Delivery SLA | Queue | Consumer Share |
|----------|-----------|-------------|-------|----------------|
| **Critical** | OTP, security alerts, payment failures | < 3 sec | `notifications.critical` | 60% of capacity |
| **High** | Order confirmations, shipping updates | < 30 sec | `notifications.high` | 25% of capacity |
| **Normal** | Social notifications, recommendations | < 5 min | `notifications.normal` | 10% of capacity |
| **Low** | Marketing, newsletters, digests | Best-effort (hours) | `notifications.low` | 5% of capacity |

**Isolation guarantees:**
- Separate Kafka topics mean a backlog in `notifications.low` (e.g., 10M marketing campaign) creates zero consumer lag in `notifications.critical`.
- Each priority level has its own consumer group with dedicated instances. Critical consumers auto-scale independently.

**Starvation prevention:**
- Low-priority consumers have a minimum guaranteed throughput (5% of total capacity ≈ 250/sec at peak).
- If critical queue is empty, its idle consumer capacity is NOT redistributed — it stays ready for the next burst. Over-provisioning critical capacity is cheap insurance.

**Priority assignment logic:**
- The caller specifies `priority` in the API request.
- A mapping table overrides implicit priority by notification type (e.g., `type=OTP → critical` regardless of what the caller sends).
- This prevents a misconfigured caller from sending OTPs as low priority.

### 4d. Rate Limiting per Provider (~4 min)

**Problem:** External providers enforce strict rate limits. If we exceed them, they throttle us (HTTP 429), temporarily block our account, or silently drop messages.

**Design: Token bucket rate limiter per provider, per channel.**

```
Provider rate limits (configured):
  SendGrid:     1,000 emails/sec
  Amazon SES:   500 emails/sec  (secondary)
  Twilio:       200 SMS/sec
  APNS:         10,000 push/sec (batch)
  FCM:          10,000 push/sec (batch)

Token bucket implementation:
  Bucket: rate_limit:{provider}:{channel}
  Store:  Redis (INCR + EXPIRE for sliding window, or Lua script for token bucket)
  Refill: tokens replenish at the provider's documented rate

Worker flow:
  1. Acquire token from bucket for target provider
  2. If token available → send to provider
  3. If no token → hold message, retry after token refill interval
     (backpressure: pause Kafka consumer for this provider)
```

**Multi-provider failover:**

```
Email delivery attempt:
  1. Try SendGrid (primary) → check rate limit bucket
     → If tokens available → send → done
     → If throttled (no tokens or HTTP 429) → fall through
  2. Try Amazon SES (secondary) → check its rate limit bucket
     → If tokens available → send → done
     → If throttled → route to retry queue with delay
```

**Why this matters at scale:**
- At peak, we emit ~3,000 emails/sec. SendGrid allows 1,000/sec.
- Without rate limiting: 2,000 requests/sec are rejected (429), wasting compute and delaying delivery.
- With rate limiting + failover: 1,000/sec → SendGrid, 500/sec → SES, remaining 1,500/sec buffered and delivered within seconds as tokens refill.

**Adaptive rate limiting:**
- Monitor provider response codes. If 429s increase, reduce the configured rate preemptively.
- Track provider latency (p99). If latency spikes, reduce concurrency to avoid timeouts.
- Emit metrics to a dashboard: tokens consumed/sec, throttle events/sec, failover events/sec.

---

## Phase 5 — Trade-offs & Wrap-up (5 min)

### Key Trade-offs to Surface

| Decision | Choice | Trade-off |
|----------|--------|-----------|
| At-least-once vs exactly-once | At-least-once + dedup | Simpler architecture; rare duplicate is acceptable vs missed notification |
| Separate priority queues vs single queue | Separate queues | More Kafka topics to manage; but guarantees critical notifications are never blocked |
| Single provider vs multi-provider | Multi-provider with failover | Increased integration complexity; but eliminates single provider as SPOF |
| Sync vs async delivery | Async (queue-based) | Callers don't get instant delivery confirmation; but system handles 5,000/sec peak without backpressure to callers |
| Preference check before vs after queuing | Before queuing | Adds ~5 ms latency to ingestion; but prevents wasting queue capacity on suppressed notifications |
| NoSQL vs SQL for notification logs | NoSQL (DynamoDB/Cassandra) | No complex queries on logs; but handles 1,150 writes/sec with horizontal scaling |

### Evolution Narrative

| Version | What Changes | Handles |
|---------|-------------|---------|
| **v1-basic** | Single API server, single queue (RabbitMQ), one email provider, no priority tiers | ~100 notifications/sec, email only |
| **v2-scaled** | LB + multiple API servers, Kafka with priority topics, multi-channel (email + push + SMS), Redis for preferences/dedup, retry + DLQ | ~5,000 notifications/sec, 3 channels, 4 priority tiers |
| **v3-distributed** | Multi-region deployment, multi-provider failover, in-app channel with WebSocket, campaign service for bulk sends, smart delivery timing, cross-channel orchestration | ~50,000 notifications/sec globally, 4+ channels, 99.99% availability |

### Closing Statement (say this to the interviewer)

> "To summarize: we've designed a multi-channel notification service handling 100M notifications per day for 500M users. The core architecture is an API gateway that validates requests and checks user preferences, then publishes to priority-partitioned Kafka topics. Dedicated consumer groups per channel process messages with at-least-once delivery and application-level deduplication for effectively-once semantics. Rate limiters with token buckets protect external providers, and multi-provider failover ensures resilience. The system scales from a single-queue MVP to a globally distributed service with priority isolation, campaign support, and cross-channel delivery orchestration. The key trade-off is choosing at-least-once delivery with dedup over exactly-once, which is appropriate because a rare duplicate notification is far less damaging than a missed security alert."

---

*See [RUBRIC](./RUBRIC.md) for how this answer maps to scoring criteria, and [PITFALLS](./PITFALLS.md) for common mistakes to avoid.*
