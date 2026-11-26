# Payment System — Comparison Notes

| System | Similarity | Key difference |
|---|---|---|
| Realtime Metrics Platform | stream ingestion, aggregation, replay, alerting | metrics tolerate approximate aggregates; payments require exact state transitions and audit evidence |
| Notification Service | async delivery, retries, provider adapters, DLQs | notifications can often retry until success; payments must prevent duplicate money movement |
| Workflow Orchestration | multi-step reliability, sagas, compensating actions | payment gateways are external authorities; reconciliation evidence can override local assumptions |
| Ledger/Wallet System | immutable money movement and balances | payment orchestration talks to external providers; wallet ledgers usually own internal balance truth |

## Migration and reuse
- Reuse queue + idempotency + DLQ patterns.
- Reuse alerting/monitoring controls for operations.
- Isolate control-plane and data-plane concerns early.

## What makes payment harder

Payment interviews punish vague distributed-systems answers because correctness is business-critical. The candidate must explain where money movement is authorized, where internal events are committed, how duplicate evidence is deduped, and how provider settlement records repair local unknown states.
