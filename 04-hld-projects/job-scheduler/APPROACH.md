# Design Approach for Job Scheduler

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify requirements | 6 min | Job types (one-time/cron/DAG), correctness target, tenant model |
| Capacity estimation | 6 min | Jobs/min, retries, queue depth, worker concurrency |
| API + state model | 10 min | Submit/pause/resume/cancel and run-state transitions |
| Architecture | 13 min | Scheduler, dispatcher, worker pools, lease/recovery path |
| Deep dives | 7 min | Duplicate prevention, fairness, dead-letter policy |
| Wrap-up | 3 min | Evolution to multi-region orchestration |

## Suggested execution order
1. Lock execution semantics and retry boundaries.
2. Define job/run entities and transition guards.
3. Design dispatch + worker ownership using leases.
4. Add fairness and backpressure controls.
5. Close with recovery and observability plan.
