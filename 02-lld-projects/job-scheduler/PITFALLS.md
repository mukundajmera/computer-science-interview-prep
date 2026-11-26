# Job Scheduler - Common Pitfalls

## Common pitfalls
1. Combining schedule computation and execution side effects in one method.
2. Allowing illegal transitions such as `SUCCESS -> RUNNING`.
3. Unbounded queue growth under producer bursts.
4. Retry policies without a cap, backoff boundary, or dead-letter terminal state.
5. Using wall clock directly in tests, creating flaky trigger and retry behavior.

## Why these fail interviews
- They hide correctness risks that appear under load.
- They make failure behavior impossible to reason about.
- They weaken confidence in deterministic tests and production-readiness.

## Mitigations
- Centralize transition validation in one state manager.
- Use a bounded queue and explicit admission policy.
- Keep trigger, retry/backoff, worker, and dead-letter behavior behind separate abstractions.
- Capture attempt metadata before deciding retry or DLQ handoff.
- Inject a clock/time source for deterministic tests.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
