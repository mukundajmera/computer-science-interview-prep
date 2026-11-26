# Ad Click Aggregator — LLD Rubric

| Dimension | Strong signal |
|---|---|
| Event model | Event identity, timestamp, and attribution dimensions are explicit |
| Aggregation logic | Window semantics and query path are deterministic |
| Reliability | Dedup and late-event rules are modular and testable |
| Concurrency | Safe counter updates and bounded ingestion queue in `v3` |
| Test quality | Duplicate, out-of-order, and replay cases are covered |
| Parity | Equivalent Java/Python policy abstractions |

## Red flags
- Counter updates without dedup boundary.
- Mixing ingest schema directly with query DTOs.
- No replay or reset strategy.
