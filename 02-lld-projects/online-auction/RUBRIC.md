# Online Auction - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies auction lifecycle, bid ordering, minimum increment, close behavior, and read views |
| Lifecycle modeling | 25% | Uses explicit auction states so bids cannot be accepted before start or after close |
| Bid correctness | 25% | Enforces monotonic bidding, validates bidder/auction input, and returns deterministic results |
| Contention boundaries | 20% | Separates bid validation, repository writes, snapshots, and idempotency concerns |
| Extensibility and communication | 15% | Explains v1 to v3 progression without coupling the design to one storage or locking strategy |

## Performance bands
- `1/5`: simple key/value store or append-only bid list with unclear lifecycle rules.
- `3/5`: working in-memory auction service with basic validation and query support.
- `5/5`: state-driven bid flow with repository/policy boundaries, deterministic mutation contracts, and replay-safe idempotency discussion.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
