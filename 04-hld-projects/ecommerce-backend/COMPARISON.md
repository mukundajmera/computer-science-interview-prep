# E-commerce Backend — System Comparison

How the E-commerce Backend compares to related systems: a marketplace (eBay), a food delivery platform (DoorDash), and a ticket booking system (Ticketmaster). Understanding these parallels strengthens your ability to discuss trade-offs and reuse patterns across interviews.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## E-commerce Backend vs Marketplace (eBay)

eBay is an auction-based marketplace where sellers list items and buyers bid or purchase. An Amazon-style e-commerce backend focuses on fixed-price, high-throughput catalog purchases. Both handle multi-vendor selling, but the buying mechanics differ fundamentally.

| Dimension | E-commerce Backend (Amazon) | Marketplace (eBay) | Key Difference |
|-----------|---------------------------|---------------------|----------------|
| **Buying model** | Fixed price, instant purchase | Auction-based (bidding) + Buy It Now | Auctions need real-time bid tracking and countdown timers; e-commerce is a simpler add-to-cart flow |
| **Inventory model** | Warehouse-managed, quantity-based stock | Mostly single-item listings (one seller, one item) | E-commerce tracks stock counts per SKU per warehouse; eBay listings are predominantly unique items |
| **Pricing** | Seller sets fixed price, platform enforces policies | Dynamic (bidding drives price), with reserve prices | Auction systems need real-time price updates pushed to all watchers via WebSockets |
| **Catalog structure** | Centralized catalog with shared product pages (many sellers → one product) | Each listing is unique, even for the same product | Amazon merges seller offers onto one product page; eBay has millions of individual listing pages |
| **Search complexity** | Structured catalog with facets (brand, category, price range, ratings) | Unstructured listings, title-based search, condition filters (new, used) | eBay search must handle highly variable listing quality; Amazon search can rely on structured product attributes |
| **Fulfillment** | Platform-managed (FBA) or seller-shipped | Exclusively seller-shipped | Amazon's FBA model requires warehouse management systems; eBay delegates logistics entirely |
| **Trust mechanism** | Product reviews + seller ratings | Seller reputation (feedback score), buyer protection | eBay's feedback system is bidirectional (buyers rate sellers AND sellers rate buyers) |
| **Payment flow** | Immediate charge (authorize at checkout, capture at shipment) | Auction: charge winner after auction ends; Buy It Now: immediate | Auction payments are deferred, adding a "winner notification → payment collection" step |

### Shared Patterns

- Both are **multi-vendor platforms** requiring seller onboarding, product listing APIs, and payment splitting.
- Both need **search at scale** with relevance ranking and filtering.
- Both implement **buyer protection programs** (refunds, disputes, fraud detection).
- Both use **event-driven architectures** for order state changes and notifications.

---

## E-commerce Backend vs Food Delivery Platform (DoorDash)

DoorDash connects restaurants, drivers, and customers in a real-time, time-sensitive delivery network. An e-commerce backend sells physical goods with hours-to-days delivery. Both process orders and payments, but the real-time matching and perishability constraints differ dramatically.

| Dimension | E-commerce Backend (Amazon) | Food Delivery (DoorDash) | Key Difference |
|-----------|---------------------------|--------------------------|----------------|
| **Order lifecycle** | Minutes to days (place → ship → deliver in 1–7 days) | Minutes (~30 min from order to delivery) | Food delivery operates on a 30-minute SLA; every system must be optimized for real-time |
| **Inventory** | Pre-stocked in warehouses, countable SKUs | Menu items with real-time availability (restaurant can 86 an item mid-shift) | E-commerce inventory is deterministic and pre-counted; restaurant availability is fluid and reported in real-time |
| **Supply-side matching** | No real-time matching; warehouses fulfill asynchronously | Real-time driver-order matching (assignment algorithm) | DoorDash must solve a dynamic assignment problem: which driver, which route, which batch of orders |
| **Perishability** | Non-perishable goods (mostly) | Food degrades in quality within minutes | Food delivery optimizes for speed and freshness; e-commerce optimizes for cost and accuracy |
| **Pricing model** | Fixed product prices + shipping cost | Base price + delivery fee + service fee + surge pricing | DoorDash has dynamic pricing based on demand, distance, and driver availability |
| **Geographic scope** | Global (ship anywhere) | Hyper-local (5–10 mile delivery radius per restaurant) | DoorDash's architecture is partitioned by metro area; e-commerce is partitioned by warehouse region |
| **Peak patterns** | Flash sales (planned), holiday seasons | Meal times (lunch, dinner) — daily recurring peaks | DoorDash peak is predictable and recurring; e-commerce flash sales are episodic and more extreme |
| **Cancellation impact** | Low cost (restock item) | High cost (food already prepared, driver en route) | Food delivery cancellations have immediate financial loss; e-commerce cancellations are simpler to reverse |

### Shared Patterns

- Both orchestrate **multi-party transactions** (buyer, seller/restaurant, and optionally a logistics provider).
- Both require **real-time order status tracking** (where's my order/food).
- Both use **payment processing with tip/commission splitting** across multiple parties.
- Both need **search and discovery** (product search vs restaurant/menu search).
- Both employ **notification systems** for order updates (push notifications, SMS, email).

---

## E-commerce Backend vs Ticket Booking System (Ticketmaster)

Ticketmaster sells tickets for events (concerts, sports) where each seat is a unique, non-fungible inventory item. An e-commerce backend sells fungible goods where any unit of a SKU is interchangeable. Both face high-concurrency inventory challenges, but the constraints differ.

| Dimension | E-commerce Backend (Amazon) | Ticket Booking (Ticketmaster) | Key Difference |
|-----------|---------------------------|-------------------------------|----------------|
| **Inventory type** | Fungible (any unit of SKU-123 is the same) | Non-fungible (Seat A1 ≠ Seat A2) | Ticket systems need a seat map with per-seat availability; e-commerce tracks aggregate stock counts |
| **Concurrency challenge** | Multiple users competing for the last N units of a product | Thousands of users selecting the same seat simultaneously | Both face hot-item contention, but ticket booking has per-seat locking — a much finer granularity |
| **Inventory size** | 100M+ products, replenishable stock | Thousands of events × thousands of seats = millions of seats, but each event is ephemeral | E-commerce inventory is long-lived and restockable; ticket inventory is one-time and time-bound |
| **Reservation model** | Reserve stock → complete checkout (10–15 min timeout) | Temporary seat hold → complete purchase (2–5 min timeout, much tighter) | Ticket holds must be short to avoid blocking other buyers; e-commerce can be more lenient |
| **Pricing** | Fixed price per product (occasional discounts) | Dynamic pricing (primary sale, VIP packages, resale market) | Ticketmaster uses real-time demand-based pricing; e-commerce pricing changes less frequently |
| **Sale pattern** | Steady traffic with flash sale spikes | "Onsale" events — massive thundering herd at a single moment (millions hit "Buy" at 10:00 AM) | Ticket onsales have an even more extreme spike profile than flash sales — all demand compressed into seconds |
| **Seat selection UX** | Add to cart → checkout (simple) | Interactive seat map → select → hold → checkout (complex) | Seat selection requires real-time availability rendering of a visual seat map with WebSocket updates |
| **Post-purchase** | Shipping and delivery tracking | Digital ticket delivery, transfer, resale | Ticket systems need QR code generation, anti-counterfeiting, and a secondary resale marketplace |

### Shared Patterns

- Both require **high-concurrency inventory management** with reservation timeouts.
- Both use **queue-based admission control** for high-demand events/products.
- Both need **payment idempotency** and retry handling.
- Both employ **caching aggressively** for catalog/event information (read-heavy workloads).
- Both have **fraud prevention needs** (scalpers/bots for tickets, fake accounts for e-commerce promotions).

---

## Cross-Cutting Comparison Summary

| Concern | E-commerce (Amazon) | Marketplace (eBay) | Food Delivery (DoorDash) | Ticket Booking (Ticketmaster) |
|---------|--------------------|--------------------|--------------------------|-------------------------------|
| **Inventory type** | Fungible SKUs, quantity-based | Unique listings, mostly single-item | Menu items, fluid availability | Non-fungible seats, per-seat state |
| **Peak concurrency** | 50K orders/sec (flash sales) | 10K bids/sec (auction end) | 5K orders/sec (dinner rush) | 100K+ seat requests/sec (onsale) |
| **Consistency requirement** | Strong for inventory, eventual for catalog | Eventual for listings, strong for bids | Strong for order assignment | Strong for seat holds |
| **Order lifecycle** | Hours to days | Hours to days (+ auction period) | Minutes | Instant (digital delivery) |
| **Primary storage** | SQL (orders) + NoSQL (catalog) + Elasticsearch | SQL (listings, bids) + search index | SQL (orders) + Redis (driver state) | SQL (events, seats) + Redis (seat holds) |
| **Hardest problem** | Inventory consistency at scale | Bid consistency + auction timing | Real-time driver-order matching | Thundering herd on onsale |
| **Real-time needs** | Low (mostly async) | Medium (auction countdown, bid updates) | High (driver tracking, ETAs) | High (seat availability, queue position) |
| **Caching importance** | Critical (product pages, search) | Critical (listing pages) | Moderate (menus, restaurant info) | Critical (event pages, seat maps) |

---

## When to Reference These Comparisons

- **eBay/marketplace comes up?** Reuse your e-commerce design but replace the fixed-price cart flow with an auction engine (bid tracking, auction clock, winner determination). Add seller-side reputation and feedback.
- **DoorDash/food delivery comes up?** Keep the order and payment core, but add a real-time matching engine (driver assignment), hyper-local partitioning, and a 30-minute end-to-end SLA.
- **Ticketmaster/ticket booking comes up?** Keep the checkout and payment flow, but replace fungible inventory with a seat map, add per-seat locking with tight timeouts, and design for an even more extreme thundering herd than flash sales.

---

*See [DESIGN](./DESIGN.md) for the full E-commerce Backend architecture and [FOLLOW-UPS](./FOLLOW-UPS.md) for interview extensions that push toward these related systems.*
