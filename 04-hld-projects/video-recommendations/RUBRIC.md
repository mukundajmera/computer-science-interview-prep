# Video Recommendations — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | objective clarity beyond CTR |
| 2 | Estimation | 10% | scale math justifies multi-stage design |
| 3 | API Design | 10% | context + feedback contracts |
| 4 | Data Model | 15% | candidate/ranking/feedback lifecycle |
| 5 | Architecture | 20% | candidate generation + ranking cascade |
| 6 | Deep Dives | 20% | exploration, cold start, feedback loops |
| 7 | Trade-offs & Communication | 15% | short-term vs long-term metric balance |

## Dimension Signals (1 / 3 / 5)

### 1. Requirements
- **1:** “maximize clicks.”
- **3:** clear engagement target.
- **5:** long-term satisfaction objective with constraints.

### 2. Estimation
- **1:** no request/catalog math.
- **3:** baseline QPS estimate.
- **5:** quantitative proof single-stage scoring is infeasible.

### 3. API Design
- **1:** one opaque endpoint.
- **3:** request + response basics.
- **5:** explicit context schema and feedback ingestion.

### 4. Data Model
- **1:** no candidate/rank lineage.
- **3:** stores final recommendations.
- **5:** stores candidate sources, ranking features, and delayed outcomes.

### 5. Architecture
- **1:** monolithic ranker only.
- **3:** two-stage rough design.
- **5:** robust multi-stage retrieval/ranking with operational controls.

### 6. Deep Dives
- **1:** hand-wavy “use ML model.”
- **3:** mentions cold start/exploration.
- **5:** concrete explore budget, drift monitoring, long-horizon eval plan.

### 7. Trade-offs & Communication
- **1:** no alternatives discussed.
- **3:** basic pros/cons.
- **5:** clear narrative connecting metrics to business outcomes.
