# Brokerage Platform — Common Interview Pitfalls

## 1. Designing an Exchange Instead of a Brokerage
A brokerage routes orders and tracks state; it does not own market matching logic.

## 2. Eventual Consistency for Final Order State
Order completion/cancellation must be strongly correct for user trust and compliance.

## 3. No Idempotency for Order Commands
Retries without idempotency create duplicate submissions and inconsistent balances.

## 4. Coupling Quote Fanout With Order Mutation
High-frequency market data can starve command processing if paths are not isolated.

## 5. Missing Reconciliation Loop
External acks can be delayed or dropped; periodic reconciliation is mandatory.

## 6. Ignoring Backpressure on Stream Subscribers
Without bounded queues and drop/degrade rules, websocket hubs fail under bursts.

## 7. No Explicit Order State Machine
Ad-hoc string updates create illegal transitions and debugging dead ends.

---

## Quick Self-Check

- Did I separate fanout read path and command write path?
- Did I include idempotency and replay behavior?
- Did I define order transitions and reconciliation ownership?
