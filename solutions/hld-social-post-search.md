
# 🏆 Coach Answer: Social Post Search — HLD

> **Type:** High-Level Design
> **Difficulty:** Advanced
> **Time Target:** 45 minutes

## Phase 1 — Requirements (5 min)

- Clarify core functional requirements and strict out-of-scope boundaries.
- Lock non-functional goals that affect design choices.

## Phase 2 — Capacity and pressure points (5 min)

- Derive read/write envelopes and burst assumptions.
- Identify one primary bottleneck to anchor architecture.

## Phase 3 — API and data model (10 min)

- Define request contracts with idempotency/cursor semantics.
- Model core entities and critical state transitions.

## Phase 4 — Architecture (15 min)

- Present explicit read path, write path, and async path.
- Add resilience controls: retries, DLQ, replay, and degraded mode.

## Phase 5 — Deep dives (7 min)

1. Correctness boundary.
2. Hotspot mitigation.
3. Recovery and replay strategy.

## Phase 6 — Trade-offs and wrap-up (3 min)

- Explain one intentional trade-off and one evolution trigger.
