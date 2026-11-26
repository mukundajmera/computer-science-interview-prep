# Online Shopping Cart

## Problem Statement

Design an online shopping cart system that handles product management, cart operations, pricing with discounts/coupons, and checkout processing.

---

## Functional Requirements

1. **Product Catalog**: Browse and search products by category, name, or price
2. **Cart Management**: Add, remove, and update product quantities in cart
3. **Inventory Check**: Verify product availability before adding to cart
4. **Price Calculation**: Calculate subtotal, apply discounts, taxes, and shipping
5. **Coupon System**: Apply promotional codes for discounts
6. **Checkout Process**: Convert cart to order with payment processing
7. **Multiple Carts**: Support multiple saved carts per user
8. **Wishlist**: Move items between cart and wishlist

---

## Non-Functional Requirements

1. **Concurrency**: Handle multiple users updating carts simultaneously
2. **Consistency**: Ensure inventory accuracy during checkout
3. **Performance**: Fast cart operations and price calculations
4. **Scalability**: Support large product catalogs and user base
5. **Reliability**: Handle abandoned carts and session recovery

---

## Constraints & Assumptions

- Products have unique SKUs
- Prices are in a single currency (USD)
- Coupons have validity periods and usage limits
- Tax rates vary by region
- Shipping costs depend on weight and destination
- Inventory is reserved during checkout (with timeout)

---

## Sample Interactions

```
1. User browses Electronics category
2. User adds "Laptop" ($999.99) x 1 to cart
3. User adds "Mouse" ($29.99) x 2 to cart
4. Cart displays:
   - Laptop x1: $999.99
   - Mouse x2: $59.98
   - Subtotal: $1,059.97
5. User applies coupon "SAVE10" (10% off)
   - Discount: -$105.99
   - Subtotal after discount: $953.98
6. User proceeds to checkout
   - Tax (8%): $76.32
   - Shipping: $9.99
   - Total: $1,040.29
7. User completes payment
8. Order confirmed, inventory updated
```

---

## Clarifying Questions to Ask

1. "How should coupons be validated and applied?"
2. "Can multiple coupons be stacked?"
3. "What happens when a product goes out of stock while in cart?"
4. "How long should items be reserved in cart?"
5. "Should we support guest checkout?"
6. "How are shipping costs calculated?"
7. "What payment methods should be supported?"
8. "Should we track cart abandonment?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| Product | Product information and pricing |
| Category | Product categorization |
| Cart | User's shopping cart |
| CartItem | Product in cart with quantity |
| Coupon | Discount code and rules |
| PricingEngine | Calculate totals with discounts |
| Inventory | Track product availability |
| Order | Completed purchase |

---

## Checkout Flow

```
         ┌─────────────┐
         │   Browse    │
         │  Products   │
         └──────┬──────┘
                │
                ▼
         ┌─────────────┐
         │  Add to     │
         │   Cart      │
         └──────┬──────┘
                │
                ▼
         ┌─────────────┐
         │  View Cart  │
         │ (Edit/Remove)│
         └──────┬──────┘
                │
                ▼
         ┌─────────────┐
         │  Apply      │
         │  Coupons    │
         └──────┬──────┘
                │
                ▼
         ┌─────────────┐
         │  Checkout   │
         │ (Reserve)   │
         └──────┬──────┘
                │
         ┌──────┴──────┐
         │             │
    Payment OK   Payment Fail
         │             │
         ▼             ▼
  ┌─────────────┐ ┌─────────────┐
  │  Complete   │ │  Release    │
  │   Order     │ │  Reserved   │
  └─────────────┘ └─────────────┘
```

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Products, cart, add/remove, total calculation |
| v2-extended | Coupons, discounts, taxes, shipping, multiple carts |
| v3-optimized | Thread-safe cart updates, inventory reservation, abandoned cart |
