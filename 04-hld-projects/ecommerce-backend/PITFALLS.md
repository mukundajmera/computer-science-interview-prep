# E-commerce Backend — Common Interview Pitfalls

The top 7 mistakes candidates make in an E-commerce Backend system design interview, why each is a problem, and what the interviewer actually expects.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## 1. Ignoring Inventory Consistency (Overselling)

### ❌ The Mistake

Treating inventory as a simple decrement (`stock -= 1`) without addressing race conditions. During a flash sale with 50K concurrent requests for the same item, this approach oversells massively — selling 500 units when only 100 exist.

### 🎯 What the Interviewer Expects

- Explain the **two-phase inventory model:** `available → reserved → committed`. A checkout *reserves* stock (atomic decrement with a version check), and stock is *committed* only after payment succeeds.
- Use **optimistic concurrency control:** `UPDATE inventory SET available = available - qty, reserved = reserved + qty WHERE product_id = ? AND available >= qty AND version = ?`.
- Handle reservation expiry: if checkout is abandoned, a background job or TTL releases reserved stock back to available after 10–15 minutes.
- Discuss the alternative: **pessimistic locking** (SELECT FOR UPDATE) works for low contention but creates a bottleneck during flash sales. Optimistic locking with retries is preferred for high concurrency.

### 💡 Tip

Inventory consistency is *the* defining challenge of e-commerce design. If you get nothing else right, get this right. Draw the state machine: `available → reserved → committed → (shipped)` and `reserved → released (on timeout/cancel)`.

---

## 2. Not Handling Flash Sale Traffic Spikes

### ❌ The Mistake

Designing for average load (115 orders/sec) and assuming the system will "auto-scale" during a flash sale that generates 50K orders/sec — a 400× spike. Auto-scaling cannot provision hundreds of servers in seconds.

### 🎯 What the Interviewer Expects

- **Admission control:** Place a virtual queue or token-bucket in front of the checkout service. Only N users (e.g., 50K) can enter checkout simultaneously; overflow receives a "You're in line, position #X" response.
- **Pre-warming:** Before the sale, pre-warm CDN caches for the flash product pages, pre-load inventory into Redis, and pre-scale API servers and databases.
- **Separation of concerns:** Flash sale product pages should be served from a dedicated, static-content CDN path — not hit the general product service.
- **Inventory tokens:** For limited items (100 units), pre-generate 100 "purchase tokens" in Redis. Acquiring a token (`DECR`) is O(1) and atomic. Users without a token get "Sold Out" instantly.
- **Graceful degradation:** If downstream services (payment, notification) slow down, the system must not cascade-fail. Use circuit breakers and async processing where possible.

### 💡 Tip

Flash sale handling is often the follow-up that separates "Hire" from "Strong Hire." Prepare a concrete strategy with numbers — don't just say "we'll scale up."

---

## 3. Missing Cart Persistence and Consistency

### ❌ The Mistake

Storing cart data only in the browser (localStorage) or treating it as a stateless concern. Users expect their cart to persist across devices and sessions, and prices/availability must reflect reality at checkout time.

### 🎯 What the Interviewer Expects

- **Server-side carts:** Store active carts in Redis (keyed by `user_id`), with a write-through to a persistent store (DynamoDB or PostgreSQL) for durability.
- **Cart merging:** When a guest user logs in, merge their anonymous cart (tracked by session ID) with their authenticated cart, resolving conflicts (e.g., same item in both — take the higher quantity or prompt the user).
- **Price and availability validation:** At checkout time, re-validate every cart item against current price and inventory. Don't trust the price stored in the cart from hours ago.
- **Cart expiration:** Abandon carts after 30 days of inactivity to reclaim storage. Send reminder emails at 24h and 7d.

### 💡 Tip

Mention the guest-to-authenticated cart merge — it's a detail most candidates miss, and interviewers notice.

---

## 4. No Payment Idempotency

### ❌ The Mistake

Processing payment as a simple `POST /pay` without handling retries. If the network times out after the payment gateway charges the card but before the server records the response, the user retries and gets double-charged.

### 🎯 What the Interviewer Expects

- **Idempotency key:** Every payment request includes a client-generated `Idempotency-Key` header (typically the `order_id`). The server stores the key and result; duplicate requests return the cached result without re-processing.
- **Two-phase payment:** Authorize the card at checkout (hold funds) → Capture after order fulfillment (charge funds). This separates "can the user pay?" from "we're actually charging."
- **Gateway timeout handling:** If the payment gateway doesn't respond within the timeout, do not retry blindly. Instead, run a **reconciliation job** that queries the gateway for the transaction status and updates the order accordingly.
- **PCI compliance boundary:** Never store raw card numbers. Use tokenization (Stripe/Braintree tokens) and keep the PCI scope limited to the payment gateway. The e-commerce backend only handles tokens.

### 💡 Tip

State the idempotency strategy explicitly and early. It signals awareness of distributed systems failure modes — something interviewers specifically probe for.

---

## 5. Ignoring Search and Catalog Scale

### ❌ The Mistake

Proposing `SELECT * FROM products WHERE title LIKE '%keyword%'` for a catalog of 100M products. This is a full table scan that takes seconds, cannot rank results by relevance, and doesn't support faceted filtering (brand, price range, ratings).

### 🎯 What the Interviewer Expects

- **Elasticsearch** (or Solr) as the primary search engine, separate from the product database. Products are indexed asynchronously via an event pipeline (product created/updated → Kafka → Elasticsearch indexer).
- **Search features:** Full-text search with relevance scoring (BM25), autocomplete (prefix suggestions), faceted navigation (category, brand, price range, rating), and personalization (boost items based on user history).
- **Read path for product pages:** CDN for static assets → Redis/Memcached for product detail JSON → catalog database as the source of truth.
- **Catalog write path:** Seller updates product → write to catalog DB → publish event → Elasticsearch re-indexes → CDN cache invalidated.
- **Scale numbers:** 100M products × 5 KB avg = 500 GB index. Elasticsearch cluster: 5–10 nodes with sharding and replicas handles 50K search queries/sec.

### 💡 Tip

Explicitly call out that search is a separate subsystem. This shows you understand domain decomposition, not just CRUD.

---

## 6. Overlooking the Order State Machine

### ❌ The Mistake

Modeling order status as a free-form string field that can be set to any value. This leads to invalid transitions (e.g., jumping from "created" to "delivered"), lost states, and no auditability.

### 🎯 What the Interviewer Expects

- Define a **finite state machine** for orders with explicit transitions:

```
CREATED → PAYMENT_PENDING → PAID → PROCESSING → SHIPPED → DELIVERED
                ↓                      ↓
            PAYMENT_FAILED         CANCELLED
                                       ↓
                                   REFUNDED
```

- **Every transition is an event** recorded in an `order_events` table (event sourcing or at minimum an audit log): `(order_id, from_status, to_status, timestamp, actor, metadata)`.
- **Saga orchestration:** The order service orchestrates the checkout saga — reserve inventory → process payment → confirm order. Each step has a compensating action (payment failed → release inventory).
- **Concurrency protection:** Use optimistic locking on the order status field to prevent race conditions (e.g., two concurrent requests both trying to cancel and ship the same order).

### 💡 Tip

Draw the state diagram on the whiteboard. It takes 30 seconds and immediately demonstrates structured thinking about the most complex entity in the system.

---

## 7. Not Addressing Multi-Vendor / Marketplace Concerns

### ❌ The Mistake

Designing the system as if a single company owns all products. In reality, Amazon-scale platforms are marketplaces with millions of third-party sellers, each with their own inventory, pricing, and fulfillment.

### 🎯 What the Interviewer Expects

- **Multi-tenancy:** Products belong to a `seller_id`. Inventory is partitioned by seller and warehouse. Pricing is seller-controlled with platform guardrails (minimum margin, price-gouging detection).
- **Order splitting:** A single cart may contain items from multiple sellers. At checkout, the order is split into **sub-orders** per seller, each with its own fulfillment lifecycle.
- **Payment splitting:** The platform collects the full payment, then disburses to each seller minus the platform commission. This requires a **ledger system** tracking: customer payment → platform escrow → seller payout.
- **Seller APIs:** Sellers need APIs/dashboards for listing products, managing inventory, viewing orders, and tracking payouts. This is a separate service boundary.
- **Trust and quality:** Seller ratings, product reviews, and return policies vary by seller. The platform aggregates quality signals to rank sellers in search results.

### 💡 Tip

Even if the interviewer doesn't explicitly mention "marketplace," acknowledging multi-vendor concerns shows you understand Amazon-scale complexity. A brief mention of sub-orders and payment splitting is enough.

---

## Summary Table

| # | Pitfall | What's Missing | Scoring Impact |
|---|---------|---------------|----------------|
| 1 | No inventory consistency | Race condition handling, overselling prevention | Deep Dives dimension: -3 to -4 points |
| 2 | No flash sale strategy | Admission control, pre-warming, graceful degradation | Deep Dives dimension: -2 to -3 points |
| 3 | No cart persistence | Cross-device sync, guest merge, price revalidation | Data Model dimension: -1 to -2 points |
| 4 | No payment idempotency | Double-charge prevention, gateway timeout handling | Deep Dives dimension: -2 to -3 points |
| 5 | No search architecture | Full-text search, faceted navigation, catalog scale | Architecture dimension: -2 to -3 points |
| 6 | No order state machine | Status transitions, saga orchestration, audit trail | Data Model dimension: -2 to -3 points |
| 7 | No multi-vendor design | Sub-orders, payment splitting, seller isolation | Architecture dimension: -1 to -2 points |

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

## 11. Treating Geospatial Search as a Plain SQL Problem

### ❌ The Mistake

Using wildcard text search plus crude latitude/longitude range checks as the primary local discovery path for business search.

### 🎯 What the Interviewer Expects

- Separate OLTP product/business storage from search projection.
- Use Elasticsearch geospatial primitives (`geo_point`, `geo_distance`) for radius constraints.
- Combine text relevance with distance-aware ranking instead of sorting by distance only.
- Address edge behavior: dense downtown zones, sparse rural zones, and adaptive search radius.

### 💡 Tip

State the query shape explicitly: text relevance in `must`, business constraints in `filter`, distance scoring in `function_score`.

## 12. Calculating Average Rating at Query Time

### ❌ The Mistake

Computing per-business average rating during each search request by aggregating raw reviews.

### 🎯 What the Interviewer Expects

- Maintain denormalized aggregates (`rating_sum`, `rating_count`, `avg_rating`) on write path.
- Update search index asynchronously from aggregate changes.
- Use periodic reconciliation to repair projection drift.
- Clarify consistency: slight delay in rating updates is acceptable; correctness must converge.

### 💡 Tip

Interviewers reward designs that keep read paths cheap and predictable, even if write paths become more deliberate.

## 13. Enforcing One-Review-Per-User in the Search Index

### ❌ The Mistake

Trying to enforce review uniqueness directly in Elasticsearch or application memory.

### 🎯 What the Interviewer Expects

- Enforce `(business_id, user_id)` uniqueness in OLTP source-of-truth database.
- Make review create endpoint idempotent for retry safety.
- Treat Elasticsearch as projection/search layer only.
- Define duplicate behavior clearly: conflict response or update-existing review workflow.

### 💡 Tip

When a requirement is a hard invariant, enforce it in the transactional store, not in eventually consistent projections.
