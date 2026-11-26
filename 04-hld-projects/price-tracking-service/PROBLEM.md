
# Price Tracking Service

## Problem Statement

Design a product price tracking platform that ingests observed prices, stores history, and triggers threshold alerts.

---

## Requirements and Constraints

### Functional Requirements

1. Store historical price points for tracked products
2. Subscribe for price-drop alerts
3. Serve low-latency price history

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Query latency | < 500 ms P95 |
| Alert delay | < 1 hour |
| Availability | 99.9% |
| Scale | Hundreds of millions of products |

### Out of Scope

- Full recommendation/ads internals.
- Back-office analytics tooling.
- Third-party billing and compliance details.

---

## High-Level Design Outline

- API Gateway + stateless app tier
- Domain service layer
- Cache + durable primary store
- Async pipeline for fanout/indexing/notifications
- Monitoring, alerting, and replay controls

### Sample APIs

```http
POST /api/v1/subscriptions
GET /api/v1/products/{productId}/prices
POST /api/v1/collectors/price-events
GET /api/v1/subscriptions/{subscriptionId}
```

---

## Scoring Rubric

- Requirement framing and boundary definition
- Capacity assumptions tied to architecture
- Correct consistency model on critical operations
- Clear failure handling and degraded mode

See [RUBRIC](./RUBRIC.md).

## Common Pitfalls

See [PITFALLS](./PITFALLS.md).

## Follow-Up Questions

See [FOLLOW-UPS](./FOLLOW-UPS.md).

## Variants and Extensions

- Global multi-region rollout.
- Cost-optimized variant with relaxed freshness.
- Compliance-first variant with stricter audit rules.

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/write-scaling](../../03-hld-concepts/write-scaling/)
- [03-hld-concepts/workflow-orchestration](../../03-hld-concepts/workflow-orchestration/)
- [03-hld-concepts/time-series-databases](../../03-hld-concepts/time-series-databases/)
- [solutions/hld-price-tracking-service.md](../../solutions/hld-price-tracking-service.md)
