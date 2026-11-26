# E-commerce Backend — Interview Scoring Rubric

A structured rubric for evaluating E-commerce Backend system design interviews across 7 dimensions, each scored from 1 (Poor) to 5 (Strong).

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|-----------|--------|------------|
| 1 | Requirements Gathering | 10% | Clarifying questions, scope definition |
| 2 | Back-of-Envelope Estimation | 10% | Traffic, storage, bandwidth math |
| 3 | API Design | 15% | RESTful endpoints, idempotency, error handling |
| 4 | Data Model | 15% | Schema, relationships, partitioning strategy |
| 5 | Architecture | 20% | Components, data flow, high-level diagram |
| 6 | Deep Dives | 20% | Inventory management, checkout flow, flash sale handling, payment processing |
| 7 | Trade-offs & Communication | 10% | Pros/cons, justification, clear explanation |

---

## 1. Requirements Gathering

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Jumps straight into design without asking questions. Treats the system as a single monolithic CRUD app. Does not distinguish between buyer and seller flows. |
| **3 — Acceptable** | Asks about DAU, product catalog size, order volume, and peak traffic (flash sales). Identifies core flows (browse, cart, checkout, payment). Mentions availability and latency targets. |
| **5 — Strong** | Systematically clarifies scope: 50M DAU, 100M products, 10M orders/day, 50K peak orders/sec during flash sales. Separates buyer-facing (browse, search, cart, checkout) from seller-facing (listing, inventory, fulfillment) flows. Explicitly lists what is out of scope (e.g., delivery logistics, customer support chat). Defines non-functional requirements with specific numbers: 99.99% availability, < 200 ms search latency, < 500 ms checkout latency, strong consistency for inventory and payments. |

---

## 2. Back-of-Envelope Estimation

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Provides no numbers or wildly inaccurate estimates. Cannot convert daily order volume to orders/sec. Skips storage sizing entirely. |
| **3 — Acceptable** | Calculates orders/sec (~115 avg, ~50K peak during flash sales). Provides a rough storage estimate for the product catalog. Mentions cache sizing for product pages. |
| **5 — Strong** | Derives all key figures methodically: 10M orders/day ≈ 115 orders/sec avg, 50K/sec peak (flash sale). Product search: 50M DAU × 20 searches/day = 1B searches/day ≈ 12K searches/sec (peak ~50K/sec). Product pages: 100M products × 5 KB avg = 500 GB catalog data. Order records: 10M/day × 2 KB = 20 GB/day, ~7 TB/year. Cart data: 50M DAU × 3 items avg × 200 bytes = 30 GB active carts in Redis. Payment throughput: 10M transactions/day ≈ 115 TPS avg. Notes 500:1 read-to-write ratio for product catalog. |

---

## 3. API Design

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Vague or missing API definition. No mention of idempotency for payment/order endpoints. Lumps all functionality into a few generic endpoints. |
| **3 — Acceptable** | Defines endpoints for product search, product detail, cart operations, and checkout. Mentions appropriate HTTP methods and status codes. Includes pagination for search results. |
| **5 — Strong** | Provides versioned REST endpoints with complete request/response payloads across all domains. Product: `GET /api/v1/products?q=&category=&page=` (200), `GET /api/v1/products/{id}` (200). Cart: `POST /api/v1/cart/items` (201), `PUT /api/v1/cart/items/{id}` (200), `DELETE /api/v1/cart/items/{id}` (204). Checkout: `POST /api/v1/orders` with idempotency key header (201). Payment: `POST /api/v1/payments` with idempotency key (201). Lists error codes (400, 402, 404, 409, 422, 429) with clear semantics. Discusses idempotency for order creation and payment processing. Mentions optimistic locking for cart updates and API rate limiting per user. |

---

## 4. Data Model

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No schema defined or only describes fields informally. No discussion of database choice per domain. Treats products, orders, and inventory as a single table. |
| **3 — Acceptable** | Defines separate tables for products, users, carts, orders, and order items. Chooses appropriate database types (SQL for orders, NoSQL for catalog) with brief rationale. Mentions indexing on product category and user ID. |
| **5 — Strong** | Presents a complete domain-driven schema: Product (id, seller_id, title, description, price, category, attributes JSONB, status, created_at), Inventory (product_id, warehouse_id, quantity, reserved, version), Cart (user_id → items list in Redis), Order (order_id, user_id, status, total, created_at), OrderItem (order_id, product_id, quantity, price_at_purchase), Payment (payment_id, order_id, amount, status, idempotency_key, provider_ref). Justifies polyglot persistence: Elasticsearch for product search, PostgreSQL for orders/payments (ACID), Redis for carts and sessions, DynamoDB/Cassandra for product catalog reads. Explains inventory versioning for optimistic concurrency control. Defines partition keys and sharding strategy (order_id hash for orders, product_id for catalog). |

---

## 5. Architecture

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Draws a single box or lists components without showing data flow. Misses critical services (inventory, payment). No distinction between read and write paths. |
| **3 — Acceptable** | Shows a layered diagram: clients → CDN → load balancer → API gateway → microservices → databases. Identifies at least 4 services (product, cart, order, payment). Describes the checkout flow at a high level. |
| **5 — Strong** | Draws a complete microservices architecture: CDN → API Gateway (auth, rate limiting) → service mesh with Product Service (Elasticsearch + catalog DB), Inventory Service (PostgreSQL with row-level locking), Cart Service (Redis cluster), Order Service (PostgreSQL, saga orchestrator), Payment Service (idempotent, external gateway integration), Notification Service (async via message queue). Separates read path (CDN → cache → catalog) from write path (cart → order → inventory reservation → payment → confirmation). Includes an event bus (Kafka) for inter-service communication. Shows async flows: order events → inventory update, payment confirmation → order status update, order completion → notification. Addresses flash sale architecture with a queue-based admission control layer. |

---

## 6. Deep Dives

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Cannot explain how inventory is kept consistent during concurrent purchases. No mention of payment idempotency. Treats flash sales as regular traffic. |
| **3 — Acceptable** | Describes inventory reservation at checkout with a basic locking mechanism. Mentions payment idempotency keys. Aware that flash sales cause traffic spikes but offers only surface-level solutions (e.g., "add more servers"). |
| **5 — Strong** | **Inventory management:** Explains two-phase inventory model (available → reserved → committed) with optimistic concurrency control (`UPDATE inventory SET available = available - qty WHERE available >= qty AND version = v`). Discusses TTL-based reservation release for abandoned checkouts. **Checkout flow:** Details the saga pattern — reserve inventory → create order → process payment → confirm order. Handles partial failures with compensating transactions (payment fails → release reservation). **Flash sale handling:** Queue-based admission control: user requests enter a virtual queue → token bucket limits concurrent checkout to 50K/sec → overflow gets "please wait" with position. Pre-warms caches, pre-generates inventory tokens for flash items. **Payment processing:** Idempotency keys prevent double-charges. Two-phase: authorize → capture after shipping. Handles gateway timeouts with reconciliation jobs. Discusses PCI compliance boundary (tokenization, never store raw card data). |

---

## 7. Trade-offs & Communication

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Makes design choices without explaining why. Cannot articulate alternatives or downsides. Answers are disorganized and hard to follow. |
| **3 — Acceptable** | Explains at least two trade-offs (e.g., SQL vs NoSQL for orders, synchronous vs async checkout). Communicates the design in a logical order. Responds to interviewer follow-ups adequately. |
| **5 — Strong** | Proactively surfaces trade-offs at each decision point: strong consistency for inventory vs availability (chose CP for inventory, AP for catalog), synchronous payment vs async (chose sync authorize with async capture), monolith vs microservices (chose microservices for independent scaling of search vs checkout), SQL vs NoSQL per domain. Articulates the evolution path (v1 monolith → v2 service-oriented with caching → v3 event-driven microservices with flash sale infrastructure). Communicates clearly, uses diagrams, and structures the answer with time awareness. Wraps up by summarizing key decisions and open questions. |

---

## Quick Calibration Guide

| Total Score (out of 35) | Rating | Recommendation |
|--------------------------|--------|----------------|
| 30–35 | 🟢 Strong Hire | Exceeds expectations across all dimensions |
| 22–29 | 🟡 Hire | Solid fundamentals, minor gaps in depth |
| 15–21 | 🟠 Lean No Hire | Acceptable basics but missing key deep dives |
| 7–14 | 🔴 No Hire | Significant gaps in design thinking |

---

*Use this rubric alongside the [STRONG-ANSWER](./STRONG-ANSWER.md) for calibration and [PITFALLS](./PITFALLS.md) to identify common failure modes.*
