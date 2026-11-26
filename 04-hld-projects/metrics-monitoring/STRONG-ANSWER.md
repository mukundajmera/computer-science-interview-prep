# Metrics Monitoring — Strong Answer Outline (Time-Boxed)

## 0-5 min: Requirements
- Clarify supported metric types: counters, gauges, histograms, labels, timestamps, dashboards, and alert rules.
- State the main risk early: uncontrolled label cardinality can make ingestion, storage, and queries fail even if raw sample volume is acceptable.
- Defer logs, traces, and incident-management workflow unless asked.

Say: "The hardest part is not only ingesting samples; it is controlling series cardinality so writes, storage, queries, and alerts stay predictable."

## 5-10 min: Estimation
- Use 5M samples/s to justify write sharding, compressed chunks, and rollup jobs.
- Estimate daily sample volume and retention tiers, then explain why hot/warm/cold storage and downsampling are necessary.

## 10-20 min: API + data model
- Present write, query, alert-rule, and cardinality-inspection APIs.
- Model `series_id`, `sample_chunk`, `rollup_chunk`, and `alert_rule`.
- Describe label indexes, tenant quota checks, and alert evaluation state.

## 20-35 min: Architecture
- Walk ingestion through gateway validation, cardinality guard, TSDB writer, hot store, rollup jobs, and cold retention.
- Walk query planning across raw chunks and rollups with freshness/partial-result metadata.
- Walk alert evaluation as a separate path so dashboard query spikes do not break alert SLA.

## 35-42 min: Deep dives
- Deep dive cardinality budgets, label dropping, and user-facing diagnostics.
- Explain late sample handling and alert replay after evaluator failover.
- Discuss alert deduplication and multi-window burn-rate to reduce noise.

## 42-45 min: Wrap-up
- Restate tiered TSDB storage, cardinality enforcement at write time, rollups, dedicated alert evaluator, and explicit freshness/partial markers.
- Mention the advanced follow-up: graduate to [Realtime Metrics Platform](../realtime-metrics-platform/) for stricter event-time semantics and replay-heavy processing.

Say: "I would enforce label policy on the write path, use rollups for long ranges, and keep alert evaluation separate from dashboard queries so operational alerts do not depend on ad hoc query traffic."
