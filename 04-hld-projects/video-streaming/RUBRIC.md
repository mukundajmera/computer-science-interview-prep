# Video Streaming — Interview Scoring Rubric

## Weighted Rubric

| Dimension | Weight | Strong Signal |
|---|---|---|
| Requirements handling | 10% | playback + rec scope correctly separated |
| Estimation quality | 10% | egress + ranking latency/cost considered |
| API + contracts | 12% | upload lifecycle + rec endpoint clarity |
| Data modeling | 13% | media and recommendation entities modeled |
| Architecture quality | 20% | ingest/process/delivery + rec pipeline decomposition |
| Deep dives | 20% | multipart safety + multi-stage ranking + cold start/feedback controls |
| Trade-offs/communication | 15% | latency-quality-cost rationale is explicit |

## Score Bands

- **5/5:** clear media/data plane split, explicit stage latency budgets, practical cold-start handling, and robust loop safeguards.
- **3/5:** good playback design but recommendation path is shallow or lacks budgeted stages.
- **1/5:** monolithic design with no staged ranking, no cold-start strategy, or no upload resilience.
