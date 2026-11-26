# Real-Time Metrics Platform

## Positioning

This project is the **advanced sibling** of [Metrics Monitoring](../metrics-monitoring/). Use this version when interview constraints require higher ingest rates, stricter real-time behavior, and richer stream-processing controls.

## Problem Statement

Design a real-time metrics platform that ingests high-volume telemetry, powers low-latency dashboards, and supports continuous alerting with retention tiers.

## Requirements and constraints

### Functional requirements
1. Ingest high-volume metric points (`name`, labels, timestamp, value).
2. Query recent and historical windows with aggregation support.
3. Evaluate alert rules continuously with bounded delay.
4. Enforce tenant quotas and cardinality controls.

### Non-functional requirements

| Requirement | Target |
|---|---|
| Availability | 99.95% |
| Ingest latency | p99 < 2s |
| Query latency | p95 < 300ms (hot window) |
| Throughput | 1M points/sec steady, 3M peak |
| Durability | No committed data loss |

## Variant guidance
- Choose **Metrics Monitoring** for interview-baseline observability design.
- Choose **Real-Time Metrics Platform** when pushed on stream semantics, replay, and aggressive scale.

## YouTube Top-K Variant
- Variant prompt: maintain a rolling top-K videos list over configurable windows (e.g., 5m, 1h, 24h).
- Key extension: combine event-time windowing with late-arrival handling and deterministic tie-breaking.
- Interview focus: exact-vs-approximate ranking, hot-key skew mitigation, and window state recovery after failures.
