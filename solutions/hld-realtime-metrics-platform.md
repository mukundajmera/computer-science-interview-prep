# 🏆 Coach Answer: Real-Time Metrics Platform — HLD

> **Type:** High-Level Design
> **Difficulty:** Advanced
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional
1. Ingest high-volume metric points.
2. Serve low-latency dashboard queries.
3. Evaluate alert rules continuously.
4. Support retention/downsampling tiers.

### Non-Functional
| Metric | Target |
|---|---|
| Availability | 99.95% |
| Ingest p99 | < 2s |
| Query p95 | < 300ms |
| Peak throughput | 3M points/sec |

---

## Phase 2 — Estimation (5 min)

- Steady ingest: 1M points/sec -> 86.4B/day.
- Peak ingest: 3M points/sec.
- Conclusion: hot/cold data split is mandatory; pure relational design is insufficient.

---

## Phase 3 — API + Data Model (10 min)

```http
POST /api/v1/metrics/ingest
GET /api/v1/metrics/query?metric=...&from=...&to=...&step=...
POST /api/v1/alerts
```

Series identity:
`series_id = hash(metric_name + sorted_tags + tenant_id)`

Storage choices:
- Kafka (buffer/replay)
- Flink (rollups + alert eval)
- Hot TSDB (recent reads)
- Object storage/rollups (historical)
- PostgreSQL (control plane)

---

## Phase 4 — Architecture (15 min)

```text
Agents -> Gateway -> Ingest -> Kafka -> Flink -> Rollups/Alerts
                         \-> Hot TSDB -> Query Service -> Dashboards
Cold path: rollups/raw export -> Object storage -> historical queries
```

### Critical design callouts
- Per-tenant quotas + cardinality policy at ingest.
- Event-time windows and late-data policy.
- Debounce to reduce alert flapping.

---

## Phase 5 — Deep Dives (7 min)

### 1) Cardinality control
- Deny dangerous tags and enforce tenant budgets.

### 2) Late event correctness
- Watermark + allowed lateness; side-output very-late data.

### 3) Retention economics
- Raw short window, medium rollups, long coarse rollups.

---

## Phase 6 — Trade-offs + Wrap-up (3 min)

| Decision | Chosen | Alternative | Why |
|---|---|---|---|
| Compute | Flink streaming | Batch-only | Needed for real-time alerts |
| Hot storage | TSDB | PostgreSQL-only | Better ingest/time-window performance |
| Retention | tiered rollups | full raw | sustainable cost |

Close statement:
"This design prioritizes real-time operational correctness while containing storage cost through rollups and strict cardinality governance."

---

## YouTube Top-K Variant Notes

- Add top-K query endpoints for all-time and tumbling windows.
- Define late-event policy and replay window flow.
- Prefer precomputed per-window rankings over request-time global scans.
