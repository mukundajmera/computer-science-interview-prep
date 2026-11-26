# Content Moderation Platform — Approach

## 45-Minute Flow

| Phase | Time | Expected Outcome |
|---|---|---|
| Scope and objectives | 6 min | Action ladder + precision constraints |
| Estimates | 5 min | Throughput and reviewer bottleneck |
| API + data model | 8 min | Explicit decision contract |
| Architecture | 12 min | Inference -> calibration -> enforcement |
| Deep dives | 10 min | HITL queueing, drift rollback |
| Wrap-up | 4 min | Trade-offs + next-scale bottleneck |

## Recommended Sequence

1. Set objective: minimize harmful exposure under false-positive budget.
2. Separate fast online path from slower review/feedback loops.
3. Define actions and thresholds before drawing components.
4. Show end-to-end traceability: score -> decision -> enforcement -> audit.
5. Deep dive on queue policy and safe policy rollout.
