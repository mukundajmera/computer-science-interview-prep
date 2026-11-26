# Instagram Core - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies media posting, follow graph behavior, feed reads, invalid mutations, and idempotency scope |
| Service boundaries | 25% | Separates `MediaPostService`, `FollowGraphService`, `FeedComposer`, and `MediaStorageGateway` responsibilities |
| Feed correctness | 25% | Produces deterministic timeline snapshots from posts and follow relationships without leaking invalid state |
| Read/write performance | 20% | Explains O(1)/O(log n) writes, indexed lookups, and bounded-window feed reads |
| Extensibility and communication | 15% | Walks v1 to v3 from in-memory model to repositories, storage gateway, thread safety, and replay-safe mutations |

## Performance bands
- `1/5`: blends posting, storage, follows, and feed composition into one mutable service.
- `3/5`: working in-memory posting and follows with basic feed reads but weak idempotency or boundary handling.
- `5/5`: clean service split with deterministic feeds, validated mutations, indexed reads, and explicit v3 replay/concurrency tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
