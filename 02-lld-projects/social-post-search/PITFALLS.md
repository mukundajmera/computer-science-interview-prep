# Social Post Search - Common Pitfalls

## Common pitfalls
1. Using full scans after naming an `InvertedIndex`.
2. Mixing ingestion, query planning, and ranking into one method.
3. Ignoring token normalization and duplicate tokens in a post.
4. Forgetting to update or remove index entries when a post changes state.
5. Returning unbounded results without a deterministic tie-breaker.

## Why these fail interviews
- They miss the project docs' indexing and query-planning boundaries.
- They make search results inconsistent across repeated requests.
- They hide the cost of ranking and bounded-window reads.

## Mitigations
- Define the token-to-post mapping owned by `InvertedIndex`.
- Keep `QueryPlanner` responsible for term combination and candidate selection.
- Make `SearchRankingService` deterministic with explicit tie-breakers.
- Treat ingestion as a replay-safe mutation in v3.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
