# Vending Machine - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies payment methods, denominations, exact-change behavior, refunds, and admin scope |
| State modeling | 25% | Uses explicit states to prevent invalid dispense, selection, and cancellation flows |
| Transaction correctness | 25% | Preserves money/product consistency across payment, selection, dispense, change, and refund |
| Inventory and change handling | 20% | Checks stock and change availability before committing irreversible steps |
| Extensibility and communication | 15% | Explains payment strategy, admin operations, and v3 concurrency without overbuilding v1 |

## Performance bands
- `1/5`: procedural flow with scattered conditionals and unclear rollback behavior.
- `3/5`: working state machine with basic inventory and change handling.
- `5/5`: transaction-safe state design with explicit failure paths, refund handling, and extensible payment/change policies.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Parking Lot rubric](../parking-lot/RUBRIC.md)
