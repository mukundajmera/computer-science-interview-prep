# Online Shopping Cart - Follow-Up Questions

## Follow-up questions
1. What happens if product price changes after an item was added to the cart?
2. How would you reserve inventory during checkout without holding stock for abandoned carts?
3. How would you support multiple coupons while keeping discount rules understandable?
4. What should happen if payment succeeds but order creation or inventory deduction fails?
5. How would you make cart updates thread-safe for the same user session?

## Variants and extensions
1. Saved carts, wishlists, and guest checkout conversion.
2. Buy-X-get-Y, category-specific, and max-discount coupon strategies.
3. Shipping calculators based on weight and destination.
4. Event history for cart abandonment and order audit.

## Interviewer probes to prepare
- "When is inventory reserved versus deducted?"
- "What amount is charged if the product price changes?"
- "Where do coupon usage limits become atomic?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
