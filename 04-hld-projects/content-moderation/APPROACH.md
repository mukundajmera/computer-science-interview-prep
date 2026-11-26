# Design Approach for Content Moderation

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify problem | 6 min | policy scope, modalities, guardrails, reviewer capacity |
| Estimation | 6 min | event volume, harmful prevalence, review queue size |
| API + state model | 8 min | evaluate/report/appeal contracts and decision lifecycle |
| Architecture | 13 min | ingestion, inference, policy action, feedback loop |
| Deep dives | 9 min | precision calibration, class imbalance, drift response |
| Wrap-up | 3 min | trade-offs, failure modes, next iteration |

## Suggested execution order

1. Lock business objective and precision guardrails.
2. Define decision states and policy actions.
3. Sketch online inference path + async enrichment path.
4. Add human-review and feedback ingestion loop.
5. Close with calibration/drift and abuse-evasion defenses.
