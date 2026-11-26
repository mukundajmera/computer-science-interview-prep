# Collaborative Document Editor — Strong Interview Answer (45 Minutes)

Say: "I will make concurrent editing explicit: clients can be optimistic, but the server needs a deterministic merge model, durable operation log, and recovery path for reconnecting collaborators."

## 0-5 min: Requirements
- Scope simple text collaboration, not full formatting suite.
- Confirm realtime, convergence, and durability goals.

## 5-10 min: Estimates
- Estimate websocket concurrency and per-document edit rate.
- Use limits to justify doc-session sharding strategy.

## 10-15 min: API + Entities
- Define metadata REST APIs and websocket session endpoint.
- Define operation model and replay token contract.

## 15-30 min: Architecture
- Show session gateway, operation processor, operation log, snapshot worker.
- Separate metadata read/write from edit hot path.

## 30-40 min: Deep Dives
1. Convergence and conflict handling.
2. Reconnect replay and snapshot compaction.
3. Horizontal scaling with document-affinity routing.

## 40-45 min: Trade-offs + Wrap
- Chosen now: eventual convergence with durable operation log.
- Revisit trigger: replay latency or transform failure rate breaches SLO.
