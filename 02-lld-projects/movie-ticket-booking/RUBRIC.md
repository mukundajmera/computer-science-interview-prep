# Movie Ticket Booking - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Captures lock TTL, ownership, and cancellation boundaries |
| Domain model quality | 20% | Clean `Show`/`ShowSeat`/`Booking` boundaries |
| Concurrency correctness | 30% | Atomic seat locking and exactly-one-confirmed winner |
| Failure handling | 20% | Safe timeout, payment failure, and cancellation transitions |
| Extensibility and communication | 15% | Clear version roadmap and practical scaling discussion |

## Performance bands
- `1/5`: ignores contention; seat state can be corrupted.
- `3/5`: handles happy path and basic locking but misses edge-case transitions.
- `5/5`: demonstrates race-safe lifecycle design, compatibility awareness, and clear tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Rate Limiter rubric](../rate-limiter/RUBRIC.md)
