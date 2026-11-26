# Design Approach for Real-Time Metrics Platform

## Interview flow
1. Clarify SLA split: dashboard freshness vs alert correctness.
2. Quantify ingest pressure and cardinality budget.
3. Define ingestion, query, and alert contracts.
4. Walk stream architecture with replay and lateness handling.
5. Close with tiered retention and tenant-isolation trade-offs.

## Baseline vs advanced decision
- Start from [Metrics Monitoring](../metrics-monitoring/) baseline.
- Add advanced controls only when scale/latency constraints require them:
  - event-time semantics + allowed lateness
  - stream replay and compensation paths
  - stronger tenant controls and cardinality governance
