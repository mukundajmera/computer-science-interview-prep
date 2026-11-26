# Ride Sharing — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | Scope clarity and lifecycle framing |
| 2 | Estimation | 10% | Location/update throughput math |
| 3 | API Design | 15% | Correct rider/driver contracts |
| 4 | Data Model | 15% | Ride and driver state modeling |
| 5 | Architecture | 20% | Split ingestion, matching, lifecycle paths |
| 6 | Deep Dives | 20% | Matching, geo indexing, surge/ETA |
| 7 | Trade-offs & Communication | 10% | Consistency and latency rationale |

## Dimension Signals (1 / 3 / 5)

### 1. Requirements
- **1:** Unbounded feature list.
- **3:** Captures request/match/track flow.
- **5:** Prioritizes core lifecycle and constraints explicitly.

### 2. Estimation
- **1:** No throughput math.
- **3:** Rough update and ride volume estimates.
- **5:** Estimates drive architecture split and capacity plan.

### 3. API Design
- **1:** Vague endpoints.
- **3:** Core rider/driver endpoints present.
- **5:** Includes idempotency and state-transition actions.

### 4. Data Model
- **1:** Flat ride table only.
- **3:** Ride/driver/location modeled.
- **5:** Explicit transition-safe state machine with availability model.

### 5. Architecture
- **1:** Single service path.
- **3:** Service decomposition exists.
- **5:** Correct separation of write-heavy location path and assignment path.

### 6. Deep Dives
- **1:** No matching logic detail.
- **3:** Basic nearest-driver explanation.
- **5:** Covers offer loops, boundary cases, and overload handling.

### 7. Trade-offs & Communication
- **1:** No trade-offs discussed.
- **3:** Mentions alternatives.
- **5:** Clear decisions with revisit triggers.
