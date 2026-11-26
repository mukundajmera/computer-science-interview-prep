# Live Comments - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies ingestion, fanout, replay, reconnect state, invalid mutations, and idempotency scope |
| Service boundaries | 25% | Separates `CommentIngressService`, `CommentFanoutService`, `CommentReplayStore`, and `LiveSessionRegistry` |
| Delivery correctness | 25% | Preserves deterministic comment ordering, replay snapshots, and safe reconnect behavior |
| Latency and storage tradeoffs | 20% | Explains O(1)/O(log n) writes, indexed lookup, bounded replay windows, and fanout cost |
| Extensibility and communication | 15% | Walks v1 to v3 from in-memory comments to repository boundaries, thread safety, and replay-safe mutations |

## Performance bands
- `1/5`: appends comments to a list and pushes them without replay or session state.
- `3/5`: supports ingest, fanout, and recent reads but has weak reconnect or duplicate handling.
- `5/5`: clean live-session design with deterministic replay, bounded reads, idempotent ingest, and explicit fanout tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
