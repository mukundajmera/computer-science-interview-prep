# Payment System

## Problem Statement

Design a payment processing platform for merchant intents, transaction processing, status updates, and durable audit trails.

---

## Requirements and constraints

### Functional requirements
1. Create payment intents for merchant checkout sessions with amount, currency, customer, and merchant metadata.
2. Confirm authorization, capture funds, and process partial/full refunds through gateway adapters.
3. Accept asynchronous gateway webhooks and reconcile unknown or delayed outcomes.
4. Expose customer/merchant status queries for payment intent, transaction, refund, and settlement state.
5. Provide operator visibility into failed captures, duplicate-key rejections, reconciliation mismatches, and retry queues.

### Non-functional requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Throughput | 15K payment intents/sec peak, 22.5K gateway callbacks/sec peak |
| Latency | p95 < 800 ms for authorization response; p95 < 150 ms for status reads |
| Durability | No committed data loss |
| Consistency | zero double-charge invariant; eventual settlement consistency within 24h |

### Constraints
- Prefer managed primitives where possible.
- Explicitly model idempotency and replay behavior.
- Keep v1 interview scope realistic (defer non-core concerns).

### Out of scope
- Organization-specific compliance implementation details.
- Build/deploy pipeline internals.
- ML-driven anomaly/fraud models unless explicitly requested.

## API / system interface


```http
POST /api/v1/payment-intents
POST /api/v1/payment-intents/{id}/confirm
POST /api/v1/payment-intents/{id}/refund
POST /api/v1/gateway/webhook
GET /api/v1/payment-intents/{id}
```

### Example contracts

```http
POST /api/v1/payment-intents
Idempotency-Key: merchant-123:cart-789:v1

{
  "merchant_id": "m_123",
  "customer_id": "c_456",
  "amount_minor": 4999,
  "currency": "USD",
  "capture_mode": "automatic"
}
```

```json
{
  "payment_intent_id": "pi_abc",
  "state": "created",
  "created_at": "2026-06-13T10:15:00Z"
}
```

Error contract:

| Error | HTTP | Meaning |
|---|---:|---|
| `duplicate_idempotency_key` | 409 | Same key used with different payload hash. |
| `invalid_state_transition` | 409 | Requested operation is not legal from current state. |
| `gateway_timeout_unknown` | 202 | Gateway outcome is unknown; reconciliation will finalize state. |

## Key design challenges

1. Financial correctness across async gateway interactions
2. Idempotency, reconciliation, and durable ledger semantics
3. Balancing correctness, latency, and cost over retention windows.

## Related links
- [HLD Design Template](../DESIGN-TEMPLATE.md)
- [Idempotency](../../03-hld-concepts/idempotency/THEORY.md)
- [Distributed Transactions](../../03-hld-concepts/distributed-transactions/THEORY.md)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/THEORY.md)
- [Write Scaling](../../03-hld-concepts/write-scaling/THEORY.md)
