# Design Approach for Job Scheduler

## Approach overview
Design around clear scheduling boundaries: trigger calculation, queue admission, worker execution, and state transition management. Keep each boundary testable in isolation.

## Step 1: Model execution lifecycle
1. Define legal state transitions for job and run attempts.
2. Separate schedule computation from execution side effects.
3. Treat idempotency keys as part of handler contract.

## Step 2: Introduce bounded coordination
- Use a bounded queue abstraction for producer-consumer handoff.
- Define queue backpressure policy explicitly.
- Keep worker pool size configurable and observable.

## Step 3: Add retry and failure isolation
- Keep retry policy pluggable.
- Move poison jobs to dead-letter sink after retry budget exhaustion.
- Capture attempt metadata for post-failure debugging.

## Step 4: Optimize v3 paths
- Synchronize shared counters/state transitions.
- Keep lock scope narrow around mutable run state.
- Add recovery checkpoints for restart continuity.

## Step 5: Progressive versions
- `v1-basic`: deterministic single-process scheduling loop.
- `v2-extended`: trigger/retry abstractions and metrics.
- `v3-optimized`: bounded concurrency, lease/recovery helpers.

## Requirements and constraints checklist
- Bounded handoff under load.
- Retry storms prevented via capped backoff.
- Illegal state transitions rejected.
- Java/Python parity for queue/retry semantics.

## Scoring rubric
See [RUBRIC.md](./RUBRIC.md).

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Variants and extensions
1. Priority-aware bounded queues.
2. Delayed queue partitions by tenant.
3. Separate control plane for schedule edits.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Rate Limiter approach](../rate-limiter/APPROACH.md)
- [Movie Ticket Booking pitfalls](../movie-ticket-booking/PITFALLS.md)
