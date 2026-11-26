# Bot Detection — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | clear abuse objective + FP constraints |
| 2 | Estimation | 10% | event-rate and label-capacity reasoning |
| 3 | API Design | 10% | account state, appeals, investigator label flow |
| 4 | Data Model | 15% | risk state + action/event lineage |
| 5 | Architecture | 20% | layered detection and policy enforcement |
| 6 | Deep Dives | 20% | adversarial drift, calibration, active labeling |
| 7 | Trade-offs & Communication | 15% | precision/coverage balance clarity |

## Dimension Signals (1 / 3 / 5)

### 1. Requirements
- **1:** “detect bots” only.
- **3:** Defines state/actions and constraints.
- **5:** Ties objective to abuse impact and user trust.

### 2. Estimation
- **1:** No scale math.
- **3:** Basic throughput estimate.
- **5:** Connects event and investigator limits to design boundaries.

### 3. API Design
- **1:** Single scoring endpoint.
- **3:** Score + status APIs.
- **5:** Includes appeals + investigator labels + auditability.

### 4. Data Model
- **1:** Flat score table.
- **3:** Risk state and action events.
- **5:** Full lineage for rollback/retraining and policy versioning.

### 5. Architecture
- **1:** monolithic ML block.
- **3:** model + action engine.
- **5:** layered realtime + async risk stack with safe fallbacks.

### 6. Deep Dives
- **1:** generic “monitor drift”.
- **3:** mentions calibration and labels.
- **5:** concrete active-learning + adversarial operations plan.

### 7. Trade-offs & Communication
- **1:** no explicit alternatives.
- **3:** simple pros/cons list.
- **5:** clear precision/coverage/business impact narrative.
