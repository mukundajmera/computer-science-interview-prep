# YouTube Top-K - Follow-Up Questions

## Follow-up questions
1. How would `ViewEventIngestor` deduplicate retried view events?
2. What data structure would `WindowedTopKAggregator` use for frequent top-K queries?
3. How do you define window boundaries for late or out-of-order events?
4. What tie-breaker makes top-K results deterministic when counts match?
5. How should `WindowStateStore` expire old windows without breaking active queries?

## Variants and extensions
1. Top-K by region, channel, or category.
2. Sliding windows instead of fixed windows.
3. Approximate heavy-hitter tracking.
4. External stream processor behind the aggregation interface.

## Interviewer probes to prepare
- "Why not sort all videos on every query?"
- "What is the source of truth for a window's count?"
- "What changes when events arrive late?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
