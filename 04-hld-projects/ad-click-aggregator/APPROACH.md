# Design Approach for Ad Click Aggregator

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify requirements | 6 min | Event schema, attribution windows, freshness SLO |
| Capacity estimation | 6 min | Events/sec, duplicate rate, hot-key skew |
| API + data model | 10 min | Ingest contracts, dedup key, windowed aggregate schema |
| Architecture | 13 min | Ingestion log, stream aggregation, correction pipeline |
| Deep dives | 7 min | Event-time windows, late data, replay safety |
| Wrap-up | 3 min | Fraud detection and multi-tenant controls |

## Suggested execution order
1. Lock event-time correctness and late-event policy.
2. Define immutable ingest log and dedup boundaries.
3. Design windowed aggregation and query-serving path.
4. Add correction/backfill workflow.
5. Close with skew mitigation and cost controls.
