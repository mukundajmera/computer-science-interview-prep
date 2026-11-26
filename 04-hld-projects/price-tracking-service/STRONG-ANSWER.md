
# Price Tracking Service - Strong Answer

## 0-5 min: Requirements

Say: "I will separate product reads, crawl control, price ingestion, and alert delivery so merchant spikes do not break user-facing reads."

- Support product lookup, current offer, historical price charts, user alerts, crawl scheduling, and merchant-level controls.
- Non-goals: checkout, merchant onboarding, and full anti-bot policy design unless requested.
- Correctness boundary: accepted price observations are immutable events; alerts are idempotent per user, product, and condition.

## 5-10 min: Scale and Constraints

Say: "Reads need low latency, while crawls are bursty and must be throttled per merchant."

- Plan for product price reads around 30K QPS peak and alert writes around 5K QPS peak.
- Target p95 product read latency under 300 ms and p99 under 800 ms.
- Crawl pipeline availability can be lower than user API availability because stale prices are preferable to broken reads.

## 10-20 min: API and Data Model

Say: "The public API reads projections, while internal ingestion writes normalized observations with producer identity."

- `GET /products/{id}/price` returns current offer, merchant, currency, freshness, and confidence.
- `GET /products/{id}/price-history` reads rollups plus recent raw events.
- `POST /alerts` creates idempotent threshold, drop-percent, or availability alerts.
- Core data: `product`, `offer`, `price_event`, `price_rollup`, `alert_rule`, `alert_delivery`, `crawl_job`, and `merchant_budget`.

## 20-35 min: Architecture

Say: "The crawler is a controlled producer; it should not directly mutate user-facing state."

- Product/Alert API serves reads from cache and relational metadata.
- Scheduler emits crawl jobs by merchant budget, priority, robots policy, and freshness target.
- Collectors normalize observations and submit to Price Ingestion API.
- Ingestion appends `PriceObserved`, updates current-offer projection, writes history, and emits `AlertMatched` when rules qualify.

## 35-42 min: Deep Dives

Say: "The failure mode to avoid is a bad merchant crawl poisoning prices or spamming alerts."

- Merchant pause: set `merchant_budget.paused_until`; existing prices remain readable while crawls drain.
- Late or duplicate observations: event writes are idempotent and rollups are rebuilt by `(offer_id, bucket)`.
- Alert delivery: dedupe by rule and triggering event, respect quiet hours, and record delivery state.
- Bad parser rollout: shadow ingest one merchant, compare against samples, then enable projections gradually.

## 42-45 min: Wrap-up

Say: "I chose append-only price events plus derived current projections because auditability and rebuildability matter more than overwriting the latest price."

- Trade-off: more write amplification, but safer recovery and accurate charts.
- Next evolution: merchant-specific crawl policies, anomaly scoring before projection, and cost-aware freshness tiers.
