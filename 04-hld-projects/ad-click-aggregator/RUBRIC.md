# Ad Click Aggregator — Interview Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---|---|
| Requirement framing | 10% | Distinguishes ingestion, attribution windows, and reporting latency |
| Estimation | 15% | Calculates events/sec, skewed keys, and retention tiering |
| API/contract design | 10% | Defines event schema, idempotency key, and late-event policy |
| Data model | 15% | Event log + aggregate tables align with query dimensions |
| Processing architecture | 20% | Stream ingestion, dedup, windowed aggregation, and serving path are coherent |
| Correctness depth | 20% | Handles duplicate clicks, out-of-order events, and backfill replay |
| Communication | 10% | Trade-offs on exactness vs timeliness are explicit |

## Score bands (0-35)
- **30-35:** Strong hire; strong event-time reasoning and replay safety.
- **22-29:** Hire; mostly complete with minor edge-case gaps.
- **15-21:** Lean no-hire; unclear on dedup/window correctness.
- **<15:** No-hire; misses core stream-aggregation fundamentals.

## Related content
- [Stream Processing](../../03-hld-concepts/stream-processing/THEORY.md)
- [Duplicate Handling and Idempotent Consumers](../../03-hld-concepts/message-queues/INTERVIEW-QA.md)
- [LLD Ad Click Aggregator](../../02-lld-projects/ad-click-aggregator/)
