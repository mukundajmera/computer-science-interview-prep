# Metrics Monitoring — Interview Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---|---|
| Requirement framing | 10% | Defines metric types, cardinality limits, retention tiers, and alert SLAs |
| Capacity planning | 15% | Converts samples/sec and label cardinality into storage/index budgets |
| API + query model | 10% | Write/query APIs include tenant and label constraints |
| Data model | 15% | Time-series chunks, index metadata, and downsample rollups are coherent |
| Architecture | 20% | Ingestion, TSDB storage, query engine, and alert evaluator are separated |
| Reliability + correctness | 20% | Handles late data, scrape gaps, and alert noise with clear policy |
| Communication | 10% | Discusses cost vs precision trade-offs concretely |

## Score bands (0-35)
- **30-35:** Strong hire; strong handling of cardinality and alert correctness.
- **22-29:** Hire; mostly complete with minor query-path omissions.
- **15-21:** Lean no-hire; weak on time-series constraints.
- **<15:** No-hire; generic logging-style design presented as metrics platform.

## Related content
- [Monitoring and Observability](../../03-hld-concepts/monitoring-observability/THEORY.md)
- [Realtime Metrics Platform (Advanced)](../realtime-metrics-platform/)
