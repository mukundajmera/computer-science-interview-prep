# Strong Answer: Payment System

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Payment System, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

## 2. Entity Modeling (10 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."
The architecture comprises `PaymentRequest`, `Transaction`, `IdempotencyStore`, `GatewayAdapter`, and `WebhookHandler`. The database acts as the immutable source of truth for all movements, ensuring we never double-charge.

## 3. Data Structure Rationale (10 mins)
**Say:** "Choosing the right data structures is critical for meeting our latency and throughput requirements."
Concurrent Hash Maps provide rapid idempotency key lookup. A thread-safe, strictly ordered log structure forms the basis of the transaction ledger.

## 4. Design Pattern Justifications (5 mins)
**Say:** "To keep the system modular and maintainable, I've applied specific design patterns."
The **Strategy Pattern** abstracts our interaction with multiple external gateways (like Stripe or Adyen). The **State Pattern** tracks the precise lifecycle of a `Transaction` (`INITIATED`, `GATEWAY_PENDING`, `COMPLETED`, `DECLINED`, `FAILED`).

## 5. Concurrency Defense & Thread-Safety Details (10 mins)
**Say:** "Given that this system will be accessed by multiple threads concurrently, ensuring thread safety without creating bottlenecks is a priority."
We enforce strict optimistic concurrency controls (or deterministic locking in memory) to ensure that if a webhook callback arrives concurrently with a frontend synchronous gateway response, only one thread successfully advances the state to `COMPLETED`. Repeated idempotency keys with the exact same payload return the cached intent; if the payload changes, we instantly reject the request to preserve money conservation.

## 6. Failure Handling (3 mins)
**Say:** "Systems fail, so we need to anticipate and handle failures gracefully at the lowest level."
For ambiguous gateway timeouts, we treat the state as `GATEWAY_PENDING` rather than `FAILED` and rely on a background reconciler to poll for final status, ensuring we don't accidentally retry a successful charge. Out-of-order and duplicate webhook deliveries, ambiguous gateway timeout, retry, decline and compensation preserve allowed transitions and money conservation.

## 7. Production Trade-offs (2 mins)
**Say:** "In a real production environment, this in-memory or single-node design would require certain trade-offs and adaptations."
Using synchronous database locks during gateway API calls can exhaust thread pools quickly if the gateway is slow. In large-scale production, an event-driven architecture using Kafka or an Outbox pattern is strongly preferred to decouple intent creation from final reconciliation.
