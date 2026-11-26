# Distributed Transactions

Distributed transactions are the design choices used when one business action spans multiple services, databases, queues, or external providers and the system still needs a defensible correctness story.

In interviews, this topic is less about saying "use 2PC" and more about proving you know where atomicity is truly required, where eventual consistency is acceptable, and how failures are repaired without double-charging, overselling, or losing auditability.

## What is it?

A distributed transaction coordinates one logical business operation across more than one independent participant.

Examples:

- checkout: reserve inventory, authorize payment, create order, emit confirmation;
- payment refund: update ledger, call gateway, notify merchant, expose status;
- ticket booking: hold seat, accept payment, issue ticket, expire abandoned hold;
- marketplace order: debit buyer, credit seller, reserve shipment, update fraud/risk state.

The hard part is that each participant can commit, fail, timeout, retry, or recover independently. A single ACID transaction inside one database cannot automatically protect the whole workflow.

## Core mental model

Use this ladder before choosing a pattern:

1. Can the operation fit inside one database transaction?
2. Can the business invariant be redesigned around one owning service?
3. Can we reserve first, then confirm later?
4. Can partial completion be repaired by compensation or reconciliation?
5. Is strict all-or-nothing commit across participants truly mandatory?

Most scalable systems avoid global atomic commit. They use local transactions, idempotent commands, durable events, and repair loops to create correct business outcomes over unreliable infrastructure.

## Why do we need it?

Distributed transactions appear whenever correctness crosses service boundaries:

- payment succeeds but the order write times out;
- inventory is reserved but payment fails;
- a queue publish fails after the database row commits;
- a worker retries and performs the same side effect twice;
- one region accepts a booking while another region still has stale state;
- a saga compensates one step but that compensation also times out.

Without an explicit strategy, candidates usually produce one of two weak designs: an unavailable strongly consistent design that cannot scale, or an eventually consistent design with no repair path.

## Pattern selection matrix

| Pattern | Best fit | Strength | Cost / risk |
|---------|----------|----------|-------------|
| Single-owner local transaction | one service can own the invariant | simplest correctness | requires domain boundary discipline |
| Two-phase commit (2PC/XA) | rare strict atomic commit across trusted participants | all-or-nothing outcome when everyone cooperates | blocking, latency, coordinator failure, poor fit for external APIs |
| Saga orchestration | ordered business workflow with compensations | explicit state, retries, auditability | compensation complexity; not true rollback |
| Saga choreography | event-driven steps with local reactions | loose coupling, scalable fanout | harder global visibility and debugging |
| Transactional outbox | database update and event publication must not diverge | durable event handoff | relay lag, duplicate events, cleanup |
| Inbox / idempotent consumer | queue redelivery or replay is expected | safe at-least-once processing | dedupe state and retention cost |
| Try-confirm-cancel (TCC) | scarce resources need temporary holds | clear reservation lifecycle | hold expiry, orphan cleanup, user-facing pending states |
| Escrow / quota reservation | bounded counters like inventory or credits | avoids global locking for every write | requires partitioned budgets and reconciliation |
| Reconciliation job | external or ambiguous outcomes exist | repairs reality from source-of-truth records | delayed correctness; needs strong observability |

## 2PC in interviews

Two-phase commit has two phases:

1. **Prepare:** coordinator asks every participant if it can commit.
2. **Commit / abort:** if every participant prepared successfully, coordinator tells all to commit; otherwise it tells all to abort.

Use it only when all of these are true:

- participants are under your control;
- participants support prepare/commit semantics;
- latency budget accepts multiple round trips;
- availability loss during coordinator/participant failure is acceptable;
- the invariant truly requires atomic commit.

Why interviewers expect caution:

- prepared participants may hold locks while waiting for the coordinator;
- coordinator failure can block participants;
- external systems such as card networks, email providers, and shipping APIs usually do not support 2PC;
- multi-region 2PC makes latency and partition behavior worse.

Strong answer: "I would avoid 2PC for the checkout hot path. I may use it inside a narrow internal back-office workflow if participants are few, trusted, and availability trade-offs are acceptable."

## Saga pattern

A saga breaks one distributed transaction into a sequence of local transactions. Each local transaction commits independently. If a later step fails, earlier steps are undone semantically through compensating actions.

Checkout example:

```text
create order PENDING
-> reserve inventory
-> authorize payment
-> mark order PAID
-> publish OrderCreated

failure after payment:
-> void authorization
-> release inventory
-> mark order FAILED
```

Saga design rules:

- Persist saga state before and after each step.
- Make every command idempotent.
- Define compensation for every step with an external side effect.
- Treat compensation as a normal workflow, not a best-effort cleanup.
- Expose user-facing pending/failed states instead of hiding uncertainty.
- Add manual intervention states for money, legal, or irreversible side effects.

Sagas do not provide database rollback. They provide business recovery.

## Transactional outbox and inbox

The outbox solves this failure:

```text
write order row succeeds
publish OrderCreated event fails
```

Instead of publishing directly, write both business state and an outbox row in the same local transaction:

```sql
BEGIN;
  INSERT INTO orders (...);
  INSERT INTO outbox_events (event_id, aggregate_id, event_type, payload, status);
COMMIT;
```

A relay reads unsent outbox rows and publishes them to Kafka/SQS/PubSub. Consumers dedupe by `event_id` or business command id.

Consumer-side inbox/dedupe table:

```text
consumer_name + event_id -> processed_at + result
```

This turns "exactly once" into a practical contract: at-least-once delivery plus idempotent handlers plus durable dedupe.

## TCC and reservations

Try-confirm-cancel is useful for scarce resources:

| Phase | Seat booking example | Inventory example |
|-------|----------------------|-------------------|
| Try | hold seat for user | reserve stock |
| Confirm | issue ticket after payment | commit stock after order paid |
| Cancel | release hold on timeout/failure | release reservation |

Key controls:

- hold owner and expiry time;
- unique reservation id;
- confirm only by the same owner;
- idempotent confirm/cancel;
- cleanup job for expired holds;
- metrics for stuck holds and abandoned reservations.

This is not the same as 2PC. TCC models business states explicitly and accepts that users may see pending states.

## Choosing consistency boundaries

| Domain | Correctness boundary | Common strategy |
|--------|----------------------|-----------------|
| Payment charge | never double-charge; ledger audit is durable | idempotency key, gateway reference, outbox, reconciliation |
| Inventory | do not oversell committed stock | reservation state machine, optimistic concurrency, TTL release |
| Ticket seat | one owner per seat | per-seat hold, serialized booking, expiry |
| Notification | no silent loss; duplicates acceptable | outbox + idempotent consumer |
| Analytics | approximate correctness acceptable | at-least-once stream + dedupe window or bounded error |
| Search index | eventual consistency acceptable | async event projection + replay |

State the invariant first. Then choose the weakest mechanism that protects it.

## Data model building blocks

Typical tables or records:

| Record | Purpose |
|--------|---------|
| `business_entity` | order/payment/booking current state |
| `state_transition_log` | audit of valid transitions |
| `idempotency_record` | request key, payload hash, result replay |
| `reservation` | resource, owner, expiry, status |
| `saga_instance` | workflow id, current step, status, retry count |
| `saga_step` | step id, command id, compensation id, terminal result |
| `outbox_event` | event id, aggregate id, payload, publish status |
| `inbox_event` | consumer dedupe record |
| `reconciliation_record` | local state vs external source-of-truth comparison |

## Failure semantics

| Failure | Correct response |
|---------|------------------|
| Client retries create order | return existing order using idempotency key |
| Order row commits but event publish fails | outbox relay publishes later |
| Event publishes twice | consumer dedupes with inbox/event id |
| Inventory reserved, payment fails | release reservation through compensation |
| Payment gateway times out | mark payment pending; reconcile by gateway reference |
| Compensation fails | retry with backoff, then park for manual intervention |
| Saga orchestrator crashes | resume from persisted step state |
| Outbox relay crashes after publish before marking sent | publish may repeat; consumers must be idempotent |
| Region partition occurs | route strict writes to home region or fail closed for protected resource |

## Capacity and retention

Distributed transaction support creates extra writes. Estimate them.

Example checkout flow:

```text
50K peak orders/sec
5 saga steps per order
1 outbox event per step
2 dedupe/inbox records per event
retention = 7 days
```

Outbox events per second:

```text
50K * 5 = 250K events/sec
```

Inbox records per second:

```text
250K * 2 = 500K records/sec
```

Retention sizing:

```text
records = writes_per_second * retention_seconds
storage = records * bytes_per_record * replication_factor
```

If each dedupe record is 200 bytes and retained for 7 days with 3x replication:

```text
500,000 * 604,800 * 200 * 3 ~= 181 TB
```

That estimate changes design: use shorter hot dedupe windows where business-safe, compact old audit records, partition by tenant/resource, and keep ledger/audit retention separate from retry dedupe retention.

## When to use each approach

| Situation | Recommended answer |
|-----------|--------------------|
| One database owns the invariant | local ACID transaction |
| Multi-step user workflow | saga orchestration |
| DB write must emit event | transactional outbox |
| Queue consumers mutate state | inbox/dedupe + idempotent handler |
| Scarce resource with timeout | TCC/reservation |
| Money moved through external gateway | idempotency + ledger + reconciliation |
| Strict atomic commit across few internal DBs | consider 2PC, explain availability cost |
| Analytics/search projections | eventual consistency + replay |

## When NOT to use distributed transactions

- Pure reads.
- Single-row or single-database mutations.
- Low-value metrics where bounded duplicate/error is acceptable.
- Search, recommendations, and caches that can rebuild from source data.
- High-latency user paths where pending state is acceptable.
- External APIs that cannot participate in a prepare/commit protocol.

Do not force global atomicity when a clear state machine plus repair loop gives a better product and operational outcome.

## Observability

Track:

- saga success/failure/compensation rate;
- stuck workflow count by step;
- retry depth and age;
- outbox lag and oldest unpublished event age;
- inbox duplicate-hit rate;
- reservation expiry and orphan count;
- reconciliation mismatch count and age;
- manual intervention queue size;
- double-charge, oversell, and invalid-transition counters;
- p95/p99 latency for protected commands.

Alerts should focus on business invariants, not just infrastructure health.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Boundary choice | identifies exact invariant and owner | says "use distributed transaction" generically |
| Pattern selection | compares local transaction, saga, outbox, TCC, 2PC | names one pattern only |
| Failure handling | timeout, duplicate, crash, compensation, reconciliation covered | happy path only |
| Consistency trade-off | states what is strong vs eventual | claims everything is strongly consistent |
| Idempotency | keys per command/event/step | retries side effects blindly |
| Operations | outbox lag, stuck saga, replay, manual repair metrics | no repair visibility |
| Scale | sizes outbox/dedupe/retention writes | ignores metadata amplification |

## Common pitfalls

- Treating 2PC as the default answer for checkout.
- Calling a saga a rollback. It is compensation, not undo.
- Publishing an event after commit without an outbox.
- Forgetting that outbox relays can publish duplicates.
- Retrying non-idempotent payment or inventory commands.
- Hiding pending states from users/operators.
- No reconciliation for ambiguous external outcomes.
- No TTL cleanup for reservations.
- One global idempotency key reused across steps.
- No manual intervention path for money or legal states.

## Interview answer frame

Use this 60-second structure:

1. "The invariant is X."
2. "I will keep X inside one owner if possible."
3. "For cross-service flow, I use saga/TCC/outbox, not 2PC, because..."
4. "Every command/event has an idempotency key."
5. "Failures become explicit states: pending, compensated, failed, needs manual review."
6. "I validate with reconciliation and invariant metrics."

## Related concepts

- [Idempotency](../idempotency/THEORY.md)
- [Workflow Orchestration](../workflow-orchestration/THEORY.md)
- [Message Queues](../message-queues/THEORY.md)
- [Contention Control](../contention-control/THEORY.md)
- [CAP Theorem](../cap-theorem/THEORY.md)
- [Database Replication](../database-replication/THEORY.md)
- [Microservices Communication](../microservices-communication/THEORY.md)
- [Payment System HLD](../../04-hld-projects/payment-system/)
- [E-commerce Backend HLD](../../04-hld-projects/ecommerce-backend/)
- [Ticketing Platform HLD](../../04-hld-projects/ticketing-platform/)
- [Amazon Orders Case Study](../../case-studies/amazon-orders/)
