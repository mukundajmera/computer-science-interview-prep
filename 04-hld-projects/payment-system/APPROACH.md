# Design Approach for Payment System

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify requirements | 6 min | Intent/auth/capture/refund scope, compliance boundaries |
| Capacity estimation | 6 min | TPS, callback load, reconciliation window |
| API + state model | 10 min | Idempotent APIs and payment state machine |
| Architecture | 13 min | Orchestrator, gateway adapters, webhook + reconciliation |
| Deep dives | 7 min | Unknown outcomes, duplicate callbacks, ledger integrity |
| Wrap-up | 3 min | Multi-gateway rollout and risk controls |

## Suggested execution order
1. Declare payment invariants and terminal states.
2. Define API contracts with idempotency keys.
3. Separate sync client path from async settlement path.
4. Add reconciliation and operational controls.
5. Close with compliance and regional extension path.

## Candidate decision checklist

| Decision | Strong default | Why it matters |
|---|---|---|
| Source of truth | Immutable `payment_event` plus rebuildable projections | Audits and dispute investigation need replayable history. |
| Idempotency scope | API key + payload hash + provider reference dedupe | Prevents duplicate charges across client retries and webhook repeats. |
| Gateway timeout | transaction `unknown` status + `processing_unknown` read projection + reconciliation | Timeout is not success or failure until provider evidence arrives. |
| Webhook handling | Signature verify, event-id dedupe, ordered state validator | Providers retry and can deliver out of order. |
| Ledger update | Local transaction before external side effect dispatch | Keeps internal evidence durable before unreliable network calls. |

## Deep-dive flow to rehearse

Say: "The hard part is not the happy-path charge. It is preserving financial correctness when the client retries, the gateway times out, and webhooks arrive later. I will acquire an idempotency lock with a payload hash and lease, write the intent, transaction, event, and outbox atomically, let only the lock owner call the idempotent gateway adapter, and treat final settlement as asynchronous evidence from webhooks and reconciliation. That lets me return quickly while still proving zero double-charge semantics."
