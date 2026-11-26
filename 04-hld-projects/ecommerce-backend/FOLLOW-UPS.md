# E-commerce Backend — Follow-Up Questions

Common follow-up variants an interviewer may ask after the core E-commerce Backend design, along with brief approach outlines for each.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [COMPARISON](./COMPARISON.md)

---

## 1. "How would you handle a flash sale with 50K orders/sec for a limited item?"

### Why They Ask

Tests whether you can design for extreme traffic spikes without overselling, while maintaining a good user experience for the 99% who won't get the item.

### Approach

- **Admission control layer:** Place a virtual queue (backed by Redis sorted sets or a dedicated queue service) in front of the checkout flow. Only the first N users (where N = available stock × small multiplier) pass through to the actual checkout page.
- **Inventory tokens:** For a flash item with 1,000 units, pre-generate 1,000 tokens in Redis. Acquiring a token is an atomic `DECR` — O(1), no database hit. Users without a token get an instant "Sold Out" response.
- **Static product pages:** Serve the flash sale product page from pre-rendered static files on a CDN. No dynamic rendering, no product service calls during the spike.
- **Pre-warming infrastructure:** 30 minutes before the sale, scale API servers to 10×, warm Redis caches, open database connection pools, and increase rate limits on the checkout path.
- **Countdown + stagger:** Show a countdown timer. At T=0, stagger user access by adding a random delay (0–2 sec) per client to avoid a thundering herd on the exact millisecond.

```
User → CDN (static page) → Queue Service (admission control)
                                  ↓ (admitted)
                           Inventory Token (Redis DECR)
                                  ↓ (token acquired)
                           Checkout Service → Payment → Order
```

**Key trade-off:** Strict fairness (first-come-first-served) vs throughput. A pure FCFS queue serializes requests; a token-grab approach is faster but less "fair." Most platforms favor token-grab for performance.

---

## 2. "How would you add a recommendation engine?"

### Why They Ask

Probes your understanding of data pipelines, ML integration, and how to serve real-time personalization without adding latency to the critical path.

### Approach

- **Data collection:** Capture user behavior events (views, searches, purchases, cart adds) into a Kafka event stream. Store raw events in a data lake (S3 + Parquet) for offline processing.
- **Offline pipeline:** Run collaborative filtering (user-user or item-item) and content-based models on the data lake using Spark. Pre-compute "users who bought X also bought Y" associations. Store results in a recommendations database (DynamoDB or Redis).
- **Real-time pipeline:** For session-based recommendations ("because you just viewed X"), a stream processor (Flink) consumes recent events and updates a real-time feature store.
- **Serving layer:** A Recommendation Service looks up pre-computed recommendations from the database, optionally re-ranks using real-time signals, and returns top-N items.
- **Integration points:**
  - Product detail page: "Frequently bought together" (pre-computed).
  - Home page: "Recommended for you" (personalized, refreshed daily).
  - Cart page: "You might also need" (real-time, based on current cart).

```
User Events → Kafka → Data Lake → Spark (offline models) → Recommendation DB
                    → Flink (real-time features) → Feature Store ↗
                                                                    ↘
                         Recommendation Service ← merges both → API response
```

**Key trade-off:** Pre-computed recommendations (low latency, stale) vs real-time inference (fresh, higher latency and cost). A hybrid approach — pre-computed base with real-time re-ranking — balances both.

---

## 3. "How would you support multi-region deployment?"

### Why They Ask

Tests your understanding of global distribution, data replication, and consistency trade-offs when an e-commerce platform serves users across continents.

### Approach

- **Architecture:** Deploy full stacks in 3+ regions (US-East, EU-West, AP-Southeast). Each region has its own API servers, caches, search clusters, and database replicas.
- **DNS routing:** Use latency-based DNS to route users to the nearest region. CDN serves static assets and product images globally.
- **Data partitioning by domain:**
  - **Product catalog (read-heavy):** Replicate the full catalog to all regions (async replication, eventual consistency). A product update by a seller propagates within seconds. Acceptable staleness.
  - **Inventory (strong consistency):** Inventory for a given warehouse is owned by the region closest to that warehouse. Cross-region inventory checks add latency but prevent overselling.
  - **Orders (regional ownership):** An order is created and owned by the region where the user is located. Order data replicates to other regions for analytics and customer support.
  - **User accounts:** Global table with multi-leader replication (e.g., DynamoDB Global Tables). Conflicts resolved by last-writer-wins for profile fields; append-only for order history.
- **Checkout across regions:** If a user in EU orders from a US warehouse, the EU order service communicates with the US inventory service synchronously for reservation, then handles payment locally.

**Key trade-off:** Low-latency reads (replicate everything) vs inventory accuracy (single-owner for stock). A hybrid per-domain approach — AP for catalog, CP for inventory — is the practical solution.

---

## 4. "How would you prevent fraud?"

### Why They Ask

Probes your awareness of adversarial scenarios: fake accounts, stolen credit cards, abuse of promotions, and return fraud. Tests whether you can add trust & safety without degrading the checkout experience.

### Approach

- **Real-time risk scoring:** At checkout, a Fraud Service assigns a risk score (0–100) based on signals: device fingerprint, IP geolocation vs billing address, order velocity (too many orders per minute), payment method age, order value deviation from user history.
- **Decision engine:**
  - Score < 30 → auto-approve.
  - Score 30–70 → step-up verification (SMS OTP, email confirmation).
  - Score > 70 → hold for manual review; authorize but don't capture payment.
- **Signals and features:**
  - **Device:** Browser fingerprint, device ID, known proxy/VPN detection.
  - **Behavioral:** Session duration before purchase (bots are fast), mouse movement patterns, page sequence.
  - **Payment:** BIN country match, AVS/CVV response from gateway, velocity of card usage across accounts.
  - **Promotion abuse:** Same address/device using multiple accounts for first-time discounts. Track normalized address hashes.
- **Async review pipeline:** Flagged orders enter a review queue. Analysts can approve, reject, or request more information. ML model retrains weekly on analyst decisions.
- **Post-order:** Monitor return rates per user. Flag accounts with abnormally high return rates or "item not received" claims.

**Key trade-off:** False positives (blocking legitimate customers → lost revenue) vs false negatives (letting fraud through → chargebacks). Err on the side of step-up verification rather than hard blocks for borderline cases.

---

## 5. "How would you handle inventory across multiple warehouses?"

### Why They Ask

Tests whether you can design a distributed inventory system that optimizes for shipping cost and delivery speed while maintaining accuracy across locations.

### Approach

- **Inventory model:** Each product has inventory records per warehouse: `(product_id, warehouse_id, available, reserved, version)`. Total available = `SUM(available)` across all warehouses.
- **Display vs allocation:** On the product page, show aggregate availability ("In Stock" if any warehouse has stock). At checkout, allocate inventory from the optimal warehouse.
- **Warehouse selection algorithm:**
  1. Filter warehouses with sufficient stock.
  2. Rank by: distance to shipping address (shipping cost/speed), current stock level (balance load), warehouse capacity utilization.
  3. Select top-ranked warehouse; fall back to second choice if reservation fails.
- **Split shipments:** If no single warehouse has all items, split the order into sub-shipments from different warehouses. Show the customer: "Item A ships from Warehouse 1 (arrives Monday), Item B ships from Warehouse 2 (arrives Tuesday)."
- **Inventory synchronization:** Each warehouse's inventory is the source of truth for its own stock. A central Inventory Service aggregates views. Updates propagate via events (warehouse stock change → Kafka → central index update).
- **Rebalancing:** Offline analytics identify products with high demand in regions where stock is low. Trigger warehouse-to-warehouse transfers to preposition inventory closer to demand.

```
Product Page → Inventory Aggregator (cached, eventually consistent)
Checkout → Warehouse Selector → Reserve at optimal warehouse (strong consistency)
                               → Fallback to next warehouse on failure
```

**Key trade-off:** Single-warehouse simplicity (one reservation, one shipment) vs multi-warehouse optimization (lower shipping cost, faster delivery, but more complex reservation and potential split shipments).

---

## 6. "How would you design the returns and refunds flow?"

### Why They Ask

Tests whether you think beyond the happy path. Returns involve reverse logistics, inventory re-stocking, payment refunds, and seller disputes — a complex multi-step workflow.

### Approach

- **Return request:** User initiates a return via `POST /api/v1/orders/{id}/returns` with reason and item list. The system validates the return window (e.g., 30 days from delivery) and return policy per seller/category.
- **Return state machine:**

```
REQUESTED → APPROVED → ITEM_SHIPPED_BACK → ITEM_RECEIVED → INSPECTED → REFUNDED
               ↓                                               ↓
           REJECTED                                     PARTIAL_REFUND
```

- **Refund processing:** After inspection, trigger a refund through the Payment Service. Refund goes to the original payment method. Use the original transaction's `payment_id` for traceability.
- **Inventory re-stocking:** Only re-add to available inventory after the item passes inspection. Damaged items go to a separate "defective" inventory pool.
- **Seller notifications:** In a marketplace, the seller is notified at each step. If the seller disputes the return, the platform mediates (hold refund until resolution).
- **Fraud signals:** High return rates per user feed into the Fraud Service. Patterns like "frequently returns expensive electronics" trigger review.

**Key trade-off:** Generous return policies (better customer experience, higher return rate and cost) vs strict policies (lower cost, worse customer perception). Most platforms optimize for customer trust with fraud detection as a backstop.

---

## Quick Reference

| # | Follow-Up | Core Challenge | Key Concept |
|---|-----------|---------------|-------------|
| 1 | Flash sale handling | Extreme concurrency, fairness, overselling | Admission control, inventory tokens, pre-warming |
| 2 | Recommendation engine | Data pipeline, ML serving, personalization | Offline + real-time hybrid, feature store |
| 3 | Multi-region deployment | Replication, per-domain consistency model | AP for catalog, CP for inventory, regional ownership |
| 4 | Fraud prevention | Adversarial users, real-time risk scoring | Risk score engine, step-up verification, ML retraining |
| 5 | Multi-warehouse inventory | Distributed stock, warehouse selection, split shipments | Aggregation layer, optimal allocation, rebalancing |
| 6 | Returns and refunds flow | Reverse logistics, refund processing, seller disputes | Return state machine, inventory re-stocking, fraud signals |

---

*See [STRONG-ANSWER](./STRONG-ANSWER.md) for how to structure the base design, and [PITFALLS](./PITFALLS.md) for mistakes to avoid when handling these extensions.*

---

## Pattern Integration Addendum

### 7. "How would you choose transport/channel strategy under changing realtime requirements?"

#### Why They Ask

Tests whether you can avoid defaulting to a single transport and instead choose based on interaction model, freshness target, and connection cost.

#### Approach

- **Channel matrix:** Polling for low-frequency updates, long polling for compatibility fallback, SSE for one-way server push, WebSocket for bidirectional high-frequency flows.
- **Fallback policy:** Keep a deterministic downgrade path (`websocket -> sse -> long polling`) for restrictive networks.
- **Ordering + replay:** Assign monotonic event IDs and replay missed ranges after reconnect.
- **Connection management:** Maintain user-to-connection mapping with heartbeat and idle timeouts.

#### Key trade-off

A richer realtime channel improves UX but increases stateful infrastructure complexity and connection operating cost.

### 8. "How would you escalate contention strategy as load and conflict rates increase?"

#### Why They Ask

Probes whether you can pick the least-complex coordination model first, then escalate only when measured conflict pressure justifies it.

#### Approach

- **Start optimistic:** Version-check + bounded retry for low conflict workloads.
- **Escalate selectively:** Move hot keys to pessimistic lock or serialized queue lanes.
- **Distributed coordination:** Use distributed lock only when cross-node exclusivity is truly required.
- **Safety controls:** Add idempotency keys, retry jitter, lock timeout, and deadlock avoidance rules.

#### Key trade-off

Stronger coordination raises correctness confidence but can reduce throughput and availability under peak contention.

### 9. "How would you make multi-step flows durable and retry-safe?"

#### Why They Ask

Tests your ability to keep business consistency across partial failures in workflows that span services and time.

#### Approach

- **State machine first:** Define explicit lifecycle states and transition guards.
- **Saga style:** Commit each step independently with compensating actions for rollback.
- **Durability:** Persist workflow checkpoints before advancing to the next step.
- **Idempotency:** Require stable idempotency keys for all side-effecting steps.
- **Versioning:** Keep old workflow definitions alive for in-flight instances during upgrades.

#### Key trade-off

Durable orchestration improves resilience and observability but adds runtime overhead and operational complexity.

### 10. "How would you adapt this design for Yelp-style local business discovery?"

#### Why They Ask

Tests whether you can extend a commerce catalog into local-intent search where distance and textual relevance must both be first-class ranking signals.

#### Approach

- **Query shape:** Support `term + location + category + page` as the default search contract.
- **Geo + text:** Use Elasticsearch `bool` query with `must` for text relevance and `filter` for category/status constraints.
- **Distance handling:** Use `geo_distance` for strict radius filtering, then `function_score` for smooth distance decay.
- **Result payload:** Return partial business cards (name, distance, rating, review_count) and load full details lazily.

#### Key trade-off

Strict radius filters improve relevance precision but may under-return in low-density regions; adaptive radius expansion improves recall but can increase latency.

### 11. "How do you support location-name search (for example, city or neighborhood) instead of raw lat/lng?"

#### Why They Ask

Evaluates whether you can bridge human-friendly location input to efficient geospatial query primitives.

#### Approach

- **Location resolver:** Resolve location text to one or more polygons via a location metadata service.
- **Index strategy:** Store business point location plus optional `location_names` keyword list for fast coarse filtering.
- **Two-stage query:** First narrow by location names/polygon bounding box, then precise geo filter/ranking.
- **Fallback:** If polygon resolution fails, geocode query to a centroid and run bounded radius search.

#### Key trade-off

Polygon precision improves correctness for irregular areas, but polygon operations are heavier than centroid/radius matching.

### 12. "How do you keep average ratings visible in search results without expensive runtime aggregation?"

#### Why They Ask

Probes whether you understand write-time denormalization for read-heavy search surfaces.

#### Approach

- **Source-of-truth writes:** Persist reviews in OLTP store with `(business_id, user_id)` uniqueness.
- **Aggregate maintenance:** Update `rating_sum`, `rating_count`, and derived `avg_rating` in business record during review writes.
- **Index projection:** Publish business aggregate changes to Elasticsearch asynchronously.
- **Drift control:** Run periodic reconciliation jobs to recompute aggregates and fix projection drift.

#### Key trade-off

Write-path complexity increases, but read latency and search cost stay predictable at scale.

### 13. "How do you enforce one-review-per-user-per-business while preserving low write latency?"

#### Why They Ask

Checks whether you separate correctness constraints from search projections and avoid enforcing invariants in Elasticsearch.

#### Approach

- **Constraint at OLTP:** Add unique constraint/index on `(business_id, user_id)` in primary relational store.
- **Idempotent write API:** Use client idempotency keys to handle retries safely.
- **Update path:** On duplicate attempts, return conflict or convert to "edit existing review" flow.
- **Projection semantics:** Search index stores denormalized review summary only; uniqueness is never enforced in ES.

#### Key trade-off

Hard constraints in OLTP guarantee correctness, while asynchronous indexing maintains search performance.

---

## Yelp-Style Quick Reference

| # | Follow-Up | Core Challenge | Key Concept |
|---|-----------|---------------|-------------|
| 10 | Local business discovery | Blend text relevance with proximity | `bool` + `geo_distance` + distance-aware ranking |
| 11 | Location-name query support | Human input to geo primitives | Polygon resolver + two-stage narrowing |
| 12 | Search-visible ratings | Fast reads without runtime aggregation | Write-time aggregates + async projection |
| 13 | One-review constraint | Correctness under retries and duplicates | OLTP unique key + idempotent writes |
