# Online Shopping Cart - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies catalog, cart operations, coupons, tax, shipping, inventory reservation, checkout, and abandonment |
| Cart and pricing model | 25% | Separates cart items, price snapshots, coupons, pricing engine, tax, shipping, and order totals |
| Inventory and checkout correctness | 25% | Checks stock, reserves during checkout, releases on failure/timeout, and deducts only after payment success |
| Extensibility boundaries | 20% | Uses strategy/factory/decorator-style seams for discounts, coupons, product bundles, and price modifiers |
| Concurrency and communication | 15% | Explains cart locking, atomic inventory operations, coupon usage limits, and order creation tradeoffs |

## Performance bands
- `1/5`: cart as a product list with totals recalculated by scattered conditionals.
- `3/5`: working cart, coupon, and checkout flow with basic inventory validation.
- `5/5`: transaction-aware checkout with price snapshot, pricing engine boundaries, inventory reservation, rollback paths, and concurrency tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Inventory Management rubric](../inventory-management/RUBRIC.md)
