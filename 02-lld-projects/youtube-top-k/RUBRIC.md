# YouTube Top-K - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies view ingestion, time windows, top-K queries, invalid events, and idempotency scope |
| Aggregation model | 25% | Separates `ViewEventIngestor`, `WindowedTopKAggregator`, `TopKQueryService`, and `WindowStateStore` |
| Top-K correctness | 25% | Maintains deterministic ranking per window with clear tie-breakers and replay-safe event handling |
| Performance and storage bounds | 20% | Explains O(1)/O(log n) updates, indexed/windowed lookup, bounded K reads, and window-state cleanup |
| Extensibility and communication | 15% | Walks v1 to v3 from in-memory aggregation to repository boundaries, thread safety, and distributed-friendly interfaces |

## Performance bands
- `1/5`: stores all events and sorts every query without a window model.
- `3/5`: counts views per video but under-explains windowing, ties, retries, or cleanup.
- `5/5`: clear windowed aggregation with deterministic top-K results, idempotent ingest, bounded query cost, and v3 concurrency/storage tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
