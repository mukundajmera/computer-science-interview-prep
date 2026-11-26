# Payment System — Interview Scoring Rubric

| Dimension | Points | Strong signal |
|---|---:|---|
| Requirement framing | 4 | Distinguishes auth, capture, refund, webhook, ledger, dispute, and PCI-boundary scope |
| Capacity and SLA sizing | 5 | Estimates TPS, peak multiplier, latency budget, webhook lag, and settlement windows |
| API contracts | 4 | Idempotent intent/confirm/refund APIs with clear request, response, and error semantics |
| Data model | 6 | Payment intent, transaction, idempotency, provider-event dedupe, outbox, and immutable ledger/event records |
| Architecture | 7 | Clear orchestration across gateway adapters, risk checks, local durable writes, and async webhooks |
| Correctness + risk depth | 7 | Double-charge prevention, unknown-timeout recovery, reconciliation, refund/dispute handling |
| Communication | 2 | Explicit trade-offs among latency, consistency, provider complexity, and compliance burden |

## Score bands (0-35)
- **30-35:** Strong hire; correctness and reconciliation are robust.
- **22-29:** Hire; good design, minor compliance/operability gaps.
- **15-21:** Lean no-hire; handles happy path only.
- **<15:** No-hire; state and idempotency are underspecified.

## Hard gates

Failing any hard gate caps the score at `21`, even if the architecture diagram looks polished.

1. No idempotency model for create, confirm, refund, and provider callbacks.
2. Treats a gateway timeout as a terminal failure or terminal success.
3. Uses mutable balance rows without immutable event or ledger evidence.
4. Cannot explain duplicate or out-of-order webhook handling.
5. Ignores reconciliation against provider settlement records.
6. Pulls card storage or PCI internals into scope without a containment boundary.

## Persistence-contract boosters

These are not separate bonus points beyond `35`. Use them to decide whether the API/data-model/correctness rows deserve full credit. A candidate who names these constraints precisely should score near the top of those rows; a candidate who only names logical entities should not.

Award extra credit when the candidate names unique constraints and indexes, not only logical entities:

- Unique `(merchant_id, idempotency_key)` with payload-hash comparison.
- `state=in_progress`, `lock_owner`, and `lease_expires_at` so only one retry owner can call the gateway.
- Unique `(gateway_id, provider_event_id)` for webhook dedupe.
- Unique or indexed provider reference for gateway status polling.
- Append-only `payment_event` sequence per intent.
- Outbox index on `(status, next_attempt_at)` for reliable async dispatch.
- Reconciliation indexes by provider reference and mismatch type.

## 60-90 second answer scoring

Strong candidates can say the architecture aloud in this order: scope, invariants, APIs, state machine, write path, webhook path, reconciliation path, and risk controls. Penalize answers that start with "use Stripe" or "use Kafka" before explaining idempotency, state, and auditability.

## Related content
- [Distributed Transactions](../../03-hld-concepts/distributed-transactions/THEORY.md)
- [Workflow Orchestration and Sagas](../../03-hld-concepts/workflow-orchestration/THEORY.md)
- [Chain of Responsibility Pattern](../../01-design-patterns/behavioral/chain-of-responsibility/README.md)
- [LLD Payment System](../../02-lld-projects/payment-system/)
