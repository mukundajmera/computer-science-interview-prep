# Ticketing Platform — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | Correctly scopes seat contention and hold TTL |
| 2 | Estimation | 10% | Peak onsale math drives architecture |
| 3 | API Design | 15% | Hold/booking/idempotency endpoints are coherent |
| 4 | Data Model | 15% | Seat state machine is explicit and safe |
| 5 | Architecture | 20% | Queue + hold + booking separation |
| 6 | Deep Dives | 20% | Locking, spikes, payment failure handling |
| 7 | Trade-offs | 10% | Clear reasoning across consistency, UX, and cost |

---

## 1. Requirements

- **1 (Poor):** Skips hold semantics; treats all flows as simple CRUD.
- **3 (Acceptable):** Captures search, hold, booking, and non-functional targets.
- **5 (Strong):** Explicitly defines booking correctness, queueing assumptions, and out-of-scope boundaries.

## 2. Estimation

- **1:** No peak/burst estimate.
- **3:** Rough QPS and event volume estimates.
- **5:** Uses peak onsale burst and seat-action throughput to justify queueing and cache strategy.

## 3. API Design

- **1:** Missing hold/booking transition details.
- **3:** Defines core endpoints and responses.
- **5:** Adds idempotency, error model (`409`, `429`), and hold-expiry semantics.

## 4. Data Model

- **1:** No seat lifecycle model.
- **3:** Defines seats/holds/bookings with basic fields.
- **5:** Enforces valid state transitions and ownership checks.

## 5. Architecture

- **1:** Single service box design.
- **3:** Multi-service decomposition with caching.
- **5:** Admission queue, hold isolation, and orchestration flow are all failure-aware.

## 6. Deep Dives

- **1:** No contention strategy.
- **3:** Mentions lock and retries.
- **5:** Covers distributed hold semantics, fairness under spikes, and reconciliation.

## 7. Trade-offs & Communication

- **1:** Tool naming only, no reasoning.
- **3:** Mentions alternatives.
- **5:** Quantifies why choices are made now and when to revisit.
