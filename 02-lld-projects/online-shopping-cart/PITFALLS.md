# Online Shopping Cart - Common Pitfalls

## Common pitfalls
1. Treating cart totals as stored truth instead of deriving them from cart items and pricing rules.
2. Ignoring price changes between add-to-cart and checkout despite the price snapshot design.
3. Deducting inventory when an item is added to cart instead of reserving during checkout.
4. Applying coupons without validity periods, usage limits, minimums, or stacking rules.
5. Losing reserved stock when payment fails, checkout times out, or a cart is abandoned.

## Why these fail interviews
- They make totals, discounts, and order amounts hard to audit.
- They either oversell inventory or hold stock while users browse.
- They under-specify rollback behavior across cart, inventory, payment, and order creation.

## Mitigations
- Keep `CartItem` responsible for quantity and price-at-add, and use a pricing engine for totals.
- Define when current product price overrides or compares against the cart snapshot.
- Reserve inventory during checkout with timeout and release paths.
- Validate coupons through explicit strategy/factory rules before applying discounts.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Design patterns](../../01-design-patterns/README.md)
