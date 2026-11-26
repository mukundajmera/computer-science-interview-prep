# Interview Questions: Idempotency

## Basic Questions

### 1. What is idempotency?
**A:** Idempotency means repeating the same logical operation has the same externally visible effect as running it once. In distributed systems, it usually means using a stable key or event identity so retries do not create duplicate side effects.

### 2. Why is idempotency important for retries?
**A:** A timeout does not prove the operation failed. The server may have committed and lost the response. Idempotency lets the client retry and receive the original result instead of creating a second charge, job, booking, or counter update.

### 3. Is `POST` always non-idempotent?
**A:** No. HTTP `POST` is not naturally idempotent, but you can make a specific `POST` endpoint operationally idempotent with an idempotency key, request hash, stored result, and expiry policy.

### 4. What should happen if the same idempotency key is reused with a different payload?
**A:** Return a conflict such as `409`. The system should bind each key to a payload hash; otherwise a client bug can silently map two different business commands to one result.

### 5. Is idempotency the same as deduplication?
**A:** They overlap but are not identical. Idempotency defines safe repeat semantics for an operation. Deduplication suppresses repeated events or messages. A payment API may use idempotency keys, while an event pipeline may use event-id dedupe.

## Intermediate Questions

### 6. How would you design an idempotent payment intent API?
**A:** Require `Idempotency-Key` scoped by merchant/account, store payload hash and status under a unique constraint, reserve the key before calling the gateway, replay the stored response on duplicate retries, reject payload mismatch, and reconcile ambiguous gateway outcomes by provider reference.

### 7. How do you handle a retry while the original request is still running?
**A:** Store a `PENDING` state. The duplicate request can return `202 Accepted` with a status URL, wait briefly for completion, or return the current resource state. It should not start a second side effect.

### 8. Where should the idempotency key live in a queue consumer?
**A:** At the consumer side-effect boundary. Use message id, business event id, or `(producer_id, sequence)` to guard the write. Offsets alone are not enough when processing can crash after side effects but before acknowledgment.

### 9. How do TTL windows affect correctness?
**A:** The guarantee only holds while the key is retained. If a client retries after expiry, the system can duplicate the side effect unless it can identify the business resource another way. Interviews should state the retention window and what happens after expiry.

### 10. Why can "exactly once" be misleading?
**A:** Networks and brokers usually provide at-least-once delivery or exactly-once within a narrow subsystem. End-to-end correctness still depends on idempotent handlers, transactional writes, dedupe stores, and reconciliation.

## Advanced Questions

### 11. What happens if the service crashes after charging the gateway but before storing success?
**A:** This is the hard ambiguous-outcome case. Use stable gateway references, transactional outbox where possible, and reconciliation jobs. On recovery, query or consume provider state and complete the local idempotency record rather than issuing another charge blindly.

### 12. How would you size an idempotency store?
**A:** Use `writes/sec * retention_seconds * bytes_per_record * replication_factor`, then add index overhead and headroom. For example, 15K writes/sec for 24 hours at 200 bytes with RF=3 is about 778 GB, so a high-scale payment API may need partitioning and separate hot cache versus durable ledger.

### 13. How do you handle multi-region idempotency?
**A:** Prefer routing a key to a home region or using a globally consistent conditional write for the key. Active-active writes with region-local dedupe can accept the same key twice during replication lag.

### 14. How do idempotency and locks differ?
**A:** A lock coordinates concurrent access while an operation runs. Idempotency recognizes repeated logical commands over time. Many systems need both: a lock or transaction for conflict control, plus idempotency for retries and replay.

### 15. What metrics would you add?
**A:** Duplicate-hit rate, payload-hash conflict rate, in-flight key age, key-store eviction, replay-after-expiry attempts, webhook duplicate/out-of-order count, retry depth, and reconciliation repairs.

## Domain Drills

### Payment System
**Q:** A client times out after confirming a payment and retries with the same key. What should happen?

**A:** Return the original payment intent or transaction state. Do not issue another gateway charge. If the gateway outcome is unknown, expose pending status and let reconciliation complete it.

### Ad Click Aggregator
**Q:** How do you prevent duplicate click delivery from inflating billing counters?

**A:** Give each click an event id or impression-click pair, store dedupe state for the billing window, drop duplicates before aggregation, and preserve immutable raw logs for replay/reconciliation.

### Job Scheduler
**Q:** How do you avoid executing the same scheduled job run twice?

**A:** Use a run key such as `(job_id, scheduled_fire_time)`, acquire a lease for execution, make the handler idempotent, and record final run state so retries replay or no-op.

### Agent Tooling
**Q:** Why do GenAI tools need idempotency?

**A:** Agent loops can retry tool calls after network errors or context replays. Read tools are naturally safer; write tools need idempotency keys, confirmation gates, or compensating controls.

## Rapid Follow-up Drill

1. What is your idempotency key for this endpoint?
2. Is the key scoped by tenant/user?
3. What payload hash do you store?
4. What do duplicate in-flight calls return?
5. What is the TTL, and why?
6. What happens after TTL expiry?
7. Which side effects are protected by this key?
8. How do you handle provider webhooks?
9. What metrics detect broken idempotency?
10. Where does reconciliation repair ambiguous outcomes?

## Strong Interview Summary

"I would treat retries as normal, not exceptional. For every side-effecting API, queue consumer, webhook, and workflow step, I define a stable operation identity, bind it to a payload hash, reserve it before executing the side effect, store the final result, and replay that result for duplicate attempts. I also state the TTL, storage sizing, payload-mismatch behavior, pending behavior, and reconciliation path for ambiguous external outcomes."
