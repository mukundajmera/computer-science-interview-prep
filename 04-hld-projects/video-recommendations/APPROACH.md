# Design Approach for Video Recommendations

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify problem | 6 min | recommendation surface, objective, latency budget |
| Estimation | 6 min | DAU, catalog, candidate-set, request throughput |
| API + state model | 7 min | request context, response schema, feedback contract |
| Architecture | 14 min | multi-stage retrieval/ranking and serving path |
| Deep dives | 9 min | value model, feedback loops, cold start, exploration |
| Wrap-up | 3 min | trade-offs and quality guardrails |

## Suggested execution order

1. Lock business objective and operating metrics.
2. Define multi-stage architecture boundaries.
3. Specify candidate generators and ranking layers.
4. Add evaluation and feedback loop.
5. Close with exploration/cold-start safeguards.
