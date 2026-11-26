# Price Tracking Service - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies price event shape, history windows, subscription thresholds, dispatch guarantees, and read views |
| Event and history modeling | 25% | Separates latest price, historical records, mutation intents, and query snapshots |
| Alert correctness | 25% | Triggers threshold dispatch from validated price changes without duplicate or missed notifications |
| Storage boundaries | 20% | Uses collector, history store, subscription service, and dispatcher contracts cleanly |
| Extensibility and communication | 15% | Explains v1 to v3 progression, idempotency, and distributed repository tradeoffs without overbuilding v1 |

## Performance bands
- `1/5`: simple key/value price map with no history, subscription, or retry story.
- `3/5`: working in-memory collector with history queries and basic alert dispatch boundaries.
- `5/5`: event-driven price flow with bounded history reads, idempotent writes, and explicit alert delivery semantics.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
