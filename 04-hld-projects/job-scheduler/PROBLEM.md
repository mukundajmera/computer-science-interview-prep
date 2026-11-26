# Job Scheduler

## Problem Statement

Design a scheduler that supports one-time and recurring jobs, near-time execution guarantees, retries, and operational visibility.

---

## Requirements and constraints

### Functional requirements
1. Create one-time, recurring, and dependency-triggered jobs with timezone-aware schedules and optional tenant quotas.
2. Pause, resume, cancel, and manually rerun jobs without losing run history.
3. Dispatch due jobs to workers with bounded trigger delay and duplicate-safe execution semantics.
4. Retry failed runs with jittered backoff, max attempts, and dead-letter routing.
5. Expose job/run history, lease state, dispatch lag, retry backlog, and tenant fairness diagnostics.

### Non-functional requirements

| Requirement | Target |
|---|---|
| Availability | 99.95% |
| Scheduled volume | 30M runs/day, 3x burst at common boundaries |
| Trigger delay | p95 < 3 seconds from scheduled time to dispatch |
| Dispatch throughput | 100K jobs/minute peak including retries |
| History retention | 30 days hot, longer cold audit as needed |
| Execution semantics | at-least-once dispatch with idempotent run keys |

### Constraints
- Exactly-once side effects are not guaranteed by the scheduler; handlers must accept idempotency/run keys.
- The scheduler owns lease correctness, retry timing, tenant fairness, and audit history.
- Recurring schedules must be explicit about timezone, daylight-saving behavior, and missed-run policy.
- Keep arbitrary workflow orchestration and human approvals as extensions, not the baseline answer.

### Out of scope
- Long-running workflow engines, manual approval flows, and task business logic.
- Worker implementation internals beyond the scheduler/handler adapter contract.
- Organization-specific compliance implementation details.

## API / system interface


```http
POST /api/v1/jobs
POST /api/v1/jobs/{job_id}/pause
POST /api/v1/jobs/{job_id}/resume
POST /api/v1/jobs/{job_id}/cancel
POST /api/v1/jobs/{job_id}/runs/{run_id}/retry
GET  /api/v1/jobs/{job_id}/runs?from=...&to=...
GET  /api/v1/operators/dispatch-lag?tenant_id=...
```

## Key design challenges

1. Efficiently finding due jobs without scanning every schedule on each tick.
2. Avoiding dual execution when scheduler shards or workers fail mid-run.
3. Balancing tenant fairness with high-throughput dispatch during burst windows.
4. Making retries, dead letters, and manual reruns auditable and safe.

## Related links
- [HLD Design Template](../DESIGN-TEMPLATE.md)
- [Idempotency](../../03-hld-concepts/idempotency/THEORY.md)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/THEORY.md)
- [Write Scaling](../../03-hld-concepts/write-scaling/THEORY.md)
