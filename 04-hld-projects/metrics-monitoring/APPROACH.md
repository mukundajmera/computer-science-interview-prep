# Design Approach for Metrics Monitoring

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify requirements | 6 min | Metric types, cardinality rules, alerting SLA |
| Capacity estimation | 6 min | Samples/sec, label explosion risk, retention tiers |
| API + data model | 10 min | Write/query contracts, series/chunk schema |
| Architecture | 13 min | Ingestion, TSDB storage, query engine, alert evaluator |
| Deep dives | 7 min | Cardinality guardrails, late data, alert-noise control |
| Wrap-up | 3 min | Migration path to advanced realtime platform |

## Suggested execution order
1. Lock cardinality and retention constraints before storage choice.
2. Define write/query/alert interfaces.
3. Design TSDB hot/warm/cold data path.
4. Add alert evaluation and tenant isolation controls.
5. Close with cost optimization and advanced-variant bridge.
