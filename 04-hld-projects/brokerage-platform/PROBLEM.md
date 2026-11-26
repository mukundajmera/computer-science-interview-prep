# Brokerage Trading Platform

## Problem Statement

Design a brokerage platform that shows near-real-time prices and lets users place or cancel orders while maintaining strict order-state correctness when communicating with external exchanges.

---

## Requirements and Constraints

### Functional Requirements

1. Users can view live prices for tracked symbols.
2. Users can submit market and limit orders.
3. Users can cancel open orders.
4. Users can view order status transitions in near real time.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Price update latency | < 500 ms P99 |
| Order submit/cancel latency | < 300 ms P99 |
| Consistency (orders) | Strong |
| Availability (price feed) | 99.99% |
| Availability (order path) | 99.95% |

### Capacity Assumptions

- 20M DAU.
- 5M+ orders/day.
- 100K+ concurrent websocket subscribers during market open.
- Highly bursty traffic around open, close, and major news events.

### Out of Scope

- Portfolio recommendation models.
- Clearing/settlement internals.
- Tax reporting details.

---

## High-Level Design Outline

### Core Services

- API Gateway
- Market Data Ingestion and Fanout Service
- Order Command Service
- Exchange Adapter Service
- Order State Store and Reconciliation Worker

### API Surface (Illustrative)

```http
GET /api/v1/symbols/{symbol}/quote
POST /api/v1/orders
POST /api/v1/orders/{orderId}/cancel
GET /api/v1/orders/{orderId}
```

---

## Scoring Rubric (Quick Signals)

1. Clear brokerage-versus-exchange boundary.
2. Durable order state machine with idempotency.
3. Correct trade-off between low-latency fanout and reliable command processing.
4. Failure reconciliation for partial external exchange failures.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Treating external exchange APIs as always reliable.
- Using eventual consistency for order ownership or final order state.
- Coupling market-data fanout path with order mutation path.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How do we support pre-market and after-hours behavior?
- How do we reduce fanout cost for large watchlists?
- How do we fail over if one exchange adapter degrades?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Multi-exchange routing policy.
- Fractional share orders.
- Conditional orders (stop/stop-limit).

---

## Related Links

- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/real-time-updates](../../03-hld-concepts/real-time-updates/)
- [03-hld-concepts/contention-control](../../03-hld-concepts/contention-control/)
- [03-hld-concepts/workflow-orchestration](../../03-hld-concepts/workflow-orchestration/)
