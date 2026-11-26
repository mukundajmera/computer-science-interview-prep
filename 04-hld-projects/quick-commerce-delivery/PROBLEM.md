# Quick Commerce Delivery Platform

## Problem Statement

Design a quick-commerce platform backend that answers location-based item availability and places orders from nearby micro-fulfillment centers with strong inventory correctness.

---

## Requirements and Constraints

### Functional Requirements

1. Users can query items deliverable to a location within a target SLA (for example, one hour).
2. Users can place orders for multiple items in a single checkout.
3. Availability reflects nearby fulfillment center inventory, not just catalog entries.
4. System returns substitute/unavailable statuses when stock is insufficient.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability query latency | < 100 ms P99 |
| Order placement latency | < 800 ms P99 |
| Consistency (inventory decrement) | Strong |
| Availability consistency | Eventual acceptable |
| Availability (read path) | 99.99% |
| Availability (order path) | 99.95% |

### Capacity Assumptions

- 20K availability QPS at peak.
- 1K-2K order create QPS at peak.
- 1K+ micro-fulfillment centers across regions.
- High read/write skew (availability queries far outnumber orders).

### Out of Scope

- Payment internals.
- Driver dispatch/routing optimization.
- Catalog editorial workflows.

---

## High-Level Design Outline

### Services

- API Gateway
- Availability Service
- Nearby Fulfillment Service
- Inventory Service
- Order Service
- Reservation/Lock Service

### Data Stores

- SQL store for orders and transactional inventory updates.
- Redis for short-lived availability cache.
- Geo index for nearest-center resolution.

### API Surface (Illustrative)

```http
GET /api/v1/availability?lat=...&lng=...&q=...&page=...
POST /api/v1/orders
GET /api/v1/orders/{orderId}
```

---

## Scoring Rubric (Quick Signals)

1. Correct distinction between item catalog and location inventory.
2. Fast availability path with bounded staleness.
3. Strong consistency for reservation/decrement flow.
4. Regional partitioning and hot-key mitigation.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Treating availability as a pure catalog search problem.
- Running availability and ordering on one shared bottleneck path.
- No lock/version control in inventory decrement.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How to include traffic-aware delivery windows?
- How to support substitution rules at checkout?
- How to handle region outage during high demand?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Scheduled delivery windows.
- Dynamic SLA estimation by demand and weather.
- Category-level merchandising constraints.

---

## Related Links

- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/caching](../../03-hld-concepts/caching/)
- [03-hld-concepts/database-sharding](../../03-hld-concepts/database-sharding/)
- [03-hld-concepts/redis](../../03-hld-concepts/redis/)
- [04-hld-projects/ride-sharing](../ride-sharing/)
- [04-hld-projects/ecommerce-backend](../ecommerce-backend/)
