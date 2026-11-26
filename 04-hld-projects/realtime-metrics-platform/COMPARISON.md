# Real-Time Metrics Platform — Comparison

| Dimension | Metrics Monitoring | Real-Time Metrics Platform |
|---|---|---|
| Typical scale | Moderate-to-high | Very high ingest and bursty loads |
| Stream complexity | Optional/minimal | Core design component |
| Replay strategy | Basic retry | Dedicated replay/backfill controls |
| Cardinality policy | Basic guardrails | Strict tenant budgets + enforcement |
| Interview focus | Breadth | Depth and failure semantics |

## Related systems
- [Metrics Monitoring](../metrics-monitoring/)
- [Ad Click Aggregator](../ad-click-aggregator/)

## YouTube Top-K Comparison Notes
- The YouTube Top-K variant prioritizes ranked window queries over arbitrary ad hoc metric exploration.
- It tolerates some bounded approximation in exchange for faster heavy-hitter detection and lower memory pressure.
- Replay correctness is evaluated by rank stability and window finalization behavior, not only aggregate accuracy.
