# YouTube Top-K - Common Pitfalls

## Common pitfalls
1. Sorting all videos on every `TopKQueryService` request.
2. Counting views globally while ignoring the window requested by the problem.
3. Not defining tie-breakers for videos with equal counts.
4. Double-counting retried view events in v3.
5. Letting old window state grow forever.

## Why these fail interviews
- They miss the documented windowed aggregation model.
- They make top-K results non-deterministic across repeated queries.
- They hide the memory and cleanup costs of event-stream aggregation.

## Mitigations
- Make `WindowStateStore` the owner of per-window counts and cleanup.
- Maintain bounded top-K state or a heap-oriented update path per active window.
- Use stable tie-breakers such as count, timestamp, then video id.
- Add event identifiers for replay-safe ingestion.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
