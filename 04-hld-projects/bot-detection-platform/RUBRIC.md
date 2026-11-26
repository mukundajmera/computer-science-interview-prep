# Bot Detection Platform — Scoring Rubric

## Weighted Rubric

| Dimension | Weight | Strong Signal |
|---|---|---|
| Framing | 12% | adversarial lens + FP constraints |
| Estimation | 10% | event scale and label scarcity impact |
| API + decision contract | 13% | risk + confidence + reason codes |
| Data model | 15% | snapshots + actions + timeline |
| Architecture | 20% | dual-path scoring + calibrated actions |
| Deep dives | 20% | adaptation loop + queue policy |
| Trade-offs + communication | 10% | risk-aware choices with clear rationale |

## Score Bands

- **5/5:** dynamic threat model, staged remediation, adaptation metrics.
- **3/5:** reasonable architecture but weak novel-attack handling.
- **1/5:** one static classifier with hard-ban defaults.
