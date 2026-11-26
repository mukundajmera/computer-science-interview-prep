# Design Approach for Online Shopping Cart

## Step 1: Identify Core Entities

From the problem statement, we identify these core entities (nouns):

| Noun | Entity? | Responsibility |
|------|---------|---------------|
| Product | Yes | Store product information, pricing |
| Category | Yes | Group related products |
| Cart | Yes | Hold items for a user |
| CartItem | Yes | Product + quantity in cart |
| Coupon | Yes | Discount rules and validation |
| Inventory | Yes | Track stock levels |
| User | Yes | Cart owner |
| Order | Yes | Completed purchase |
| Payment | Yes | Payment transaction |
| PricingEngine | Yes | Calculate prices with rules |

## Step 2: Define Relationships

```
User (1) ──────────────── (N) Cart
                              │
Cart (1) ──────────────── (N) CartItem ──── (1) Product
                              │
Product (N) ───────────── (1) Category
                              │
Inventory (1) ──────────── (1) Product
                              │
Cart ─────── uses ─────── PricingEngine
                              │
PricingEngine ─── applies ─── Coupon
                              │
Cart ─────── converts to ──── Order
```

## Step 3: Choose Design Patterns

### 1. Composite Pattern (Product Catalog)
- **Why**: Products can be individual items or bundles
- **Application**: `ProductComponent` interface with `LeafProduct` and `ProductBundle`

### 2. Decorator Pattern (Discounts/Taxes)
- **Why**: Apply multiple modifiers to prices dynamically
- **Application**: `PriceModifier` decorators for discounts, taxes, shipping

### 3. Strategy Pattern (Pricing Rules)
- **Why**: Different discount calculation strategies
- **Application**: `DiscountStrategy` for percentage, fixed amount, buy-X-get-Y

### 4. Observer Pattern (Price Updates)
- **Why**: Notify cart when product prices change
- **Application**: `PriceObserver` to update cart totals

### 5. Factory Pattern (Coupon Creation)
- **Why**: Create different coupon types with validation
- **Application**: `CouponFactory` for various discount types

## Step 4: Design Classes

### Product
**Responsibilities**: Store product information
**Attributes**: id, name, description, price, category, weight
**Methods**: getPrice(), isAvailable()

### Category
**Responsibilities**: Organize products
**Attributes**: id, name, parentCategory
**Methods**: getProducts(), getSubcategories()

### Cart
**Responsibilities**: Manage user's shopping items
**Attributes**: id, userId, items, createdAt, updatedAt
**Methods**: addItem(), removeItem(), updateQuantity(), clear(), getTotal()

### CartItem
**Responsibilities**: Link product to cart with quantity
**Attributes**: product, quantity, addedAt
**Methods**: getSubtotal(), updateQuantity()

### Inventory
**Responsibilities**: Track product stock
**Attributes**: productStock map
**Methods**: checkStock(), reserve(), release(), deduct()

### Coupon
**Responsibilities**: Define discount rules
**Attributes**: code, discountType, value, minAmount, expiresAt, usageLimit
**Methods**: isValid(), apply(), getDiscount()

### PricingEngine
**Responsibilities**: Calculate final price
**Attributes**: taxRate, shippingCalculator, discountStrategies
**Methods**: calculateSubtotal(), applyDiscount(), calculateTax(), calculateTotal()

### Order
**Responsibilities**: Record completed purchase
**Attributes**: id, userId, items, total, status, createdAt
**Methods**: confirm(), cancel(), getStatus()

## Step 5: Handle Edge Cases

1. **Empty cart checkout**: Validate cart has items
2. **Insufficient stock**: Check before adding and at checkout
3. **Expired coupons**: Validate coupon dates
4. **Concurrent cart updates**: Use locks for thread safety
5. **Invalid quantities**: Validate positive integers
6. **Price changes**: Handle price updates between add and checkout
7. **Coupon stacking**: Define rules for multiple coupons
8. **Abandoned carts**: Release reserved inventory

## Step 6: Optimization Opportunities

1. **Cart caching**: Cache cart state for fast retrieval
2. **Lazy price calculation**: Only recalculate when cart changes
3. **Inventory batching**: Batch inventory operations
4. **Read-write locks**: Allow concurrent reads, exclusive writes
5. **Event sourcing**: Track all cart events for analytics
