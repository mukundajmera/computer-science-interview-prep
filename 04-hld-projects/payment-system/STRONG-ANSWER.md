# Payment System — Strong Answer Outline (Time-Boxed)

## 0-5 min: Requirements
- Say: "I will design a payment intent platform that creates intents, confirms authorization/capture, handles refunds, accepts gateway webhooks, and reconciles unknown outcomes. I will keep card vaulting and PCI internals behind gateway/token services and focus on correctness, idempotency, state, and auditability."
- Scope auth, capture, refund, webhook ingestion, status reads, reconciliation, and operator visibility.
- Out of scope: card storage, provider-specific compliance certification, ML fraud scoring, and accounting general ledger internals.

## 5-10 min: Estimation
- Assume 15K payment intents/sec peak and 1.5x callback volume, so webhook ingestion peaks near 22.5K/sec.
- Daily volume is roughly 1.3B intents at sustained peak; event/audit storage must be append-only, partitioned by time/merchant, and retained separately from hot read projections.
- Design impact: split the synchronous authorization path from asynchronous webhook/reconciliation paths.

## 10-20 min: API + data model
- Core APIs: `POST /payment-intents`, `POST /payment-intents/{id}/confirm`, `POST /payment-intents/{id}/refund`, `POST /gateway/webhook`, `GET /payment-intents/{id}`.
- Every mutating request carries an `Idempotency-Key`; the server stores key, payload hash, state, lock owner, lease expiry, response, and expiry. Same key plus same payload replays the original response when complete; same key plus different payload returns `409`; while the first request is `in_progress`, only the lease owner can call the gateway.
- State lifecycle: `created -> processing -> authorized -> captured -> refund_pending -> refunded/partially_refunded`, with terminal `failed` states and reconciliation-driven correction for unknown gateway outcomes.
- Data model: `payment_intent`, `payment_transaction`, immutable `payment_event`, idempotency record, outbox record, and `reconciliation_record`.

## 20-35 min: Architecture
- Write path: API validates request and idempotency, writes local intent/transaction/event/outbox atomically, dispatches gateway work through an adapter, and updates projections from durable events.
- Webhook path: verify gateway signature, deduplicate by provider event ID, store raw payload hash and normalized event, then apply state transition rules.
- Read path: serve status from a projection keyed by `payment_intent_id`; fall back to event replay for audit/debug.
- Failure path: if gateway timeout leaves outcome unknown, mark transaction `processing/unknown`, enqueue poll/reconciliation, return `202`, and alert if provider settlement does not match internal state within SLA.
- Observability: double-charge rejection count, idempotency conflicts, gateway timeout rate, webhook lag, reconciliation mismatches, event replay errors, and p95 status latency.

## 35-42 min: Deep dives
- Idempotency boundary: protect at API request level and provider reference level; never retry a charge without the same idempotency semantics.
- Ledger correctness: immutable events are source of truth; projections are rebuildable.
- Partitioning: shard by merchant/time for hot writes, and keep provider reference indexes for reconciliation.
- Recovery: outbox workers are at-least-once, adapters are idempotent, and replay validates legal state transitions before updating projections.

## 42-45 min: Wrap-up
- Say: "The key decision is to make local state and audit events durable before unreliable gateway calls, then treat gateways as asynchronous systems. That gives us low-latency intent creation, zero double-charge semantics through idempotency, and eventual settlement correctness through webhooks plus reconciliation."
- Trade-off: this is more operationally complex than a synchronous wrapper, but it is the right choice for financial correctness, retries, and auditability.
