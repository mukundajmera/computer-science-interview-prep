# 🏆 Coach Answer: Brokerage Platform — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional

1. Live quotes.
2. Submit orders.
3. Cancel orders.
4. Track order status.

### Non-Functional

| Metric | Target |
|---|---|
| Quote latency | < 500ms |
| Order command latency | < 300ms |
| Order correctness | Strong |
| Availability | 99.95%+ |

---

## Phase 2 — Capacity (5 min)

- 20M DAU.
- 5M+ orders/day.
- 100K+ concurrent quote subscribers around market open.

---

## Phase 3 — APIs (5 min)

```http
GET /api/v1/symbols/{symbol}/quote
POST /api/v1/orders
POST /api/v1/orders/{orderId}/cancel
GET /api/v1/orders/{orderId}
```

---

## Phase 4 — Data Model (5 min)

- `Order(order_id, user_id, symbol, side, type, qty, state, idempotency_key)`
- `OrderEvent(event_id, order_id, type, source, ts)`

---

## Phase 5 — Architecture (10 min)

- Quote fanout path optimized for low latency.
- Order command path optimized for correctness and replay safety.
- Exchange adapter boundary with reconciliation worker.

---

## Phase 6 — Deep Dives (10 min)

1. Idempotency and duplicate submit prevention.
2. External ack ambiguity handling.
3. Reconciliation for state drift.

---

## Phase 7 — Trade-Off Wrap (5 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Quote delivery | WebSocket | Polling | Lower latency fanout |
| Order consistency | Strong transitions | Eventual | Financial correctness |
| Recovery | Reconcile + replay | Best effort | Handles partial failures |
