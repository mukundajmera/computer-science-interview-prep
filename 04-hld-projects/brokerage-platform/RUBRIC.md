# Brokerage Platform — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | Correctly scopes brokerage vs exchange |
| 2 | Estimation | 10% | Fanout and order throughput math drives architecture |
| 3 | API Design | 15% | Idempotent order APIs and stream contract |
| 4 | Data Model | 15% | Explicit order state machine and event trail |
| 5 | Architecture | 20% | Read-fanout and write-command path separation |
| 6 | Deep Dives | 20% | Reconciliation, backpressure, failure handling |
| 7 | Trade-offs & Communication | 10% | Clear rationale for latency/correctness balance |

## Dimension Signals (1 / 3 / 5)

### 1. Requirements
- **1:** Treats problem as generic CRUD.
- **3:** Captures live prices and order lifecycle.
- **5:** Explicitly defines exchange boundary and correctness-critical operations.

### 2. Estimation
- **1:** No throughput assumptions.
- **3:** Rough subscribers/orders numbers.
- **5:** Uses burst periods to justify fanout and durable command design.

### 3. API Design
- **1:** Missing cancel/status semantics.
- **3:** Basic endpoints listed.
- **5:** Idempotency keys, conflict model, and stream sequencing explained.

### 4. Data Model
- **1:** Flat order table only.
- **3:** Order state captured.
- **5:** Order + order-event model with legal transitions and auditability.

### 5. Architecture
- **1:** Single service for everything.
- **3:** Service split exists.
- **5:** Explicitly decouples quote fanout and order command pipelines.

### 6. Deep Dives
- **1:** No failure story.
- **3:** Mentions retries.
- **5:** Covers ack ambiguity, replay safety, and reconciliation workflows.

### 7. Trade-offs & Communication
- **1:** Tool listing without rationale.
- **3:** Mentions alternatives.
- **5:** Quantified, contextual decisions and evolution triggers.
