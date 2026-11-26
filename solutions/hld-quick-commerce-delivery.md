# 🏆 Coach Answer: Quick Commerce Delivery — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional

1. Query deliverable items by location.
2. Place multi-item order.
3. Reflect nearby-center inventory status.

### Non-Functional

| Metric | Target |
|---|---|
| Availability lookup latency | < 100 ms P99 |
| Order create latency | < 800 ms P99 |
| Inventory correctness | Strong on commit |
| Availability consistency | Bounded staleness acceptable |

### Out of Scope

- Driver dispatch internals.
- Payment internals.

---

## Phase 2 — Capacity (5 min)

- Availability requests are read-heavy (10x-20x order volume).
- Regional hotspots dominate load shape.
- Peak scale determined by neighborhood-level burst patterns.

---

## Phase 3 — APIs (5 min)

```http
GET /api/v1/availability?lat=...&lng=...&q=...
POST /api/v1/orders
GET /api/v1/orders/{orderId}
```

Use idempotency key for order requests.

---

## Phase 4 — Data Model (5 min)

- `FulfillmentCenter(center_id, geo, region)`
- `Inventory(center_id, item_id, available_qty, reserved_qty, version)`
- `Order(order_id, user_id, center_id, status)`
- `OrderLine(order_id, item_id, qty)`

---

## Phase 5 — Architecture (10 min)

- Geo resolver for nearby centers.
- Cache-first availability service.
- Reservation/order service with transaction or OCC.
- Event pipeline for downstream notifications/analytics.

Separate read and write paths by design.

---

## Phase 6 — Deep Dives (10 min)

1. **Inventory correctness:** transactional decrement or versioned OCC.
2. **Cache invalidation:** freshness budget and fallback policy.
3. **Regional failover:** degrade reads and protect write correctness.

---

## Phase 7 — Trade-Off Wrap (5 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Read path | Cache-first with bounded staleness | Always DB reads | Meets strict latency targets |
| Write path | Strong consistency | Async decrement | Prevents oversell |
| Partitioning | Region-local ownership | Global writes | Better locality and isolation |

### Follow-Up Extensions

1. Substitution logic.
2. Scheduled delivery windows.
3. Traffic/weather-adjusted SLA routing.
