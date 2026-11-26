# Payment System - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies intent creation, confirmation, refund, callback, and reconciliation scope |
| Domain model quality | 20% | Separates payment intent, immutable transaction records, gateway adapter, and reconciliation records |
| State and idempotency correctness | 25% | Enforces legal status transitions and idempotency keys centrally |
| Gateway reliability | 25% | Handles retries, duplicate/out-of-order callbacks, unknown outcomes, and recovery checkpoints explicitly |
| Extensibility and communication | 15% | Explains v1 to v3 evolution through policy hooks, concurrency, and reconciliation without adding live network dependencies |

## Performance bands
- `1/5`: direct gateway call wrapper with mutable status and no idempotency model.
- `3/5`: working payment flow with basic retries but weak callback ordering and reconciliation story.
- `5/5`: state-safe orchestration with immutable audit records, deterministic gateway boundaries, and clear recovery tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [HLD Payment System](../../04-hld-projects/payment-system/)
