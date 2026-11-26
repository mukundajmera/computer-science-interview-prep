# Content Moderation — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | clear business objective + guardrails |
| 2 | Estimation | 10% | prevalence-aware throughput reasoning |
| 3 | API Design | 10% | policy decision + appeal/report contracts |
| 4 | Data Model | 15% | decision lineage + feedback lifecycle |
| 5 | Architecture | 20% | tiered moderation with action policy |
| 6 | Deep Dives | 20% | calibration, imbalance, drift, HITL |
| 7 | Trade-offs & Communication | 15% | precision/recall/business-harm articulation |

## Dimension Signals (1 / 3 / 5)

### 1. Requirements
- **1:** Vague “block bad content” framing.
- **3:** Defines core actions and metrics.
- **5:** Links objective to harm exposure with precision guardrails.

### 2. Estimation
- **1:** No volume/prevalence math.
- **3:** Basic QPS estimates.
- **5:** Uses prevalence + review capacity to shape architecture.

### 3. API Design
- **1:** Single opaque endpoint.
- **3:** Evaluate + decision retrieval.
- **5:** Includes reports/appeals and decision traceability.

### 4. Data Model
- **1:** One score table only.
- **3:** Decision records + queue.
- **5:** Full lineage (policy version, reason, feedback events).

### 5. Architecture
- **1:** One-model black box.
- **3:** Model + action service.
- **5:** Tiered risk pipeline with policy and review orchestration.

### 6. Deep Dives
- **1:** Generic comments on model quality.
- **3:** Mentions thresholds + drift.
- **5:** Concrete calibration, imbalance, and adversarial adaptation plan.

### 7. Trade-offs & Communication
- **1:** No explicit alternatives.
- **3:** Lists pros/cons at high level.
- **5:** Quantifies precision/recall impact against business harm.
