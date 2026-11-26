# Job Scheduler

## Problem statement
Design a deterministic, interview-grade job scheduler with progressive implementations (`v1-basic`, `v2-extended`, `v3-optimized`) in Java and Python. The system should schedule and execute jobs safely under concurrent worker activity.

## Requirements and constraints

### Functional requirements
1. Submit one-time and recurring jobs with metadata and handler reference.
2. Support pause, resume, and cancel operations.
3. Track attempts and terminal states (`SUCCESS`, `FAILED`, `DEAD_LETTER`).
4. Support retry/backoff policy by job type.
5. Expose observability hooks (queued, running, failed, retrying counts).

### Non-functional requirements
- Deterministic behavior in tests (injectable clock where applicable).
- Bounded concurrency in `v3-optimized`.
- Safe handoff between producer and worker execution paths.
- At-least-once dispatch with idempotency boundaries.

### Constraints and assumptions
- In-memory implementation for interview scope.
- Standard-library-only implementation.
- No external queue/broker required for core versions.
- Job payload handling is abstracted; scheduler manages references and status.

## Core entities
| Entity | Responsibility |
|---|---|
| `Job` / `JobDefinition` | Scheduling metadata and handler identity |
| `JobRun` | Attempt-level execution record |
| `Trigger` / `Schedule` | Next-run computation |
| `WorkerPool` | Concurrent dispatch and execution |
| `RetryPolicy` | Delay and retry termination rules |
| `DeadLetterQueue` | Terminal sink for poison jobs |

## Concurrency expectations
- Queue saturation behavior must be explicit (block, reject, or timeout).
- Worker handoff should preserve ordering guarantees that design claims.
- State transitions must be validated to avoid illegal backward moves.

## Scoring rubric
See [RUBRIC.md](./RUBRIC.md).

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Variants and extensions
1. Priority classes with fairness quotas.
2. DAG dependencies with per-node retry policies.
3. Multi-tenant rate caps for scheduler throughput.
4. Lease-based distributed scheduler ownership.

## Version roadmap
| Version | Scope |
|---|---|
| `v1-basic` | Basic in-memory scheduler loop |
| `v2-extended` | Retry policy, trigger variants, richer metrics |
| `v3-optimized` | Concurrent workers, recovery helpers, bounded coordination |

## Cross-links
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
- [State pattern](../../01-design-patterns/behavioral/state/)
- [Strategy pattern](../../01-design-patterns/behavioral/strategy/)
- [HLD Job Scheduler](../../04-hld-projects/job-scheduler/)
