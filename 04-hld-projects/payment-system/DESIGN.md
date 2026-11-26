# Payment System — Design

## 1. Requirements and Constraints

### Functional
- Create payment intents and confirm authorization/capture flows.
- Process refunds and expose transaction lifecycle.
- Handle async gateway callbacks safely.
- Run reconciliation against provider settlement data.

### Non-functional
| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Authorization latency | p95 < 800ms |
| Double-charge rate | 0 (idempotency invariant) |
| Reconciliation lag | < 24h |

## 2. Back-of-envelope estimation

Assume 15K TPS peak payment intents, 1.5x callback volume.

| Metric | Value |
|---|---|
| Peak intents | 15K/s |
| Peak callbacks/webhooks | 22.5K/s |
| Daily transactions | ~1.3B |
| Dispute retention | 18 months metadata |

Decision impact: split synchronous user path from asynchronous settlement and reconciliation path.

## 3. APIs

```http
POST /api/v1/payment-intents
POST /api/v1/payment-intents/{id}/confirm
POST /api/v1/payment-intents/{id}/refund
POST /api/v1/gateway/webhook
GET  /api/v1/payment-intents/{id}
```

### Request/response/error contract

```http
POST /api/v1/payment-intents/{id}/confirm
Idempotency-Key: merchant-123:pi-abc:confirm:v1

{
  "payment_method_token": "tok_card_123",
  "capture_mode": "automatic"
}
```

```json
{
  "payment_intent_id": "pi_abc",
  "state": "processing",
  "transaction_id": "txn_789",
  "next_action": null
}
```

| Error | Retry? | Handling |
|---|---|---|
| `duplicate_idempotency_key` | no | Return original response when payload hash matches; reject if payload differs. |
| `invalid_state_transition` | no | Surface current state and allowed next operations. |
| `gateway_timeout_unknown` | yes, via job | Mark transaction `unknown`, enqueue status poll, and reconcile from provider records. |
| `gateway_hard_decline` | no | Terminal decline; no capture or refund is allowed. |

## 4. Data model

| Table | Key fields | Constraints and indexes | Retention |
|---|---|---|---|
| `payment_intent` | `id`, `merchant_id`, `customer_id`, `amount`, `currency`, `state`, `created_at` | PK `id`; index `(merchant_id, created_at)`; state transitions validated by service | Hot projection for status reads; archived event history by policy |
| `idempotency_record` | `merchant_id`, `idem_key`, `payload_hash`, `state`, `lock_owner`, `lease_expires_at`, `response_body`, `status_code`, `expires_at` | Unique `(merchant_id, idem_key)`; reject same key with different payload hash; only lock owner may dispatch external side effect | Retry window plus dispute/debug window for mutating APIs |
| `payment_transaction` | `txn_id`, `intent_id`, `gateway_id`, `gateway_ref`, `type`, `amount`, `status`, `created_at` | PK `txn_id`; unique `(gateway_id, gateway_ref)` when provider ref exists; index `(intent_id, created_at)` | Audit and reconciliation window |
| `payment_event` | `intent_id`, `seq`, `event_type`, `payload_hash`, `occurred_at` | Unique `(intent_id, seq)`; append-only; projection rebuild source | Long-lived audit record |
| `provider_event_dedupe` | `gateway_id`, `provider_event_id`, `payload_hash`, `received_at` | Unique `(gateway_id, provider_event_id)`; stores normalized processing result | Provider retry plus dispute window |
| `outbox_message` | `id`, `aggregate_id`, `event_type`, `payload_hash`, `next_attempt_at`, `status` | PK `id`; index `(status, next_attempt_at)`; at-least-once worker delivery | Until delivered plus replay/debug window |
| `reconciliation_record` | `gateway_ref`, `internal_status`, `provider_status`, `difference_type`, `reconciled_at` | Index `(gateway_ref)` and `(reconciled_at, difference_type)` | Settlement and audit window |

Persistence invariant: no external gateway call is dispatched unless the local intent, transaction, event, idempotency, and outbox records needed to explain the attempt are already durable.

### Idempotency acquisition contract

1. Insert or fetch `(merchant_id, idem_key)` under a unique constraint.
2. If the key exists with a different `payload_hash`, return `409 duplicate_idempotency_key`.
3. If the key exists with `state=succeeded`, replay the stored response.
4. If the key exists with `state=in_progress` and the lease is live, return `202` or block briefly on the owner result.
5. If the lease expired, one worker may acquire a new `lock_owner` and continue recovery.
6. Only the current `lock_owner` may enqueue or perform the provider side effect, which preserves zero double-charge semantics under concurrent retries.

### Persisted state machine and read projection

The authoritative `payment_intent.state` never transitions to `processing_unknown`. It remains `processing` while a gateway outcome is unresolved. The latest `payment_transaction.status` may be `unknown`; the read model may expose `processing_unknown` as a projection label so clients and operators can distinguish "still working" from "provider outcome unknown" without validating transitions from that label.

| From | Event | To | Notes |
|---|---|---|---|
| `created` | confirm requested | `processing` | Local event is committed before gateway call is dispatched. |
| `processing` | gateway authorized | `authorized` | Capture may follow automatically or manually. |
| `authorized` | capture succeeded | `captured` | Ledger projection updates merchant receivable. |
| `captured` | refund requested | `refund_pending` | Partial refunds keep captured state plus refund records. |
| `refund_pending` | refund succeeded | `refunded` / `partially_refunded` | Depends on refunded amount. |
| any non-terminal | gateway hard decline | `failed` | Terminal failure with provider reason. |
| `processing` | gateway timeout before definitive response | `processing` | Intent remains `processing`; transaction status becomes `unknown`; status polling and reconciliation own recovery. |
| `processing` | provider confirms authorization after unknown timeout | `authorized` | Provider evidence is deduped and validated before transition. |
| `processing` | provider confirms capture after unknown timeout | `captured` | Used when capture completed before local timeout was resolved. |
| `processing` | provider confirms hard decline/no charge after unknown timeout | `failed` | Terminal only after provider evidence or reconciliation record. |
| `refund_pending` | provider refund timeout | `refund_pending` | Refund transaction status becomes `unknown`; refund outcome is unresolved until provider evidence arrives. |
| `refund_pending` | provider confirms refund | `refunded` / `partially_refunded` | Depends on cumulative refunded amount. |
| `refund_pending` | provider rejects refund | `captured` | Capture remains valid; refund transaction records failure reason. |

| Projection label | Source-of-truth condition | Client meaning |
|---|---|---|
| `processing` | `payment_intent.state=processing` and latest transaction is pending/in flight | Provider call is still actively being attempted or awaited. |
| `processing_unknown` | `payment_intent.state=processing` and latest transaction status is `unknown` | Outcome is unresolved; client should poll or wait for webhook/reconciliation. |
| `refund_unknown` | `payment_intent.state=refund_pending` and latest refund transaction status is `unknown` | Refund outcome is unresolved; original capture still stands until provider evidence changes it. |

## 5. High-level architecture

Mermaid source: [architecture.mmd](./diagrams/architecture.mmd).

Client -> Payments API -> Orchestrator -> Gateway Adapter(s)
                       |                  |
                       |                  +-> Webhook Handler
                       +-> Ledger/Event Store -> Reconciliation Jobs -> Ops Dashboard

## 6. Deep dives
1. **State-machine integrity:** valid transition enforcement and terminal-state rules.
2. **Idempotency boundaries:** request idempotency key and gateway reference dedup; see the [Idempotency concept](../../03-hld-concepts/idempotency/THEORY.md) for retry, payload-hash, and TTL semantics.
3. **Distributed transaction boundaries:** keep local ledger writes atomic, use outbox/event handoff for async effects, and avoid 2PC with gateways; see [Distributed Transactions](../../03-hld-concepts/distributed-transactions/THEORY.md).
4. **Unknown outcomes:** timeout handling with async status polling + reconciliation.

### Failure path: gateway timeout after local commit

1. API validates idempotency key, acquires `idempotency_record(state=in_progress, lock_owner, lease_expires_at)`, and writes intent, transaction, event, and outbox rows in one local transaction.
2. Only the lock owner dispatches the provider-idempotent gateway call.
3. Gateway adapter call times out before a definitive provider response.
4. Orchestrator records `gateway_timeout_unknown`, sets transaction status to `unknown`, keeps the intent in `processing`, stores the replayable `202 Accepted` response, and enqueues a status-poll job keyed by provider reference or merchant/idempotency metadata.
5. Webhook handler or reconciliation job later maps the provider outcome back to the internal transaction.
6. State transition validator applies only legal transitions, and operator alerts fire if internal/provider records disagree after the reconciliation SLA.

## 7. Rollout, observability, and rollback

### Rollout
- Start with one gateway adapter and one merchant cohort behind a feature flag.
- Run shadow reconciliation for new providers before routing live authorizations.
- Ramp by merchant, currency, and payment method while watching timeout, decline, and duplicate-idempotency rates.
- Keep the old gateway path active until settlement and refund reconciliation pass for a full billing cycle.

### Observability
- Emit structured events for every state transition, gateway call, webhook, idempotency hit, and reconciliation difference.
- Dashboard p95 authorization latency, webhook lag, unknown-outcome backlog, refund age, duplicate-idempotency rejection rate, and provider/internal mismatch rate.
- Alert on any double-charge invariant breach, unexplained provider settlement, stuck `processing` transaction, or reconciliation SLA miss.
- Preserve correlation IDs across API request, outbox message, gateway reference, webhook, and ledger event.

### Rollback
- Disable the new gateway route flag and send new traffic back to the previous adapter.
- Keep status-poll and webhook consumers running until all in-flight unknown outcomes settle.
- Do not rewrite ledger history during rollback; append compensating events for refunds, reversals, and operator-reviewed corrections.
- Rebuild read projections from `payment_event` if rollback exposes projection drift.

## 8. Trade-offs

| Decision | Chosen | Alternative | Why |
|---|---|---|---|
| Consistency | immediate intent state + async finalization | fully synchronous finalization | lower user latency and better resilience |
| Ledger strategy | immutable events + projections | mutable balance rows only | auditability and replay |
| Gateway abstraction | adapter per provider | provider logic in core service | easier rollout and failover |

## 9. Variants and extensions
- Multi-currency pricing and FX service.
- Risk scoring pre-authorization hooks.
- Chargeback/dispute subsystem.

---
**Real-world reference**: See how Stripe solved this in the [Stripe case study](../../case-studies/stripe-ledger-engine/)
