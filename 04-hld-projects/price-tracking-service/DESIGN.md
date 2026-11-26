# Price Tracking Service - Design

## 1. Requirements and Constraints

### Functional
- Track products and merchant offers from submitted URLs or catalog IDs.
- Crawl merchant pages and normalize observed prices into product-level history.
- Let users create threshold, percent-drop, and back-in-stock alerts.
- Serve product detail, current offer, and historical price charts with low latency.

### Non-functional
| Requirement | Target |
|---|---|
| Product price read latency | p95 < 300ms, p99 < 800ms |
| Alert delay after observed drop | p95 < 15 minutes, hard target < 1 hour |
| Crawl freshness | top 5% watched offers every 15 minutes; long tail within 24 hours |
| Availability | 99.9% user API, 99.5% crawl pipeline |
| Duplicate alerts | effectively 0 per `(user_id, alert_id, price_event_id)` |

## 2. Back-of-envelope estimation

Assume 100M products, 700M merchant offers, 20M MAU, and 500M active alerts.

| Metric | Value |
|---|---|
| Price reads | 30K QPS peak |
| Alert writes | 5K QPS peak |
| Crawl fetches | 80K/s peak, adaptive by merchant budget |
| Accepted price events | 10K/s average, 100K/s peak during sale windows |
| Price history storage | ~100K events/s * 80 bytes normalized = ~690 GB/day before compression |

Decision impact: separate crawl control, price ingestion, alert evaluation, and read serving so sale spikes do not block user reads.

## 3. APIs

```http
POST /api/v1/products/track
GET  /api/v1/products/{product_id}
GET  /api/v1/products/{product_id}/price-history?merchant_id=&window=180d
GET  /api/v1/products/{product_id}/offers
POST /api/v1/alerts
PATCH /api/v1/alerts/{alert_id}
DELETE /api/v1/alerts/{alert_id}
POST /api/v1/crawl-observations
POST /api/v1/crawl-jobs/{merchant_id}/pause
```

### Product and offer tracking

```http
POST /api/v1/products/track
Idempotency-Key: user-123:track:https://shop.example/item/sku-9

{
  "url": "https://shop.example/item/sku-9",
  "merchant_id": "m_shop",
  "user_hint": {
    "title": "Noise Cancelling Headphones",
    "brand": "Acme"
  }
}
```

```json
{
  "product_id": "p_7f2",
  "offer_id": "o_91a",
  "tracking_state": "active",
  "current_price": {"amount_cents": 12999, "currency": "USD"},
  "next_crawl_eta": "2026-06-14T09:15:00Z"
}
```

### Alert contract

```http
POST /api/v1/alerts
Idempotency-Key: user-123:p_7f2:below-100

{
  "product_id": "p_7f2",
  "offer_scope": "any_merchant",
  "condition": {"type": "price_below", "amount_cents": 10000, "currency": "USD"},
  "channels": ["email", "push"]
}
```

| Error | Retry? | Handling |
|---|---|---|
| `duplicate_idempotency_key` | no | Return original alert when payload hash matches; reject mismatched payload. |
| `unknown_product` | no | Ask caller to track the product first. |
| `unsupported_merchant` | no | Store user request only if manual tracking is supported. |
| `crawl_observation_stale` | no | Drop observation older than the current offer version unless backfill mode is active. |
| `merchant_rate_limited` | yes | Reschedule crawl by merchant budget and keep previous price as current. |

### Crawl observation contract

Collectors and browser/render workers submit normalized observations. The API is internal and requires producer identity.

```json
{
  "merchant_id": "m_shop",
  "canonical_url": "https://shop.example/item/sku-9",
  "merchant_sku": "SKU-9",
  "observed_at": "2026-06-14T09:02:00Z",
  "price": {"amount_cents": 9999, "currency": "USD"},
  "availability": "in_stock",
  "title": "Acme Noise Cancelling Headphones",
  "content_hash": "sha256:...",
  "crawl_run_id": "cr_456"
}
```

## 4. Data model and storage

| Store/table | Key fields | Indexes, partitioning, and constraints | Retention |
|---|---|---|---|
| `product` | `product_id`, `canonical_title`, `brand`, `category`, `image_ref`, `created_at` | PK `product_id`; search index on normalized title/brand/category | Until all offers and alerts are deleted, then tombstone 90 days |
| `offer` | `offer_id`, `product_id`, `merchant_id`, `merchant_sku`, `canonical_url`, `status`, `current_price`, `updated_at` | PK `offer_id`; unique `(merchant_id, merchant_sku)` when available; unique URL hash fallback; index `(product_id, updated_at)` | Active while tracked; inactive offers compacted after 18 months |
| `price_event` | `offer_id`, `observed_at`, `amount_cents`, `currency`, `availability`, `source`, `event_hash` | Partition by day and `hash(offer_id)`; unique `(offer_id, observed_at, event_hash)`; index latest by `(offer_id, observed_at DESC)` | Raw events 90 days hot, compressed rollups 3 years |
| `price_rollup` | `offer_id`, `bucket_start`, `bucket_size`, `min_price`, `max_price`, `open_price`, `close_price` | PK `(offer_id, bucket_start, bucket_size)`; partition by month | 3 years online, archive after |
| `alert` | `alert_id`, `user_id`, `product_id`, `condition`, `channels`, `state`, `created_at` | PK `alert_id`; index `(product_id, state)` for evaluation; index `(user_id, created_at)` | Until deleted plus 30-day audit tombstone |
| `alert_delivery` | `alert_id`, `price_event_id`, `channel`, `state`, `attempt`, `dedupe_key` | Unique `dedupe_key=(user_id, alert_id, price_event_id, channel)`; index `(state, next_attempt_at)` | 30 days hot, 1 year audit summary |
| `crawl_frontier` | `merchant_id`, `offer_id`, `priority`, `next_crawl_at`, `lease_until`, `failure_count` | Partition by `merchant_id`; priority index `(next_crawl_at, priority)`; leased with compare-and-set | Active offers only |
| `merchant_budget` | `merchant_id`, `robots_policy`, `token_rate`, `burst`, `error_rate`, `paused_until` | PK `merchant_id`; updated by crawl control loop | Keep current plus 90-day config history |

Use a relational store for user alerts and product metadata, a wide-column or time-series store for price events, object storage for raw crawl artifacts, Redis-like cache for current offer reads, and Kafka/PubSub topics for `PriceObserved`, `OfferChanged`, and `AlertMatched` events.

## 5. High-level architecture

Please refer to the canonical [Architecture Diagram](./diagrams/architecture.mmd).

## 6. Critical paths

### Read path
1. Product API validates caller and reads product/offer summary from cache by `product_id`.
2. On cache miss, it reads `product` and latest `offer` rows, then refreshes cache with a short TTL.
3. Price history reads query `price_rollup` for old windows and raw `price_event` only for the recent high-resolution window.
4. If the history store is degraded, return current price plus partial chart metadata instead of failing the product page.

### Write path: observed price
1. Parser submits a crawl observation with `crawl_run_id`, URL hash, SKU, and content hash.
2. Ingestion validates merchant policy, normalizes currency, and dedupes by `(offer_id, observed_at, event_hash)`.
3. A new price event is appended, then `OfferChanged` is emitted only when price or availability materially changes.
4. Current-offer projector updates cache and latest-offer rows idempotently.
5. Alert evaluator scans active alert indexes for the product and emits deduped `alert_delivery` jobs.

### Write path: alert creation
1. API acquires idempotency by `(user_id, idempotency_key)` and validates product existence.
2. Alert row is committed with `state=active`.
3. If the current price already satisfies the condition, evaluator creates an immediate `alert_delivery` using the current latest event.
4. User-facing response is returned after durable alert creation; notification delivery remains async.

### Failure and recovery paths
- **Crawler failures:** classify DNS, timeout, parser mismatch, anti-bot, and merchant 5xx separately; retry with exponential backoff and merchant budget caps; send repeated parser failures to DLQ with the raw artifact.
- **Stale observations:** compare `observed_at` and offer version before updating current price; keep raw event for audit only in backfill mode.
- **Event replay:** rebuild current-offer cache and alert projections from `price_event` and `OfferChanged` topics using idempotent upserts.
- **Notification outage:** keep `alert_delivery` pending with channel-specific retry windows; do not generate a second delivery for the same price event.
- **History store outage:** serve cached current prices and degraded charts; backfill missed rollups from raw events after recovery.

## 7. Deep dives

### Crawl scheduling and merchant fairness
- Score each offer by watcher count, last price volatility, merchant sale calendar, user freshness SLA, and previous crawl success.
- Maintain per-merchant token buckets from robots policy and observed error rate; scheduler cannot lease more work than the merchant budget allows.
- Use `next_crawl_at` priority queues within each merchant partition, then a global fair scheduler to avoid one large merchant starving smaller ones.
- Increase crawl interval for stable low-watch offers and shrink it for high-watch or recently changed offers.
- Emergency pause a merchant by setting `merchant_budget.paused_until`; existing prices remain readable while crawls drain.

### SKU dedupe and product matching
- Prefer deterministic keys in this order: merchant SKU/GTIN, canonical URL hash, structured data identifiers, then normalized title/brand/model.
- Keep `offer` distinct from `product`: one product may have many merchant offers with different URLs, shipping states, and currencies.
- Candidate matches below confidence threshold enter review or remain separate products; never merge automatically when brand/model conflicts.
- Store merge events so product-level history can be recomputed and bad merges can be rolled back by splitting offers back to prior product IDs.

### Price history compression
- Keep raw events hot for recent debugging and high-resolution charts.
- Downsample older history into hourly and daily OHLC buckets with min/max to preserve sale lows.
- Suppress no-op events where price, availability, and currency did not change, but retain crawl metadata counters for freshness monitoring.
- Rebuild rollups by `(offer_id, bucket)` after late events; writes are idempotent and replace bucket aggregates.

### Alert fanout correctness
- Alert evaluator reads active alerts by `(product_id, state)` and filters condition, currency, merchant scope, and quiet-hour policy.
- Delivery workers enforce the `dedupe_key` unique constraint before sending email, push, or webhook notifications.
- Large sale events are buffered through partitions by `product_id` and rate-limited per user/channel to avoid notification storms.
- A missed evaluator partition can replay from the last committed `PriceObserved` offset and regenerate the same delivery keys.

## 8. Rollout, observability, and rollback

### Observability
- Track crawl freshness by merchant, parse success rate, price-event acceptance rate, dedupe drop rate, alert match lag, delivery success, and product merge/split counts.
- Emit correlation IDs across crawl run, observation, price event, alert match, and notification delivery.
- Alert on freshness SLA misses for watched offers, sudden price-event drops by merchant, duplicate delivery constraint violations, and rollup lag.

### Rollout
- Start with read-only ingestion for one merchant, compare observed prices against manual samples, then enable current-offer projection.
- Enable alert evaluation in shadow mode before sending notifications; compare matched alerts against expected rules.
- Ramp by merchant and category, not globally, so parser failures and anti-bot behavior are contained.

### Rollback
- Pause affected merchants in `merchant_budget` and stop new crawl leases.
- Disable alert sending by channel flag while leaving evaluator replay offsets intact.
- Rebuild current-offer and rollup projections from raw `price_event` after a bad parser or merge release.
- Undo incorrect product merges by replaying stored merge/split events and invalidating affected cache keys.

## 9. Trade-offs

| Decision | Chosen | Alternative | Why |
|---|---|---|---|
| Freshness model | adaptive crawl by watcher and volatility | fixed interval for every offer | better cost and merchant fairness |
| Price source of truth | append-only events plus current projection | overwrite current price only | auditability, chart rebuilds, and recovery |
| Alert delivery | async fanout with dedupe keys | synchronous notification on ingestion | protects crawl ingestion and avoids duplicate sends |
| Product matching | conservative merge with rollback log | aggressive automatic merge | fewer user-visible wrong histories |
| History retention | hot raw events plus compressed rollups | keep all raw events online forever | lower cost while preserving chart fidelity |

## 10. Interview wrap-up

For a time-boxed explanation, use the [strong answer](./STRONG-ANSWER.md): lead with the freshness/cost trade-off, make price events append-only, and spend deep-dive time on crawl scheduling, product dedupe, history compression, and alert fanout recovery.
