# Quick Commerce Delivery — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | Availability vs order correctness is separated |
| 2 | Estimation | 10% | Read-heavy ratios and hotspot assumptions |
| 3 | API Design | 15% | Clean availability + order contracts |
| 4 | Data Model | 15% | Center inventory model and order schema |
| 5 | Architecture | 20% | Distinct read/write paths and geo routing |
| 6 | Deep Dives | 20% | Locking/OCC, cache invalidation, failover |
| 7 | Trade-offs | 10% | Latency vs freshness vs correctness rationale |

---

## 1. Requirements

- **1:** Treats system as generic shopping cart.
- **3:** Captures availability and ordering at high level.
- **5:** Explicitly defines local delivery constraints, correctness boundary, and exclusions.

## 2. Estimation

- **1:** No throughput assumptions.
- **3:** Gives rough availability/order QPS.
- **5:** Quantifies read skew and hotspot implications that drive cache and partition choices.

## 3. API Design

- **1:** Vague endpoints and payloads.
- **3:** Core endpoints present.
- **5:** Idempotent order creation and paginated availability with clear error semantics.

## 4. Data Model

- **1:** Missing center-level inventory.
- **3:** Defines basic inventory/order tables.
- **5:** Includes versioned inventory updates and order line outcomes.

## 5. Architecture

- **1:** Single path for all flows.
- **3:** Basic service decomposition.
- **5:** Read/write separation, geo resolution, and cache strategy are coherent.

## 6. Deep Dives

- **1:** No contention handling.
- **3:** Mentions locking.
- **5:** Shows robust OCC/transaction strategy and failure-aware cache handling.

## 7. Trade-offs & Communication

- **1:** No reasoned decisions.
- **3:** Mentions alternatives.
- **5:** Clearly communicates why each design choice matches requirements.
