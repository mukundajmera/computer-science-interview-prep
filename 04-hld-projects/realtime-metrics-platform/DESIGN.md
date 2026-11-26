# Real-Time Metrics Platform - Advanced Design

## 1. Requirements and Constraints

### Problem statement
Design a multi-tenant real-time metrics platform that ingests high-volume telemetry points, serves low-latency dashboards, evaluates alert rules continuously, and retains downsampled history for long-term analysis.

This is the advanced version of [Metrics Monitoring](../metrics-monitoring/): the main interview differentiators are event-time correctness, bounded late-data handling, cardinality governance, replay-safe aggregation, and alert evaluation under stream failures.

### Functional requirements
- Ingest counters, gauges, histograms, and distribution samples with tenant identity, metric name, labels, event timestamp, and idempotency key.
- Query recent windows with low latency and historical windows through rollups.
- Continuously evaluate alert rules over event-time windows.
- Enforce tenant quotas, per-metric cardinality budgets, label allow/deny rules, and burst controls.
- Support replay, backfill, and late-arrival compensation without double-counting committed points.

### Non-functional requirements

| Requirement | Target |
|---|---|
| Availability | 99.95% for ingest, query, and alert control plane |
| Ingest throughput | 1M points/sec steady, 3M points/sec peak |
| Ingest acknowledgement latency | p99 < 2s after durable queue append |
| Dashboard latency | p95 < 300ms for last 1h and common aggregations |
| Alert evaluation delay | p95 < 60s after watermark closes the evaluation window |
| Durability | No acknowledged data loss; duplicate writes are tolerated and deduplicated |
| Retention | 7d raw hot, 30d 1m rollups, 13mo 5m/1h rollups |

### Out of scope
- Full trace/log search.
- Arbitrary SQL over raw telemetry.
- Exact global analytics over unbounded labels.
- Notification provider internals beyond alert dispatch handoff.

## 2. Capacity and Latency Assumptions

### Traffic and storage

| Metric | Assumption | Design impact |
|---|---:|---|
| Active tenants | 20k | Quotas and partitions include tenant isolation |
| Peak ingest | 3M points/sec | Requires durable queue, horizontal validation, stream aggregation |
| Average point envelope | 180 bytes compressed after protocol overhead | About 540 MB/sec peak before replication |
| Raw hot data | 3M/sec * 180 bytes * 7d | About 326 TB logical before compression, replication, and index overhead |
| Hot query fan-out budget | <= 64 shards per query | Requires shard routing by tenant, metric, and time bucket |
| Cardinality budget | default 2M active series per large tenant, lower for small tenants | Reject or quarantine high-cardinality label sets before they hit TSDB |

### Latency budget

| Stage | Target |
|---|---:|
| Agent to gateway | p95 < 100ms inside region |
| Validation and quota check | p95 < 40ms |
| Queue append acknowledgement | p99 < 2s |
| Stream processor lag | p95 < 15s under normal load |
| Hot TSDB write visibility | p95 < 10s after processing |
| Query service execution | p95 < 250ms service time for hot windows |
| Alert notification handoff | p95 < 60s after event-time window closes |

Key design choice: acknowledge ingestion after durable queue append, not after TSDB materialization. Dashboards may show a small freshness lag, while durability is protected by queue replay.

## 3. API / System Interface

### Ingest API

```http
POST /api/v1/metrics:write
Authorization: Bearer <tenant-token>
Content-Type: application/json
Idempotency-Key: <batch-id>

{
  "tenant_id": "t_123",
  "source_id": "host-a/us-east-1",
  "points": [
    {
      "metric": "checkout.latency_ms",
      "type": "histogram",
      "event_time": "2026-06-14T10:15:30.123Z",
      "value": {"buckets": [[50, 12], [100, 30]], "sum": 2680, "count": 42},
      "labels": {
        "service": "checkout",
        "region": "us-east-1",
        "status": "success"
      },
      "point_id": "01JZ4P5N3K9C8"
    }
  ]
}
```

Response:

```http
202 Accepted
{
  "accepted": 982,
  "rejected": 18,
  "batch_id": "gw-01/000927",
  "watermark_hint": "2026-06-14T10:15:00Z",
  "errors": [
    {"index": 7, "code": "CARDINALITY_LIMIT", "label": "user_id"}
  ]
}
```

Contract details:
- `point_id` or `(tenant_id, source_id, metric, labels_hash, event_time, value_hash)` is used for idempotent deduplication.
- Batches are capped at 10k points or 2 MB compressed.
- Timestamps older than 24h are accepted only through the backfill API.
- Unknown labels may be sampled, dropped, or rejected based on tenant policy.

### Query API

```http
GET /api/v1/query?tenant_id=t_123&metric=checkout.latency_ms&from=2026-06-14T10:00:00Z&to=2026-06-14T11:00:00Z&step=30s&agg=p95&group_by=region,status
```

Response:

```json
{
  "resolution": "30s",
  "freshness_lag_seconds": 12,
  "series": [
    {
      "labels": {"region": "us-east-1", "status": "success"},
      "points": [["2026-06-14T10:00:00Z", 82.4]]
    }
  ],
  "partial": false
}
```

Query limits:
- Hot queries over raw data are limited to 1h by default.
- Wider windows are routed to 1m, 5m, or 1h rollups.
- Queries with unbounded `group_by` are rejected with `422 QUERY_TOO_EXPENSIVE`.
- Query results include `partial=true` if a shard is degraded and stale cached data is returned.

### Alert API

```http
POST /api/v1/alerts/rules
{
  "tenant_id": "t_123",
  "name": "checkout-p95-latency",
  "expression": "p95(checkout.latency_ms{service='checkout'}) > 250",
  "window": "5m",
  "evaluation_interval": "30s",
  "for": "2m",
  "severity": "page",
  "labels": {"team": "payments"},
  "notification_policy_id": "np_critical"
}
```

```http
GET /api/v1/alerts/rules/{rule_id}/state
PATCH /api/v1/alerts/rules/{rule_id}
POST /api/v1/backfills
GET /api/v1/tenants/{tenant_id}/cardinality
```

Alert contract:
- Rules evaluate over event-time windows, not gateway receive time.
- `for` suppresses transient breaches until consecutive windows remain breaching.
- Late-data correction may emit a `corrected` state transition, but notifications are deduplicated by `(rule_id, window_start, severity)`.
- Rule updates are versioned; evaluators pin a rule version for each window.

### Error model
- `400` invalid payload or unsupported metric type.
- `401/403` invalid tenant token or unauthorized metric namespace.
- `409` idempotency-key conflict with different payload hash.
- `422` query or label set exceeds tenant limits.
- `429` tenant, source, or global ingestion throttle.
- `503` dependency unavailable; clients retry with exponential backoff and the same idempotency key.

## 4. Core Entities and Data Model

### Entity model

| Entity | Key fields | Purpose |
|---|---|---|
| `tenant` | `tenant_id`, plan, ingest quota, active-series limit | Isolation and fairness |
| `metric_descriptor` | `tenant_id`, `metric_name`, type, unit, allowed labels | Schema and governance |
| `series` | `series_id`, `tenant_id`, `metric_name`, canonical labels, `labels_hash` | Stable identity for one time series |
| `raw_point_chunk` | `tenant_id`, `series_id`, `bucket_start`, encoded samples | Hot raw reads and replay verification |
| `rollup_chunk` | `tenant_id`, `series_id`, `resolution`, `window_start`, aggregates | Fast historical reads |
| `alert_rule` | `rule_id`, `tenant_id`, expression, version, window, threshold | Alert definition |
| `alert_state` | `rule_id`, `window_start`, state, last_evaluated_watermark | Idempotent alert transitions |
| `ingest_dedup` | `tenant_id`, `idempotency_key` or `point_id`, payload hash, expiry | Duplicate suppression |

### Storage layout

| Store | Data | Primary key / partitioning | Indexes | Retention |
|---|---|---|---|---|
| Durable queue | Validated ingest events | topic partition by `hash(tenant_id, metric_name)`, ordered per series shard | offset index by partition | 72h standard, 7d during incidents |
| Hot TSDB | Raw and recent rollup chunks | `(tenant_id, metric_name_hash, time_bucket, shard)` | `series_id -> chunk`, label inverted index bounded per tenant | 7d raw, 30d 1m |
| Warm/cold object store | Compacted rollups and backfill files | `tenant_id/resolution/yyyy/mm/dd/hour` | manifest by tenant, metric, resolution, time range | 13mo or tenant policy |
| Metadata DB | tenants, metric descriptors, rules | `tenant_id` partition; `rule_id` global unique | `tenant_id + metric_name`, `tenant_id + rule_name` | indefinite with audit history |
| Dedup store | recent batch/point ids | `(tenant_id, idempotency_key)` | TTL index | 48h for normal ingest, 30d for backfill jobs |
| Alert state store | evaluation state and notifications | `(tenant_id, rule_id, window_start, rule_version)` | `tenant_id + state + severity` | 90d state, 13mo audit |

### Keys, indexes, and partitioning
- `series_id = hash(tenant_id, metric_name, canonical_sorted_labels)`; canonicalization removes label-order ambiguity.
- Queue partitions use `hash(tenant_id, metric_name, series_id % virtual_shards)` so one tenant cannot monopolize a global partition.
- Hot TSDB partitions by `(tenant_id, time_bucket)` first, then series shard, because most dashboard queries are tenant-scoped and time-bounded.
- Label inverted indexes are budgeted: high-cardinality labels like `request_id`, `trace_id`, and `user_id` are blocked unless configured as exemplars outside the metrics index.
- Rollup chunks are append-plus-compaction; late updates write correction records and compact into canonical chunks asynchronously.

## 5. High-Level Architecture

Mermaid source: [architecture.mmd](./diagrams/architecture.mmd).

```text
Agents/SDKs
   -> Regional Ingest Gateway
   -> Validator + Quota + Cardinality Guard
   -> Durable Queue
   -> Stream Processor
        -> Hot TSDB Writer
        -> Rollup Pipeline
        -> Alert Evaluator
   -> Cold Rollup Export

Query Clients -> Query Service -> Hot TSDB / Rollup Store / Metadata DB
Alerts       -> Notification Router -> Pager, Email, Webhook
```

### Component responsibilities
- **Ingest Gateway:** authenticates tenants, enforces batch limits, normalizes payloads, assigns receive time, and returns 202 after durable append.
- **Validator/Quota/Cardinality Guard:** checks metric descriptors, label policies, active-series budget, tenant rate limits, and payload idempotency.
- **Durable Queue:** absorbs spikes, preserves replayable input, and isolates ingest acknowledgement from downstream stores.
- **Stream Processor:** performs event-time windowing, deduplication, aggregation, rollup emission, and late-data correction.
- **Hot TSDB Writer:** writes compressed chunks and label indexes for recent dashboard reads.
- **Query Service:** plans queries across hot, warm, and cold stores; applies downsampling selection; protects stores with query budgets.
- **Alert Evaluator:** evaluates versioned alert rules over closed event-time windows and sends idempotent state transitions.
- **Control Plane:** manages tenants, descriptors, quotas, alert rules, rollout flags, and audit records.

## 6. Write, Read, Failure, and Recovery Paths

### Ingest write path
1. Agent sends a compressed batch with tenant token and idempotency key.
2. Gateway authenticates and rejects oversized batches before doing expensive work.
3. Validator canonicalizes labels, checks metric type, applies tenant quotas, and consults cardinality budgets.
4. Accepted points are appended to the durable queue; the gateway returns `202 Accepted`.
5. Stream processors consume by partition, deduplicate, update event-time windows, and write raw chunks plus rollups.
6. Alert evaluators consume the same window outputs so alerts and dashboards share aggregation semantics.

### Query read path
1. Query Service validates tenant authorization and parses the query into metric, filter, group-by, time range, and aggregation.
2. Planner chooses raw hot chunks for short fresh windows, 1m rollups for recent wider windows, and 5m/1h rollups for historical ranges.
3. Planner uses the metadata index to resolve bounded `series_id` sets; unbounded cardinality queries are rejected early.
4. Workers fan out to the selected shards, merge partial aggregates, and return freshness metadata.
5. If a hot shard is slow, the service can return stale cached results with `partial=true` for dashboard queries; alert evaluation does not use partial reads.

### Alert evaluation path
1. Alert rules are compiled into query plans and assigned to evaluator shards by `hash(tenant_id, rule_id)`.
2. Evaluators wait for the watermark to close a window, then evaluate the pinned rule version.
3. State transitions are written with compare-and-set on `(rule_id, window_start, rule_version)`.
4. Notification Router deduplicates by `(rule_id, incident_key, severity)` and applies cooldown/suppression policies.
5. Late corrections can reopen recent windows inside the allowed-lateness bound and update alert state with an audit trail.

### Failure and recovery path
- **Gateway failure:** clients retry with the same idempotency key; stateless gateways can be replaced behind the load balancer.
- **Queue partition unavailable:** gateway returns `503` or throttles affected tenants; no acknowledgement is returned before durable append.
- **Processor crash:** replacement consumers resume from committed offsets and rebuild in-memory window state from checkpoint plus queue replay.
- **Hot TSDB write failure:** stream processors pause commits, retry with backoff, and spill window output to a DLQ after bounded retries; replay restores missing chunks.
- **Cardinality incident:** guard switches tenant to quarantine mode, rejects new series, and continues accepting existing series.
- **Regional outage:** agents fail over to another region if tenant policy allows it; duplicate cross-region batches are deduped by idempotency key.
- **Bad rule rollout:** rule versions can be disabled immediately; evaluators stop scheduling new windows while preserving historical state.

## 7. Deep Dives

### Deep dive A: event-time windows and late data
Metrics arrive out of order because agents buffer locally, networks retry, and backfills replay old data. Processing by receive time would make dashboards fresh but alerts incorrect; processing by event time gives deterministic windows but requires a lateness policy.

Design:
- Maintain per-partition watermarks from observed event times and source heartbeat progress.
- Close normal windows after `max_observed_event_time - allowed_lateness`; default allowed lateness is 2 minutes for realtime ingest.
- Accept late points up to 24h for normal ingest, but mark points later than the alert correction window as dashboard-only corrections.
- Write correction records for already-emitted rollups rather than mutating chunks in place synchronously.
- Surface `freshness_lag_seconds`, `watermark`, and `partial` in query responses so dashboards can explain staleness.

Trade-off: wider lateness improves correctness but delays alerts. The default favors alert timeliness while still allowing bounded correction and auditability.

### Deep dive B: cardinality budgets and series governance
The main operational failure mode is unbounded labels. A single tenant adding `user_id` or `request_id` to a hot metric can create millions of active series and overload queue partitions, label indexes, memory state, and query fan-out.

Controls:
- Require metric descriptors for high-volume namespaces, including type and allowed labels.
- Maintain active-series counters per `(tenant_id, metric_name, label_name)` over rolling windows.
- Reject dangerous labels at ingest with clear `CARDINALITY_LIMIT` errors before writing to the queue.
- Allow tenant-specific emergency modes: sample new series, drop only the offending label, or quarantine the metric namespace.
- Provide `/api/v1/tenants/{tenant_id}/cardinality` so teams can see top exploding metrics and labels.

Trade-off: strict write-time enforcement can drop data during deploy mistakes, but it prevents a tenant-local mistake from becoming a platform-wide outage.

### Deep dive C: rollups and alert evaluation correctness
Dashboards need fast reads, while alerts need repeatable semantics. Both should use the same aggregation definitions, but alerting cannot depend on best-effort dashboard cache reads.

Design:
- Stream processors compute canonical window aggregates for fixed resolutions: 10s, 1m, 5m, and 1h.
- Query Service chooses the lowest-cost resolution that still respects the requested step and aggregation.
- Alert Evaluator consumes canonical window outputs, not arbitrary query results.
- Each alert evaluation stores input watermark, rule version, aggregate version, and notification dedup key.
- Backfills run as explicit jobs that write to a separate correction topic; alert re-evaluation is bounded by rule policy.

Trade-off: precomputed rollups increase write amplification, but they cap dashboard query latency and make alert replay deterministic.

## 8. Observability, Rollout, and Rollback

### Observability
- Ingest: accepted/rejected points, validation errors by code, tenant throttles, queue append latency, queue lag.
- Cardinality: active series by tenant/metric, new-series rate, rejected labels, top cardinality contributors.
- Processing: watermark lag, processor checkpoint age, window state size, replay rate, DLQ volume.
- Query: p50/p95/p99 latency by window size, shard fan-out, partial responses, cache hit ratio, rejected expensive queries.
- Alerts: evaluation delay, state transitions, notification dedupe count, flapping rules, correction events.
- Storage: chunk write latency, compaction lag, rollup completeness, cold export failures, retention deletion lag.

### Rollout
1. Mirror ingest from a small tenant set into the new queue and processors without serving reads.
2. Compare rollups and alert states against the baseline metrics platform for selected metrics.
3. Enable dashboard reads for internal tenants using feature flags and fallback to baseline query path.
4. Enable alert evaluation in shadow mode, then notify-only for low-severity rules, then page-level rules.
5. Gradually raise tenant cardinality enforcement from observe-only to warn to reject.

### Rollback and containment
- Gateway feature flag can route tenants back to the baseline metrics monitoring path.
- Query Service can pin tenants to old rollups while new processors continue shadow computation.
- Alert rules keep previous versions, so a bad rule compiler or evaluator rollout can revert without losing state history.
- Queue retention preserves replay input long enough to rebuild hot chunks after processor or TSDB incidents.
- Quota and cardinality changes are control-plane versioned and can be rolled back per tenant.

What could fail silently: dropped labels, partial rollups, delayed alert windows, and stale dashboards. Each must emit tenant-visible diagnostics and platform SLO alerts.

## 9. Trade-offs and Decisions

| Decision | Chosen | Alternative | Why chosen now | Revisit trigger |
|---|---|---|---|---|
| Ingest acknowledgement | After durable queue append | After TSDB write | Protects durability and absorbs TSDB lag | Users require read-after-write visibility under 2s |
| Time semantics | Event-time windows with bounded lateness | Receive-time windows | Correct alerts and deterministic replay | Alert SLA becomes stricter than lateness bound |
| Storage | Hot TSDB + rollup object store | One large TSDB tier | Balances p95 dashboard latency and retention cost | Historical queries need ad hoc raw scans |
| Cardinality control | Write-time budget enforcement | Post-hoc cleanup | Prevents runaway tenant impact | False positives block critical metrics too often |
| Alert path | Dedicated evaluator over canonical windows | Query service executes alerts | Isolates alerts from dashboard spikes | Rule volume is too low to justify separate service |
| Backfill | Explicit backfill jobs and correction topic | Normal ingest path only | Avoids old data destabilizing realtime watermarks | Backfills become rare and low volume |

## 10. Migration Path from Baseline Monitoring

1. Introduce durable ingest queue behind the existing ingest API.
2. Add metric descriptors, idempotency keys, and cardinality observe-only reporting.
3. Split hot raw storage from rollup storage while preserving existing query responses.
4. Move dashboards to Query Service with fallback to baseline metrics monitoring.
5. Run Alert Evaluator in shadow mode and compare incident states.
6. Enable event-time alerts, late-data corrections, and tenant-level fairness controls.
7. Enforce cardinality budgets and retire unsupported high-cardinality query patterns.

## 11. Follow-up Questions

1. What changes at 10x ingest volume?
2. How do you support multi-region active-active ingestion without double-counting?
3. What is the contract for alert corrections after a late backfill?
4. How do you protect the platform from a tenant deploying a bad label?
5. When would you move from exact rollups to approximate sketches?
6. How do you prove dashboards and alerts use the same aggregation semantics?

## 12. Strong Answer Closing

For a time-boxed interview close, use the narrative in [STRONG-ANSWER.md](./STRONG-ANSWER.md): start from baseline monitoring, justify stream semantics, explain replay-safe aggregation and alert correctness under lateness, then close with migration and cost trade-offs.

Final 60-90 second summary:
1. The platform accepts high-volume tenant metrics through a durable, quota-protected ingest path.
2. Stream processors compute event-time raw chunks, rollups, and alert windows from the same replayable source.
3. Query Service uses hot TSDB data for fresh dashboards and rollups for historical windows.
4. The hardest risks are late data, cardinality explosions, and alert correctness; the design contains them with watermarks, budgets, idempotency, correction records, and versioned alert state.

---
**Real-world reference**: See how Google Spanner solved this in the [Google Spanner case study](../../case-studies/google-spanner-truetime/)
