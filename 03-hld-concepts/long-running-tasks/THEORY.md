# Long-Running Tasks

Long-running tasks split request acceptance from heavy execution so user APIs remain fast while expensive work executes asynchronously.

## What is it?

API servers validate and enqueue work, return a job ID immediately, and worker pools process jobs from queues with retries, status tracking, and failure isolation.

## Why do we need it?

- Many operations exceed normal HTTP timeout budgets.
- Mixing short API calls and heavy processing hurts tail latency.
- Background work needs independent scaling and failure recovery.

## Core strategy progression

1. Introduce queue + worker pool with job status store.
2. Add retries, DLQ, and idempotency keys.
3. Add backpressure and queue-depth-based autoscaling.
4. Split mixed workloads by queue class.
5. Add workflow orchestration for multi-step dependencies.

## Requirements and constraints

- Max synchronous response time target for accept path.
- Job completion SLOs and retry budget.
- Idempotency scope for duplicate submissions.
- Backpressure thresholds and admission policy.
- Observability: queue depth, lag, failure, retry, DLQ growth.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|---|---|---|
| Decomposition | Fast accept + async execution separation | Keeps heavy work in request thread |
| Reliability | Retry/DLQ/idempotency defined | Infinite retries / duplicate side effects |
| Capacity control | Backpressure + autoscaling triggers | No queue-depth policy |
| Operability | Status API + metrics + failure drill-down | No visibility into backlog/failures |

## Common pitfalls

- Dual-write race between DB state and queue publish.
- No idempotency key on user-triggered tasks.
- Single queue for tiny and massive jobs (head-of-line blocking).
- No DLQ or retry cap for poison jobs.
- Accepting unlimited work during overload.

## Follow-up questions

1. How do you prevent duplicate job side effects?
2. What happens when workers crash mid-job?
3. When does a job move to dead letter?
4. How do you protect the system during 10x bursts?
5. When do you need orchestration instead of simple chaining?

## Variants and extensions

- **Simple async jobs:** queue + worker + status table.
- **Latency-sensitive jobs:** priority queues and dedicated worker pools.
- **Long workflows:** orchestrator/state machine with per-step retries.
- **Strict correctness:** transactional outbox for durable enqueue semantics.

## 📊 Diagrams

- [Submit, poll, and worker lifecycle](./diagrams/submit-poll-worker-lifecycle.mmd) - the accept-execute split: the API validates and enqueues the job and returns a job ID immediately, workers update the status store with capped retries, and the client polls for status and result.

## Related concepts

- [Caching](../caching/THEORY.md)
- [Database Replication](../database-replication/THEORY.md)
- [Database Sharding](../database-sharding/THEORY.md)
- [Message Queues](../message-queues/THEORY.md)
- [CDN](../cdn/THEORY.md)

## Related projects

- [Video Streaming](../../04-hld-projects/video-streaming/)
- [File Storage](../../04-hld-projects/file-storage/)
- [News Feed](../../04-hld-projects/news-feed/)
