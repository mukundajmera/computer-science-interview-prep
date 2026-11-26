# Rate Limiter - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Identifies key dimensions (scope, key, fallback mode, metadata) |
| API contract quality | 20% | Returns stable, rich decision contract |
| Algorithm architecture | 25% | Clean strategy/factory split with testable algorithm units |
| Correctness and concurrency | 25% | No over-admission under contention; atomic state updates |
| Extensibility and communication | 15% | Clear local-to-distributed evolution path |

## Performance bands
- `1/5`: hard-coded limiter with boolean-only output.
- `3/5`: working limiter with one algorithm and partial metadata.
- `5/5`: race-safe design, clean boundaries, and practical scale/failure tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Movie Ticket Booking rubric](../movie-ticket-booking/RUBRIC.md)
