# Real-Time Metrics Platform — Interview Scoring Rubric

| Dimension | Weight | Strong Signal |
|---|---|---|
| Requirements clarity | 10% | Distinguishes ingest/query/alert semantics |
| Estimation quality | 15% | Points/sec and retention math drive architecture |
| API design | 10% | Clean ingest/query/alert contracts with limits |
| Data model | 15% | Series identity + cardinality controls |
| Architecture | 20% | Clear hot/warm/cold separation |
| Deep dives | 20% | Time semantics, late data, alert correctness |
| Trade-offs & communication | 10% | Explicit alternatives with triggers |

## Score Bands

- **30-35**: Strong hire signal
- **22-29**: Hire, with limited depth gaps
- **15-21**: Lean no hire
- **<15**: No hire

## Common strong-answer behaviors

1. Quantifies ingest pressure before naming technologies.
2. Addresses cardinality and late events proactively.
3. Separates operational dashboards from historical analytics.
4. Explains alert correctness under delay/out-of-order arrivals.

---

## Top-K Variant Signals

Strong answers for this variant should include:

1. Window model selection (all-time + tumbling baseline).
2. Late-event handling contract.
3. Precompute/cache strategy for top-K queries.
4. Write-path scaling and partitioning rationale.
