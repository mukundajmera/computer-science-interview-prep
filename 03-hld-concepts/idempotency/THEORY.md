# Idempotency

Idempotency makes retries safe. In system design interviews, it is the difference between "the client can retry" and "the system can retry without duplicate charges, duplicate jobs, inflated counters, or repeated external side effects."

## What is it?

An operation is idempotent when repeating the same logical request produces the same externally visible result as executing it once.

There are three common forms:

| Form | Meaning | Example |
|------|---------|---------|
| Natural idempotence | The operation is inherently repeat-safe | `DELETE /files/{id}`, `PUT /profile/{id}` with a full replacement |
| Key-based idempotency | A caller supplies a stable key so the service can recognize retries | `POST /payment-intents` with `Idempotency-Key` |
| Deduplication | A consumer suppresses repeated events using event identity | click event `event_id`, webhook provider event id |

Idempotency is not the same as exactly-once execution. Most distributed systems execute with at-least-once delivery and make side effects idempotent at the boundary that matters.

## Why do we need it?

Retries happen even when clients and services are correct:

- clients time out after the server commits;
- load balancers retry on connection resets;
- queues redeliver after missing acknowledgments;
- workers crash after calling an external system;
- webhooks arrive twice or out of order;
- workflow engines replay steps after failover.

Without idempotency, retries can create financial loss, duplicated emails, duplicate inventory reservations, duplicate job execution, or inflated analytics.

## Core contract

For a mutation API, the contract should answer four questions:

1. What is the idempotency key?
2. What payload is bound to that key?
3. What response is replayed for duplicate calls?
4. When does the guarantee expire?

Example API shape:

```http
POST /api/v1/payment-intents
Idempotency-Key: tenant_42:checkout_abc123
Content-Type: application/json

{
  "customer_id": "cust_91",
  "amount_cents": 4999,
  "currency": "USD"
}
```

Recommended behavior:

| Case | Response |
|------|----------|
| New key + valid payload | Reserve key, execute operation, store final response |
| Same key + same payload while in progress | Return `202 Accepted`, wait/poll, or replay the pending resource state |
| Same key + same payload after success | Return the original success response |
| Same key + different payload | Return `409 Conflict` with a payload mismatch error |
| Key expired | Return a clear expiry error or treat as a new command only if the business domain allows it |

Store a payload hash with the key. Do not compare only the key; accidental key reuse with a different body is a correctness bug.

## Where to place the boundary

| Boundary | Key | Use when | Common storage |
|----------|-----|----------|----------------|
| Client API command | tenant + client request id | clients retry create/update operations | SQL unique constraint, Redis, DynamoDB |
| Service command | operation id | internal services retry commands | command table, outbox table |
| Queue consumer | message/event id | queues redeliver messages | consumer offset + dedupe table |
| Workflow step | workflow id + step id | orchestrators replay after crash | workflow state store |
| Provider callback | provider event id | payment/webhook providers retry callbacks | webhook event table |
| Reconciliation job | external reference + period | backfills and repairs rerun safely | ledger/event table |

Pick the boundary that owns the side effect. A payment gateway call, a database mutation, and a notification send may each need separate idempotency keys.

## How it works

1. Validate tenant, caller, and payload.
2. Derive or read the idempotency key.
3. Insert a record with a unique constraint on `(tenant_id, idempotency_key)`.
4. Store request hash, status, creation time, and expiry time.
5. Execute the side effect only if this caller won the reservation.
6. Store the result or final resource id.
7. Replay the stored result for duplicate attempts.

Minimal state model:

| State | Meaning | Retry behavior |
|-------|---------|----------------|
| `PENDING` | key reserved, operation not final | return in-progress state or wait with timeout |
| `SUCCEEDED` | operation committed | replay success response |
| `FAILED_RETRYABLE` | transient failure before final side effect | allow bounded retry by owner |
| `FAILED_FINAL` | business failure is final | replay final error |
| `EXPIRED` | retention window ended | no retry guarantee remains |

## Storage choices

| Store | Strength | Weakness | Best fit |
|-------|----------|----------|----------|
| SQL table with unique key | strong constraints, transactional with business row | can become hot at high write rates | payments, orders, account commands |
| Redis with TTL | low latency, natural expiry | memory cost, persistence trade-offs | short retry windows, API gateways |
| DynamoDB / key-value store | high scale, conditional writes, TTL support | eventual behavior must be understood | multi-tenant APIs, serverless workflows |
| Kafka compacted topic | replayable key history | compaction lag and operational complexity | event processors and stream dedupe |
| Stream processor state store | colocated with windowed aggregation | tied to processing framework | ad-click/event counting windows |

The safest pattern for business-critical writes is often: reserve idempotency key and business command in the same transactional store, publish side effects through an outbox, then reconcile external systems by stable references. See [Distributed Transactions](../distributed-transactions/THEORY.md) for choosing between local transactions, sagas, outbox, TCC, 2PC, and reconciliation.

## Capacity and retention math

Use this sizing formula:

```text
storage_bytes =
  writes_per_second * retention_seconds * bytes_per_record * replication_factor
```

Then add index overhead, hot-key skew, and operational headroom.

| Domain | Typical retention | Why |
|--------|-------------------|-----|
| Payment intent create/confirm | 24 hours to 7 days for client retries; longer audit in ledger | users and gateways retry after timeouts; ledger records stay much longer |
| Webhook provider events | 7 to 30 days | providers may retry for days; reconciliation needs duplicate suppression |
| Ad click dedupe | minutes to days depending on billing window | late events and replay windows define business correctness |
| Job execution keys | job schedule period + retry horizon | recurring jobs need run-specific keys, not one global job key |
| Agent tool calls | task/session window or external side-effect SLA | model loops can replay tool calls after context or network failures |

Example: 15K payment intent writes/sec, 24-hour API idempotency retention, 200 bytes/record, replication factor 3:

```text
15,000 * 86,400 * 200 * 3 ~= 778 GB
```

That is too large for casual in-memory storage unless the actual key volume is lower or the record is smaller. For high-scale systems, separate hot retry cache from durable audit/ledger records.

## Failure semantics

| Failure | Correct handling |
|---------|------------------|
| Server commits but client times out | replay the committed resource/result for the same key |
| Same key with different payload | reject with `409 Conflict`; do not guess caller intent |
| Crash after reserving key before side effect | leave `PENDING` with timeout, owner lease, or repair job |
| Crash after external side effect before local final write | reconcile by external reference and complete local record |
| Queue redelivers processed message | dedupe by event id before side effect or use idempotent upsert |
| Webhook arrives out of order | dedupe provider event id and enforce state-machine transitions |
| TTL expires then client retries | guarantee is gone; require lookup by business resource id or return expiry error |
| Multi-region active-active duplicate | scope keys by tenant and route to a home region or use globally consistent conditional write |

## When to use

- Payment create/confirm/refund APIs.
- Order placement and inventory reservation.
- Job scheduling, workflow steps, and background workers.
- Event ingestion, click counting, metrics, and stream processing.
- Webhooks, callbacks, reconciliation, and replay/backfill jobs.
- Agent tools that mutate external systems.

## When NOT to overbuild it

- Pure reads.
- Naturally idempotent full replacements.
- Local-only operations with no retry or external side effect.
- Low-value metrics where at-most-once loss or approximate dedupe is acceptable.

Even then, be explicit. "We accept duplicate metrics within 1%" is better than silently pretending exactly-once exists.

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Long retention | safer late retries and replays | higher storage cost |
| Short retention | lower cost and simpler cleanup | retry after expiry can duplicate side effects |
| Strong unique constraint | simple correctness | write hotspot risk |
| In-memory TTL cache | fast duplicate detection | weaker durability |
| Per-step workflow keys | precise retries | more state to manage |
| Global keys | cross-region safety | latency and availability trade-off |

## Observability and abuse controls

Track these metrics:

- duplicate-hit rate;
- key conflict rate with different payload hashes;
- in-flight key age;
- key-store saturation and eviction count;
- replay-after-expiry attempts;
- webhook duplicate/out-of-order count;
- retry depth by endpoint and tenant;
- reconciliation repairs caused by ambiguous outcomes.

Guard against abuse:

- scope keys by tenant/user;
- reject oversized keys and PII-bearing keys;
- apply per-tenant unique-key rate limits;
- expire pending keys with a repair path;
- avoid predictable global keys that let one tenant probe another tenant's operations.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Correctness boundary | identifies the exact side effect and key owner | says "make it idempotent" generically |
| API semantics | handles same payload, different payload, pending, success, expiry | only stores a request id |
| Failure handling | covers timeout, crash, duplicate webhook, replay | assumes the first attempt always finishes cleanly |
| Capacity | sizes key store by QPS, TTL, record size, replication | ignores retention/storage cost |
| Operations | metrics, repair, and abuse controls included | no observability for duplicate suppression |

## Common pitfalls

- Claiming exactly-once execution instead of at-least-once delivery plus idempotent side effects.
- Using one global idempotency key across multiple operations.
- Not binding a key to a payload hash.
- Retrying external calls before reserving the local command key.
- Letting `PENDING` keys live forever.
- Treating idempotency as a replacement for transactions, locks, or reconciliation.
- Using raw PII or payment details inside keys.

## Related concepts

- [API Design](../api-design/THEORY.md)
- [Message Queues](../message-queues/THEORY.md)
- [Kafka](../kafka/THEORY.md)
- [Workflow Orchestration](../workflow-orchestration/THEORY.md)
- [Contention Control](../contention-control/THEORY.md)
- [Monitoring & Observability](../monitoring-observability/THEORY.md)
- [Payment System HLD](../../04-hld-projects/payment-system/)
- [Ad Click Aggregator HLD](../../04-hld-projects/ad-click-aggregator/)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
- [Prompting, Tools & Agents](../../06-genai-systems/00-concepts/prompting-tools-agents/)
