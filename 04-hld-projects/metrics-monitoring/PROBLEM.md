# Metrics Monitoring

## Problem Statement

Design a monitoring platform that ingests metrics, serves dashboards, and evaluates threshold alerts with bounded latency.

---

## Requirements and constraints

### Functional requirements
1. Ingest counters, gauges, and histogram samples from agents/SDKs with tenant, metric name, labels, timestamp, and value.
2. Query time-series dashboards with aggregation, downsampling, and label filters.
3. Evaluate alert rules with threshold, multi-window burn-rate, and dedup/suppression behavior.
4. Enforce tenant quotas and label-cardinality controls before runaway series creation damages storage/query latency.
5. Expose operator views for ingest lag, dropped labels, rule-evaluation lag, noisy alerts, rollup lag, and partial-query status.

### Non-functional requirements

| Requirement | Target |
|---|---|
| Availability | 99.95% |
| Ingestion throughput | 5M samples/s peak |
| Query latency | p95 < 2 seconds for common 24-hour dashboard windows |
| Alert evaluation delay | < 30 seconds for hot rules |
| Retention | 30 days hot, 180 days warm, 1 year cold rollups |
| Cardinality | tenant- and metric-specific series budgets |

### Constraints
- Metrics are append-heavy and tolerate bounded late data, but alerts must be clear about evaluation windows and duplicate notification suppression.
- Label cardinality is a first-class product constraint, not an afterthought.
- Reads may return partial results during rollup lag or shard failure, but must surface freshness/partial indicators.
- Keep logs/traces and full observability-suite correlation as extensions.

### Out of scope
- Log search, distributed tracing, incident-management workflows, and on-call scheduling.
- Arbitrary query-language compatibility beyond the selected interview API.
- Organization-specific compliance implementation details.

## API / system interface


```http
POST /api/v1/metrics/write
GET  /api/v1/query?expr=...&from=...&to=...
POST /api/v1/alerts/rules
GET  /api/v1/tenants/{tenant_id}/cardinality
GET  /api/v1/operators/rollup-lag?tenant_id=...
```

## Key design challenges

1. Preventing unbounded label cardinality from creating too many series.
2. Serving fast dashboard queries across hot, warm, and cold retention tiers.
3. Evaluating alerts reliably when samples arrive late or rollup jobs lag.
4. Communicating partial data and freshness without silently misleading operators.

## Related links
- [HLD Design Template](../DESIGN-TEMPLATE.md)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/THEORY.md)
- [Write Scaling](../../03-hld-concepts/write-scaling/THEORY.md)
