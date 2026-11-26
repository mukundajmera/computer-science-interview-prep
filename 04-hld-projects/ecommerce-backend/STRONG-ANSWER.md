# E-commerce Backend — Model Answer (Time-Boxed)

Say: "I will protect the order state machine and inventory reservation path first, because checkout correctness is more important than making every catalog read strongly consistent."

A strong-answer outline for a 40-minute E-commerce Backend system design interview. Each section includes target timing and the key points an interviewer expects to hear.

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

1. "What's the expected scale — daily active users, product catalog size, and order volume?"
2. "Do we need to support flash sales? What's the peak concurrency target?"
3. "Is this a single-vendor platform or a marketplace with third-party sellers?"
4. "What payment methods do we need to support?"
5. "What's the acceptable latency for search, product pages, and checkout?"
6. "Do we need real-time inventory tracking, or is near-real-time acceptable for display?"

### Functional Requirements (confirm with interviewer)

- **Core:** Product browsing and search, shopping cart, checkout and order placement, payment processing, order tracking.
- **Seller-side:** Product listing and inventory management, order fulfillment workflow.
- **Optional:** Recommendations, reviews and ratings, returns and refunds.

### Non-Functional Requirements (state explicitly)

- **Scale:** 50M DAU, 100M products, 10M orders/day, 50K peak orders/sec during flash sales.
- **Availability:** 99.99% — downtime directly means lost revenue.
- **Latency:** Search < 200 ms, product pages < 100 ms, checkout < 500 ms.
- **Consistency:** Strong consistency for inventory and payments; eventual consistency for catalog and search.
- **Durability:** Zero tolerance for lost orders or payment records.

### Scope Boundaries

- **In scope:** Product catalog, search, cart, checkout, inventory, payments, order lifecycle.
- **Out of scope:** Delivery logistics/routing, customer support chat, seller onboarding KYC, marketing campaigns.

---

## Phase 2 — Estimation (5 min)

### Traffic

```
Orders:     10M/day ÷ 86,400 ≈ 115 orders/sec avg (50K/sec peak during flash sales)
Search:     50M DAU × 20 searches/day = 1B/day ÷ 86,400 ≈ 12K searches/sec (peak ~50K/sec)
Product views: 50M DAU × 30 views/day = 1.5B/day ≈ 17K views/sec (peak ~70K/sec)
Cart ops:   50M DAU × 5 cart actions/day = 250M/day ≈ 3K ops/sec
Read:Write ratio: ~500:1 for catalog, ~10:1 for orders
```

### Storage (1-year horizon)

```
Product catalog:  100M products × 5 KB avg = 500 GB
Product images:   100M × 5 images × 500 KB = 250 TB (object storage)
Orders:           10M/day × 2 KB × 365 = 7.3 TB/year
Order items:      10M/day × 3 items avg × 200 B × 365 = 2.2 TB/year
Search index:     100M products × 2 KB indexed fields = 200 GB (Elasticsearch)
```

### Cache

```
Active carts:     50M DAU × 30% have active carts = 15M carts × 2 KB = 30 GB (Redis)
Hot products:     Top 1M products × 5 KB = 5 GB (Redis)
User sessions:    50M × 500 B = 25 GB (Redis)
Total Redis:      ~60 GB across a cluster (easily handled by 3–5 nodes)
```

### Payment Throughput

```
Transactions:     10M/day ≈ 115 TPS avg (peak 50K TPS during flash sales)
Payment gateway:  Must support 50K authorize calls/sec during peak
```

---

## Phase 3 — API + Data Model + High-Level Design (10 min)

### API Endpoints

| Method | Endpoint | Purpose | Key Response |
|--------|----------|---------|--------------|
| `GET` | `/api/v1/products?q=&category=&page=&size=` | Search products | `200` with paginated product list, facets |
| `GET` | `/api/v1/products/{id}` | Product detail | `200` with product info, seller offers, availability |
| `POST` | `/api/v1/cart/items` | Add item to cart | `201` with updated cart |
| `PUT` | `/api/v1/cart/items/{itemId}` | Update quantity | `200` with updated cart |
| `DELETE` | `/api/v1/cart/items/{itemId}` | Remove from cart | `204` No Content |
| `POST` | `/api/v1/orders` | Place order (checkout) | `201` with order confirmation |
| `GET` | `/api/v1/orders/{id}` | Order status | `200` with order details and tracking |
| `POST` | `/api/v1/payments` | Process payment | `201` with payment confirmation |

**Error codes to mention:** `400` (invalid input), `402` (payment required/failed), `404` (not found), `409` (inventory conflict — item out of stock), `422` (validation error — price changed), `429` (rate limited).

**Idempotency:** `POST /orders` and `POST /payments` require an `Idempotency-Key` header to prevent duplicate order creation or double-charging on retries.

### Data Model

```
Table: products                          Table: inventory
─────────────────────────────            ─────────────────────────────────
product_id    UUID  (PK)                 product_id    UUID  (PK, FK)
seller_id     UUID  (FK)                 warehouse_id  UUID  (PK)
title         STRING                     available     INT
description   TEXT                       reserved      INT
price         DECIMAL                    version       INT   (optimistic lock)
category      STRING
attributes    JSONB
status        ENUM (active, inactive)
created_at    TIMESTAMP

Table: orders                            Table: order_items
─────────────────────────────            ─────────────────────────────────
order_id      UUID  (PK)                 order_item_id UUID  (PK)
user_id       UUID  (FK)                 order_id      UUID  (FK)
status        ENUM  (state machine)      product_id    UUID  (FK)
total_amount  DECIMAL                    quantity      INT
shipping_addr JSONB                      price_at_purchase DECIMAL
created_at    TIMESTAMP                  warehouse_id  UUID
updated_at    TIMESTAMP

Table: payments
─────────────────────────────
payment_id      UUID  (PK)
order_id        UUID  (FK, UNIQUE)
amount          DECIMAL
status          ENUM (authorized, captured, failed, refunded)
idempotency_key STRING  (UNIQUE)
provider_ref    STRING
created_at      TIMESTAMP
```

- **Polyglot persistence:**
  - **Elasticsearch:** Product search (full-text, facets, ranking).
  - **PostgreSQL:** Orders, payments, inventory (ACID transactions).
  - **Redis:** Carts, sessions, hot product cache, inventory token counters.
  - **DynamoDB/Cassandra:** Product catalog reads (high-throughput, eventually consistent).
  - **S3:** Product images and static assets.
- **Sharding:** Orders sharded by `hash(order_id)`. Products sharded by `hash(product_id)`. Inventory co-located with product shards.

### High-Level Architecture

```
                              ┌─────────────┐
                              │     CDN      │ (product images, static pages)
                              └──────┬───────┘
                                     │
                              ┌──────▼───────┐
        Clients ────────────► │ API Gateway   │ (auth, rate limiting, routing)
                              └──────┬───────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
     ┌────────▼─────┐     ┌─────────▼────────┐   ┌────────▼────────┐
     │Product Service│     │  Cart Service    │   │  Order Service   │
     │(search+catalog)│     │  (Redis-backed)  │   │ (saga orchestrator)│
     └───────┬──────┘     └─────────┬────────┘   └────────┬────────┘
             │                      │                      │
     ┌───────▼──────┐              │              ┌───────▼────────┐
     │ Elasticsearch │              │              │Inventory Service│
     │   Cluster     │              │              │ (reservation)   │
     └───────────────┘              │              └───────┬────────┘
                                    │                      │
                              ┌─────▼──────────────────────▼────────┐
                              │          PostgreSQL Cluster           │
                              │ (orders, payments, inventory — ACID) │
                              └──────────────┬──────────────────────┘
                                             │
                              ┌──────────────▼──────────────────────┐
                              │          Kafka Event Bus             │
                              │  (order events, inventory updates,   │
                              │   payment confirmations)             │
                              └──────────────┬──────────────────────┘
                                             │
                    ┌────────────────────────┼─────────────────┐
                    │                        │                 │
           ┌────────▼──────┐    ┌────────────▼───┐   ┌────────▼───────┐
           │Payment Service │    │Notification Svc│   │Analytics/Search│
           │(gateway integ) │    │(email, push)   │   │   Indexer      │
           └────────────────┘    └────────────────┘   └────────────────┘
```

**Read path (product search):** Client → CDN (hit?) → API Gateway → Product Service → Redis cache (hit?) → Elasticsearch → return results.

**Write path (checkout):** Client → API Gateway → Order Service → validate cart prices → Inventory Service (reserve stock) → Payment Service (authorize) → persist order → Kafka event → Notification Service (confirmation email).

---

## Phase 4 — Deep Dives (15 min)

### 4a. Inventory Management (~4 min)

**The core challenge:** 50K concurrent users trying to buy the last 100 units of a flash sale item. Naive `stock -= 1` causes massive overselling.

**Two-phase inventory model:**

```
Available → Reserved (at checkout)  → Committed (after payment)
                ↓ (timeout/cancel)
             Released (back to available)
```

**Optimistic concurrency control:**

```sql
UPDATE inventory
SET available = available - :qty,
    reserved  = reserved + :qty,
    version   = version + 1
WHERE product_id = :pid
  AND warehouse_id = :wid
  AND available >= :qty
  AND version = :current_version;

-- Rows affected = 0? → stock insufficient or concurrent update → retry or fail
```

**Reservation timeout:** A background job scans for reservations older than 15 minutes (where the order is still in `PAYMENT_PENDING`). It releases the reserved stock back to available and cancels the order.

**Flash sale optimization — inventory tokens:**
- For a limited item (1,000 units), pre-load `1,000` into a Redis counter.
- `DECR flash_item_123` is atomic and O(1). If result ≥ 0, the user has a token; proceed to checkout. If < 0, instantly return "Sold Out."
- This avoids hitting PostgreSQL entirely for the initial stock check during peak concurrency.

### 4b. Checkout Flow & Saga Orchestration (~4 min)

**The checkout is a distributed transaction** spanning multiple services. We use the **saga pattern** with an orchestrator:

```
Step 1: Validate cart (prices, availability)
   ↓ OK
Step 2: Reserve inventory (Inventory Service)
   ↓ OK                    ↓ FAIL → return error "Out of stock"
Step 3: Authorize payment (Payment Service)
   ↓ OK                    ↓ FAIL → compensate: release inventory
Step 4: Create order record (Order Service — status: PAID)
   ↓ OK                    ↓ FAIL → compensate: void payment, release inventory
Step 5: Publish OrderCreated event to Kafka
   → Notification Service sends confirmation
   → Search index removes sold-out items
   → Analytics records the sale
```

**Why not [2PC/XA atomic commit](../../03-hld-concepts/distributed-transactions/THEORY.md#2pc-in-interviews)?** 2PC blocks all participants until every node responds, which is unacceptable at 50K orders/sec. Sagas with compensating transactions provide eventual consistency with much better availability and throughput.

**Idempotency at each step:**
- Order creation: keyed on `idempotency_key` (client-generated UUID). Duplicate `POST /orders` returns the existing order.
- Payment: keyed on `order_id`. The payment gateway receives the same `order_id` and deduplicates on their side.
- Inventory reservation: keyed on `(order_id, product_id)`. Duplicate reservation attempts are no-ops.

### 4c. Flash Sale Handling (~4 min)

**Problem:** A flash sale at 8 PM drives 50K orders/sec — 400× the average rate. The system must not crash, oversell, or provide a terrible user experience.

**Architecture for flash sales:**

```
User → CDN (static flash sale page, pre-rendered)
     → API Gateway (rate limiting: 100K req/sec)
     → Queue Service (virtual waiting room)
          ↓ (admitted, position-based)
     → Inventory Token Check (Redis DECR)
          ↓ (token acquired)
     → Checkout Service (saga orchestrator)
          ↓
     → Payment + Order confirmation
```

**Pre-sale preparation (T-30 minutes):**
1. Scale API servers from 20 → 200 instances.
2. Pre-warm Redis with flash product data and inventory tokens.
3. Pre-render the product page as static HTML; deploy to CDN.
4. Open additional database connection pools.
5. Switch flash items to a dedicated inventory partition to isolate from normal traffic.

**During the sale:**
- **Virtual queue:** Users who click "Buy Now" are placed in a Redis sorted set (score = timestamp). A rate-limited consumer admits users at the target throughput (50K/sec).
- **Inventory tokens (Redis):** Pre-loaded counter. Atomic `DECR` determines eligibility in microseconds.
- **Graceful degradation:** If the Payment Service slows down, the Order Service buffers authorized orders and processes confirmations asynchronously. Users see "Order placed, confirming payment…" instead of a timeout.
- **Circuit breakers:** If any downstream service fails, the circuit opens and returns a clear error ("Please try again in 30 seconds") rather than cascading.

**Post-sale:**
- Unredeemed inventory tokens expire after 15 minutes (users who got a token but didn't complete checkout).
- Released stock goes into a second chance round.
- Scale back servers over 30 minutes as traffic normalizes.

### 4d. Payment Processing (~3 min)

**Two-phase payment flow:**

```
Checkout:    Authorize (hold $X on card) → response: auth_code
Fulfillment: Capture (charge $X using auth_code) → response: capture_id
Cancellation: Void (release hold before capture)
Return:      Refund (reverse captured amount)
```

**Why two phases?** Authorization confirms the customer can pay *before* the order is shipped. If the order is cancelled or modified, we void the hold without ever charging. This reduces chargebacks and improves customer experience.

**Idempotency implementation:**

```
Table: payment_idempotency
─────────────────────────────
idempotency_key  STRING  (PK)
order_id         UUID
status           ENUM (processing, completed, failed)
response_body    JSONB
created_at       TIMESTAMP
expires_at       TIMESTAMP (TTL: 24 hours)
```

On `POST /payments`:
1. Look up `idempotency_key`. If found and `status = completed`, return cached `response_body`.
2. If not found, insert with `status = processing` (conditional write to prevent race).
3. Call payment gateway. On success, update to `completed` with response.
4. On gateway timeout → do NOT retry immediately. A **reconciliation job** runs every 5 minutes, queries the gateway for pending transactions, and updates the order/payment accordingly.

**PCI compliance:** The e-commerce backend never sees raw card numbers. The client-side SDK (Stripe Elements, Braintree Drop-in) tokenizes the card directly with the payment provider. The backend only handles tokens: `tok_abc123` → authorize → capture.

---

## Phase 5 — Trade-offs & Wrap-up (5 min)

### Key Trade-offs to Surface

| Decision | Choice | Trade-off |
|----------|--------|-----------|
| Inventory consistency | Strong (CP) for inventory | Higher latency on writes, but prevents overselling — non-negotiable for e-commerce |
| Catalog consistency | Eventual (AP) for search/catalog | Product updates take seconds to propagate to search index; acceptable |
| Monolith vs Microservices | Microservices | Operational complexity (service mesh, distributed tracing), but allows independent scaling of search vs checkout |
| Checkout orchestration | Saga pattern | No atomic guarantees — requires compensating transactions; but far better throughput than 2PC |
| SQL vs NoSQL | Polyglot — SQL for orders/payments, NoSQL for catalog | Must manage multiple storage systems; but each is optimized for its access pattern |
| Payment timing | Authorize at checkout, capture at ship | Holds expire (typically 7 days); must capture promptly or re-authorize |
| Flash sale admission | Queue-based + inventory tokens | Not perfectly fair (network latency advantage); but prevents system overload |

### Evolution Narrative

| Version | What Changes | Handles |
|---------|-------------|---------|
| **v1-basic** | Monolith, single PostgreSQL, simple cart and checkout, Stripe integration | ~100 orders/sec, thousands of products |
| **v2-extended** | Service decomposition (product, cart, order, payment), Redis caching, Elasticsearch for search, Kafka for async events | ~5K orders/sec, millions of products |
| **v3-optimized** | Flash sale infrastructure (queue, inventory tokens, pre-warming), multi-region deployment, saga orchestration, multi-warehouse fulfillment, recommendation engine | 50K orders/sec peak, 100M products, global scale |

### Closing Statement (say this to the interviewer)

> "To summarize: we've designed an e-commerce backend serving 50M DAU with 100M products and 10M orders per day. The architecture uses microservices — Product Service backed by Elasticsearch for search, Cart Service on Redis, Order Service with saga-based checkout orchestration, and a Payment Service with idempotency guarantees. The hardest problem is inventory consistency during flash sales, which we solve with optimistic concurrency control in PostgreSQL plus Redis-based inventory tokens for O(1) stock checks at 50K/sec. Payments use a two-phase authorize/capture model with reconciliation for gateway failures. The main trade-off is choosing strong consistency for inventory and payments (we cannot oversell or double-charge) while accepting eventual consistency for catalog and search. The system evolves from a monolith MVP to a globally distributed, event-driven platform capable of handling flash sales at internet scale."

---

*See [RUBRIC](./RUBRIC.md) for how this answer maps to scoring criteria, and [PITFALLS](./PITFALLS.md) for common mistakes to avoid.*

---

## Variant Deep Dive — Yelp-Style Local Search and Reviews (Optional 5-7 min extension)

If the interviewer pivots from generic e-commerce to local business discovery, keep the same structure but swap one deep dive:

### Requirement Pivot

- Search by `term + location + category`.
- Return business cards quickly with distance and rating.
- Enforce one review per user per business.

### Data and API Changes

- Add `GET /api/v1/businesses?query=&location=&category=&page=`.
- Add `POST /api/v1/businesses/{id}/reviews`.
- Add OLTP uniqueness on `(business_id, user_id)` for review writes.
- Add denormalized rating fields on business document for low-latency reads.

### Query Strategy

- Use Elasticsearch for combined text + geo retrieval.
- Put strict constraints in `filter` context and reserve scoring for relevance.
- Rank with weighted blend of textual score, distance decay, and quality signals (`avg_rating`, `review_count`).

### Consistency Contract

- Review writes are strongly consistent in OLTP.
- Search projection is eventually consistent with bounded freshness target (for example, under 5 seconds).
- Periodic reconciliation repairs aggregate/index drift.

### 60-Second Variant Close

> "For local business discovery, I keep review correctness in OLTP with a unique `(business_id, user_id)` constraint, and project denormalized business search documents to Elasticsearch. Query latency stays low because ratings are pre-aggregated on write path, and relevance blends text match, distance, and quality signals."
