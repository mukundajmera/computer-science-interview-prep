# Job Scheduler — Strong Answer Outline (Time-Boxed)

## 0-5 min: Requirements
- Clarify supported job types: one-time, recurring, dependency-triggered, pause/resume/cancel, retries, and run history.
- State the execution contract: at-least-once dispatch, idempotent run keys, bounded trigger delay, and auditable retries.
- Defer full workflow orchestration and task business logic unless the interviewer asks.

Say: "The scheduler can guarantee durable scheduling, fair dispatch, and duplicate-safe run keys. It should not promise exactly-once side effects inside arbitrary customer handlers."

## 5-10 min: Estimation
- Use 30M scheduled runs/day with 3x burst windows to justify sharded due-time scanning and dispatch queues.
- Estimate 30-day run history at roughly 1B rows, motivating event history plus materialized latest state.

## 10-20 min: API + data model
- Present create/pause/resume/cancel/retry APIs and run-history queries.
- Model `job_definition`, `job_run`, `job_run_event`, and `dead_letter`.
- Call out indexes on `next_fire_at`, `tenant_id`, `scheduled_at`, and unique run keys.

## 20-35 min: Architecture
- Walk the schedule path: API writes definition, scheduler shards claim due runs, dispatch queue feeds worker pools, handlers execute with run keys.
- Walk retry/dead-letter flow with jittered backoff, max attempts, and operator surfacing.
- Explain latest-state materialization for reads and append-only events for recovery.

## 35-42 min: Deep dives
- Deep dive lease ownership, heartbeat expiry, and duplicate-safe retry after lost acknowledgements.
- Discuss tenant fairness during burst windows.
- Cover timezone and daylight-saving policy for recurring jobs.

## 42-45 min: Wrap-up
- Restate at-least-once execution, idempotent handlers, lease-backed ownership, append-only run events, and weighted dispatch.
- Mention extensions: cross-region scheduling, workflow templates, and cost-aware scheduling.

Say: "My main trade-off is at-least-once execution plus idempotent handlers, because that is simpler and more reliable than pretending a distributed scheduler can make every downstream side effect exactly-once."
