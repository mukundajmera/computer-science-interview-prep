# Chat/Messaging Service - Strong Answer Outline (Time-Boxed)

Say: "I will separate connection fanout from durable message storage so online users get low latency while offline users still receive ordered, recoverable messages."

A structured, interview-ready outline for a WhatsApp-like chat system.

> Related docs: [PROBLEM](./PROBLEM.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

## Time allocation

| Phase | Time | Focus |
|---|---|---|
| Requirements and scope | 5 min | Confirm constraints and boundaries |
| Capacity estimates | 5 min | Size connection and message paths |
| API + data model + architecture | 12 min | End-to-end baseline |
| Deep dives | 15 min | Reliability and ordering |
| Trade-offs + wrap | 5 min | Decision quality |

## 1) Requirements and scope

- Clarify group limit, offline retention window, multi-device expectation, and privacy model for presence/last-seen.
- Confirm target latency and availability.
- Call out out-of-scope items (media internals, auth internals, full E2E implementation details).

## 2) Capacity estimates

- Estimate message write/read throughput.
- Estimate concurrent sessions and per-connection overhead.
- Translate numbers into explicit queue, storage, and connection-tier decisions.

## 3) API and data model

- REST for historical reads and metadata actions.
- Realtime channel for message send/ack/update events.
- Partition message storage by conversation access pattern.
- Keep ephemeral session/presence state in a low-latency cache tier.

## 4) Architecture

- Send path: validate -> persist -> enqueue -> online push or offline backlog.
- Read path: conversation history via cursor pagination.
- Group path: write-once then async fan-out.
- Reconnect path: replay from last confirmed cursor.

## 5) Deep dives that win WhatsApp-style rounds

### A. Reconnect and replay
- Define replay cursor contract and duplicate suppression.
- Include retry/backoff and idempotency policy.

### B. Out-of-order handling
- Define per-conversation ordering and tie-breaks.
- Explain client reconciliation for near-simultaneous sends.

### C. Presence degradation handling
- If presence cache is unhealthy, preserve message durability first.
- Defer/approximate last-seen updates while retaining delivery correctness.

### D. Multi-device consistency
- Keep session map by user+device.
- Track read cursors per device and propagate sync events.

## 6) Trade-offs

- Low-latency push channel vs operating persistent connections.
- Strong durability for messages vs eventual consistency for presence and read receipts.
- Simpler ordering model vs richer causal semantics complexity.

## 7) Wrap-up

- Summarize architecture in one path statement.
- Name one intentional compromise and one 10x evolution step.
- Tie answer back to reliability under unstable networks and massive concurrency.
