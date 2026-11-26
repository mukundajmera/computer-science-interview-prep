# Metrics Monitoring — Comparison Notes

| System | Similarity | Key difference |
|---|---|---|
| Realtime Metrics Platform | stream + aggregation pattern | metrics-first schema and alert semantics |
| Notification Service | async delivery and retries | channel delivery vs data analytics focus |
| Workflow Orchestration | multi-step reliability concerns | orchestration depth vs data processing depth |

## Migration and reuse
- Reuse queue + idempotency + DLQ patterns.
- Reuse alerting/monitoring controls for operations.
- Isolate control-plane and data-plane concerns early.
