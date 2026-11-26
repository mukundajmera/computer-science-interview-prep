# Distributed Transactions Interview Q&A

## Basic Questions

### 1. What is a distributed transaction?
**A:** It is one logical business operation that spans multiple independent participants, such as services, databases, queues, or external providers. The challenge is preserving the business invariant even though each participant can fail or commit independently.

Example: checkout spans cart validation, inventory reservation, payment authorization, order creation, and notification.

### 2. Why not just use one database transaction?
**A:** A single database transaction works only when one database owns all affected state. Once the flow crosses service boundaries, external APIs, queues, or multiple databases, local ACID no longer covers the full operation.

Strong answer: first try to redesign ownership so the invariant fits inside one service. Use distributed patterns only when the domain genuinely crosses boundaries.

### 3. What is two-phase commit?
**A:** Two-phase commit has a coordinator ask participants to prepare, then commit only if every participant says it can commit. It can provide atomic commit across cooperative participants, but it adds latency, can block on failures, and usually does not work with external APIs.

### 4. What is a saga?
**A:** A saga is a sequence of local transactions. Each step commits independently. If a later step fails, the system runs compensating actions for earlier successful steps.

It is not a rollback. It is business-level recovery.

### 5. What is a compensating action?
**A:** A compensating action semantically reverses or repairs a previous side effect. Examples:

- release an inventory reservation;
- void a payment authorization;
- cancel a ticket hold;
- publish a cancellation event;
- mark an order failed and notify the user.

Compensation must be idempotent because it can also be retried.

### 6. What is the transactional outbox pattern?
**A:** The service writes business state and an outbox event in the same local database transaction. A separate relay publishes outbox rows to the queue. This prevents the classic failure where the database commit succeeds but event publication fails.

### 7. Why do outbox consumers still need idempotency?
**A:** The relay can crash after publishing but before marking the outbox row as sent. It may publish the same event again. Consumers need an inbox/dedupe table or idempotent state transition keyed by event id.

### 8. What is TCC?
**A:** Try-confirm-cancel is a reservation pattern:

- try: hold a resource;
- confirm: commit the held resource;
- cancel: release the hold.

It is common for seats, inventory, quotas, and appointment slots.

## Intermediate Questions

### 1. How would you design checkout without 2PC?
**A:** Use a saga:

1. Create order in `PENDING`.
2. Reserve inventory with reservation id and TTL.
3. Authorize payment with idempotency key.
4. Mark order `PAID`.
5. Publish `OrderCreated` via outbox.

If payment fails, release inventory and mark the order `PAYMENT_FAILED`. If an outcome is unknown, leave the order in `PENDING_RECONCILIATION` and query source systems by stable references.

### 2. When would you use 2PC?
**A:** Only for a narrow internal workflow where all participants are trusted, support prepare/commit, have low cardinality, and the system can accept blocking and lower availability during failures.

I would not use it for payment gateways, email providers, shipping APIs, or high-QPS checkout hot paths.

### 3. Saga orchestration vs choreography?
**A:**

| Model | Better when | Risk |
|-------|-------------|------|
| Orchestration | strict step order, audit, compensation, user-visible workflow | central coordinator complexity |
| Choreography | independent services react to domain events | hidden coupling, harder debugging |

For checkout and payments, orchestration is usually clearer because state, compensation, and audit matter.

### 4. How do you handle a payment timeout?
**A:** Do not blindly retry a charge. Persist the payment attempt with an idempotency key and gateway reference. Mark the state as pending/unknown, then reconcile by querying the gateway or consuming webhook events. Complete local state from the provider's source of truth.

### 5. How do you prevent duplicate inventory reservation?
**A:** Use a reservation table keyed by `(order_id, product_id)` or a reservation id. The reserve command is idempotent: the same command returns the same reservation. Confirm and cancel are also idempotent state transitions.

### 6. How do you publish an event safely after a DB write?
**A:** Write the business row and outbox event in the same local transaction. A relay publishes the outbox event. Consumers dedupe by event id. Monitor outbox lag and oldest unpublished event.

### 7. What states should a distributed transaction expose?
**A:** Avoid hiding uncertainty. Useful states include:

- `PENDING`;
- `RESERVED`;
- `PAYMENT_PENDING`;
- `CONFIRMED`;
- `COMPENSATING`;
- `COMPENSATED`;
- `FAILED_FINAL`;
- `NEEDS_RECONCILIATION`;
- `NEEDS_MANUAL_REVIEW`.

### 8. What is the difference between idempotency and distributed transactions?
**A:** Idempotency makes retries safe for a command, event, or step. Distributed transaction design decides how a multi-part business operation reaches a correct final outcome. A good distributed transaction strategy uses idempotency at every boundary.

## Advanced Questions

### 1. How do you recover if the orchestrator crashes after a step succeeds?
**A:** Persist workflow state before starting a step and after receiving the result. Each step command carries an idempotency key. On recovery, the orchestrator reads the last durable state and either verifies the prior step outcome or safely retries the idempotent command.

### 2. What if compensation fails?
**A:** Treat compensation as a first-class workflow. Retry with backoff, persist failure reason, expose stuck compensation metrics, and escalate to manual review if the domain is financial, legal, or irreversible. Do not silently mark the saga failed if an earlier side effect remains live.

### 3. How do you handle out-of-order events?
**A:** Use aggregate version, sequence number, or state-machine transition checks. Consumers reject invalid backwards transitions, buffer if appropriate, or trigger reconciliation. Idempotency alone does not solve ordering.

### 4. How do you size outbox and dedupe storage?
**A:** Estimate:

```text
records = events_per_second * retention_seconds
storage = records * bytes_per_record * replication_factor
```

Then separate hot retry/dedupe retention from long-term ledger/audit retention. A 7-day dedupe table at hundreds of thousands of events/sec can become tens or hundreds of TB.

### 5. How would you design multi-region booking?
**A:** Assign each protected resource a home region or shard owner. Strict booking writes route to that owner. Other regions can serve reads and queue/write-forward requests. If the home region is unavailable, either fail closed for that resource or use pre-allocated regional inventory/escrow with reconciliation.

### 6. Why is "exactly-once" usually a misleading claim?
**A:** Infrastructure often provides at-least-once delivery or replay. The practical guarantee is usually exactly-once effect: durable idempotency keys, dedupe tables, state-machine checks, and reconciliation make repeated execution converge to one business outcome.

### 7. How do you test distributed transaction correctness?
**A:** Test by injecting failures at every boundary:

- crash after DB commit before outbox publish;
- duplicate event delivery;
- payment timeout after provider charge;
- compensation failure;
- orchestrator restart mid-step;
- reservation expiry during payment delay;
- concurrent confirm/cancel attempts.

Assertions should target invariants: no double charge, no oversell, no invalid state transition, no lost outbox event.

### 8. What should be synchronous vs asynchronous?
**A:** Keep the user-facing command synchronous only until the system has accepted a durable state. Heavy or uncertain work moves async with visible status. For example, checkout can return `ORDER_PENDING` after reservation and payment initiation while settlement/reconciliation completes asynchronously.

## Domain Drills

### Payment System
**Prompt:** A card is charged, but your service times out before recording success. What do you do?

**Strong answer:** Store a stable payment attempt id before calling the gateway. On timeout, mark the attempt unknown, do not issue a second charge, and reconcile by gateway reference/webhook. The local ledger updates only after confirmed provider state.

### E-commerce Checkout
**Prompt:** Payment fails after inventory reservation.

**Strong answer:** Run compensation: release the reservation, mark order payment failed, preserve an audit event, and make release idempotent. If release fails, retry and alert on stuck reservation age.

### Ticket Booking
**Prompt:** Two users try to book the same seat.

**Strong answer:** Use a per-seat hold state machine with one active owner, TTL expiry, and idempotent confirm/cancel. Route strict seat writes to one owner/partition; do not rely on eventual consistency for final seat commit.

### Notification Fanout
**Prompt:** Order row commits but notification event publish fails.

**Strong answer:** Use transactional outbox. The notification worker consumes outbox-published events and dedupes by event id. User confirmation is not coupled to email provider availability.

### Marketplace Ledger
**Prompt:** You need buyer debit and seller credit.

**Strong answer:** Keep ledger entries append-only and balanced within the ledger service if possible. If external settlement is involved, use local immutable ledger state plus outbox/reconciliation. Avoid cross-service 2PC unless all ledger participants are controlled and strict atomicity is worth the availability cost.

## Rapid Follow-Up Drill

| Question | Strong response |
|----------|-----------------|
| What is the invariant? | Name the protected business rule first. |
| Can one service own it? | Prefer single-owner local ACID if possible. |
| Why not 2PC? | Blocking, latency, availability, and external participant limits. |
| What is the retry key? | Command/event/step idempotency key, scoped by owner. |
| What if event publish fails? | Transactional outbox and relay. |
| What if event publishes twice? | Inbox/dedupe and idempotent state transition. |
| What if compensation fails? | Retry, persist, alert, manual review. |
| What is user-visible? | Pending/failed/reconciled states, not hidden uncertainty. |
| What do you monitor? | Stuck saga, outbox lag, duplicate rate, reconciliation age, invariant violations. |

## Common Wrong Answers

- "Use 2PC for everything."
- "Kafka gives exactly-once, so no duplicates."
- "Rollback the payment after it charged."
- "Just retry the payment request."
- "Eventual consistency means we do not need state machines."
- "Compensation can be a cleanup cron later."
- "The order is confirmed before inventory/payment outcomes are durable."
- "We do not need reconciliation because webhooks will arrive."

## Related Concepts

- [Distributed Transactions Theory](./THEORY.md)
- [Idempotency](../idempotency/THEORY.md)
- [Workflow Orchestration](../workflow-orchestration/THEORY.md)
- [Message Queues](../message-queues/THEORY.md)
- [Contention Control](../contention-control/THEORY.md)
- [Payment System HLD](../../04-hld-projects/payment-system/)
- [E-commerce Backend HLD](../../04-hld-projects/ecommerce-backend/)
