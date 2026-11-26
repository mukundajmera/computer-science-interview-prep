# Brokerage Platform — Strong Interview Answer (45 Minutes)

Say: "I will optimize the design around correctness of orders, positions, and audit trails first; low latency matters, but never at the cost of duplicated orders or incorrect account state."

## 0-5 min: Requirements
- Scope live quotes + order create/cancel/status.
- Clarify brokerage boundary vs exchange internals.
- Set consistency priority for order state.

## 5-10 min: Estimates
- Model peak websocket subscribers at market open.
- Estimate daily order volume and retry amplification.

## 10-15 min: API + Entities
- Present idempotent order APIs and quote stream contract.
- Define order state machine and order event log.

## 15-30 min: Architecture
- Draw two-path architecture: quote fanout vs order commands.
- Show exchange adapter, durable events, and reconciliation worker.

## 30-40 min: Deep Dives
1. Ambiguous external ack handling.
2. Backpressure and stream reliability.
3. Replay and reconciliation safety.

## 40-45 min: Trade-offs + Wrap
- Chosen now: low-latency websocket fanout and strongly consistent order transitions.
- Revisit trigger: if reconciliation lag or pending-state tail grows above SLO.
