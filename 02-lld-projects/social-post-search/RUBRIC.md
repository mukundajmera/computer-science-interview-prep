# Social Post Search - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies post ingestion, keyword queries, ranking, invalid mutations, and idempotency scope |
| Indexing design | 25% | Separates `PostIngestionService`, `InvertedIndex`, `QueryPlanner`, and `SearchRankingService` |
| Query correctness | 25% | Handles token normalization, multi-term planning, deterministic ranking, and stale-post updates |
| Performance and bounds | 20% | Explains indexed lookup, O(1)/O(log n) writes, bounded result windows, and ranking cost |
| Extensibility and communication | 15% | Walks v1 to v3 from in-memory index to repository boundaries, alternate stores, and thread-safe updates |

## Performance bands
- `1/5`: scans every post for every search with no index or ranking boundary.
- `3/5`: builds an inverted index but under-explains updates, ranking, or deterministic query results.
- `5/5`: clear ingestion/index/query/ranking split with bounded reads, update handling, idempotent ingestion, and v3 storage/concurrency tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
