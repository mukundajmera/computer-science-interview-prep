# Real-Time Metrics Platform - Strong Answer

## 0-5 min: Requirements

Say: "I will design a multi-tenant metrics platform where ingestion is durable, dashboards are fast, and alert evaluation is repeatable."

- Support high-volume metric writes, label validation, low-latency recent dashboards, rollup history, alert rules, and tenant isolation.
- Non-goals: logs, traces, and arbitrary SQL analytics unless the interviewer expands scope.
- Correctness boundary: no acknowledged data loss; duplicates are tolerated and deduplicated.

## 5-10 min: Scale and Constraints

Say: "The platform should acknowledge after durable queue append, not after every downstream storage write."

- Target p99 ingest acknowledgement under 2 seconds after durable append.
- Target p95 dashboard latency under 300 ms for recent common aggregations.
- Raw point visibility can lag processing, but alert windows must be deterministic and replayable.

## 10-20 min: API and Data Model

Say: "Tenant and label cardinality controls are part of the API contract, not an afterthought."

- `POST /api/v1/metrics:write` accepts tenant id, series labels, timestamp, value, and idempotency metadata.
- `GET /api/v1/query` supports metric, time range, step, aggregation, and group-by labels.
- Alert API stores rule expression, evaluation interval, hold duration, notification policy, and replay policy.
- Core records: `series_registry`, `raw_point_chunk`, `rollup_chunk`, `alert_rule`, `alert_state`, `tenant_quota`, and `correction_event`.

## 20-35 min: Architecture

Say: "Ingest, stream processing, hot storage, rollups, and alert evaluation are separate so one slow tier does not take down the platform."

- Gateway authenticates tenants, enforces quotas, validates labels, and appends to a durable queue partitioned by tenant and series.
- Stream processors deduplicate, update event-time windows, and write hot compressed chunks plus rollups.
- Query service fans out to hot TSDB and rollup store, with bounded partial responses only for dashboards.
- Alert evaluators use the same aggregation definitions as dashboards but do not depend on dashboard cache results.

## 35-42 min: Deep Dives

Say: "Silent failure is the real risk: dropped labels, partial rollups, stale dashboards, and delayed alerts must be visible."

- Cardinality control: reject or throttle high-cardinality label explosions before they become platform-wide outages.
- Late data: write correction records for rollups and bound alert re-evaluation by rule policy.
- TSDB failure: processors pause commits, retry, spill to DLQ after bounded retries, and replay missing chunks.
- Tenant isolation: quota budgets, shard placement, and noisy-tenant throttles prevent one tenant from starving others.

## 42-45 min: Wrap-up

Say: "I chose durable queue acknowledgement, hot-plus-rollup storage, and explicit correction records because this gives recoverability without making dashboards slow."

- Trade-off: precomputed rollups increase write amplification, but they cap query latency and make alert replay deterministic.
- Next evolution: adaptive rollup selection, tenant-specific retention tiers, and query cost estimation before execution.
