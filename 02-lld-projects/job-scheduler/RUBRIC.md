# Job Scheduler - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies one-time vs recurring jobs, pause/resume/cancel, retry, and observability scope |
| Domain model quality | 20% | Separates job definition, trigger, run attempt, worker pool, retry policy, and DLQ |
| Coordination correctness | 25% | Uses bounded producer-consumer handoff with explicit saturation behavior |
| Failure handling | 25% | Enforces retry caps, terminal states, dead-letter handoff, and safe recovery semantics |
| Extensibility and communication | 15% | Explains v1 to v3 evolution toward metrics, leases, recovery, and distributed ownership |

## Performance bands
- `1/5`: single loop with mixed responsibilities and undefined failure paths.
- `3/5`: functional scheduler with retries but weak concurrency boundaries.
- `5/5`: strong coordination model, deterministic transitions, and scalable evolution story.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
