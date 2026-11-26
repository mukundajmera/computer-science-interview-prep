# Chat/Messaging Service - Common Interview Pitfalls

Common failure patterns for WhatsApp-like chat interviews.

> Related docs: [PROBLEM](./PROBLEM.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

## 1. Treating polling as the primary realtime channel

- Mistake: Designing around periodic polling at large concurrency.
- Expected: Persistent channel (WebSocket/SSE) with controlled fallback and heartbeat.

## 2. No reconnect replay contract

- Mistake: Client reconnects and either misses or duplicates messages.
- Expected: Replay from `last_seen_message_id` or cursor, plus idempotent client message IDs.

## 3. Ignoring out-of-order delivery behavior

- Mistake: Assuming timestamps alone guarantee order.
- Expected: Per-conversation ordering keys, deterministic tie-breakers, and client-side reordering rules.

## 4. No offline delivery durability path

- Mistake: Online push only.
- Expected: Persist before ack, durable backlog, retry policy, and reconnect drain flow.

## 5. Group fan-out as synchronous loop

- Mistake: Blocking sender path while iterating all members.
- Expected: Write-once, async fan-out workers, batching by destination server.

## 6. Missing multi-device semantics

- Mistake: One user -> one session assumption.
- Expected: Per-device sessions, per-device cursor/ack, and reconciliation strategy.

## 7. Not defining behavior when presence cache degrades (Redis or equivalent)

- Mistake: Presence failure leads to delivery blackout.
- Expected: Degraded-mode policy (queue-first delivery, delayed presence updates, retry backoff).

## 8. Read receipts causing write amplification

- Mistake: Synchronous per-message receipt writes.
- Expected: Batched or checkpoint-style read acknowledgments with eventual consistency.

## 9. Last-seen/privacy ignored in architecture

- Mistake: Presence broadcast without audience constraints.
- Expected: Privacy policy enforcement (`everyone`, `contacts`, `nobody`) in presence pipeline.

## 10. E2E encryption implications handwaved

- Mistake: Claiming E2E and still proposing server-side full-text search/moderation on plaintext.
- Expected: Explicitly note feature constraints and viable alternatives.
