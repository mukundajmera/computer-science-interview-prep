# Content Moderation Platform — Scoring Rubric

## Weighted Rubric

| Dimension | Weight | Strong Signal |
|---|---|---|
| Problem framing | 12% | objective + false-positive budget |
| Estimation | 10% | reviewer bottleneck included |
| API + decision contract | 13% | score, confidence, reasons, versioning |
| Data model | 15% | timeline/audit entities are explicit |
| Architecture | 20% | inference-calibration-enforcement split |
| Deep dives | 20% | queueing + drift + rollback details |
| Trade-offs + communication | 10% | decisions tied to risk and ops |

## Score Bands

- **5/5:** clearly models action ladder, HITL, and safe rollout controls.
- **3/5:** workable architecture but weak calibration or feedback loop.
- **1/5:** single black-box classifier with no audit or escalation.
