# Restaurant Management - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies table capacity, reservation time slots, waitlist, menu availability, taxes, tips, split bills, and inventory scope |
| State and workflow modeling | 25% | Uses explicit order states from placed through completed and prevents invalid kitchen, serving, billing, and payment transitions |
| Reservation and table correctness | 25% | Avoids double-booking tables for the same time, matches party size to capacity, and releases tables after billing and cleaning |
| Kitchen and billing correctness | 20% | Checks menu/item availability, supports controlled order modifications, sends orders to the kitchen queue, and calculates bills accurately |
| Extensibility and communication | 15% | Explains v1 to v3 progression through reservations, split bills, kitchen queue, waitlist, inventory, and concurrent reservations |

## Performance bands
- `1/5`: table and order CRUD with no time-slot reservation or order-state control.
- `3/5`: working order and billing flow with basic reservations and kitchen handoff.
- `5/5`: workflow-safe design with table conflict checks, kitchen state transitions, split billing, waitlist handling, and concurrency tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
