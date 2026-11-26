# Strong Answer: Online Shopping Cart

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Online Shopping Cart, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

**Explicit Clarifications:**
- "How should coupons be validated and applied?" (Stacking logic configurable via Validator).
- "What happens when a product goes out of stock while in cart?" (Temporary hold reservations across multiple warehouses).
- "How are taxes and shipping calculated?" (Handled dynamically during checkout).

## 2. Entity Modeling & APIs (10 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."
**Entities:** `Cart`, `CartItem`, `Product`, `Coupon`, `InventoryManager`, `InventoryHold`, and `PricingEngine`. 

**Core APIs:**
- `createCart(userId) -> Cart`
- `addToCart(cartId, productId, quantity) -> boolean`
- `applyCoupon(cartId, couponCode) -> boolean`
- `checkout(cartId) -> PriceSummary`

## 3. Data Structure Rationale & Design Alternatives (10 mins)
**Say:** "Choosing the right data structures is critical for meeting our latency and throughput requirements."
A `ConcurrentHashMap` links a `CartID` to their active `Cart`. Within the cart, a `ConcurrentHashMap` manages `CartItem`s for fast lookups. The `CopyOnWriteArrayList` is used for applied coupons and hold IDs since reads outnumber writes. 

**Design Alternative:** An RDBMS could persist carts for durability, but writing on every `addToCart` would increase latency. In a real system, Redis offers a better trade-off: durability across app server restarts with low latency.

## 4. Correctness & Complexity (5 mins)
**Say:** "Let's evaluate the complexity of operations."
- `addToCart`: O(W) where W is the number of warehouses to scan for available inventory.
- `checkout`: O(N) where N is the number of unique items to commit holds and calculate `PriceSummary`.
- **Correctness:** The design explicitly validates stock reservation *before* returning success to `addToCart`. Empty or invalid input checks are handled gracefully, returning explicit errors.

## 5. Concurrency Defense & Failure Handling (10 mins)
**Say:** "Given that this system will be accessed by multiple threads concurrently, ensuring thread safety without creating bottlenecks is a priority."
The `InventoryManager` safely tracks active stock using a `ConcurrentHashMap` of `Warehouse`s and `InventoryHold`s. 
- **Failure Rollback:** If a cart update fails (e.g. attempting to request 5 items but only 3 exist across all warehouses), the system gracefully releases all newly created `InventoryHold`s for that request to prevent partial locks. 
- **Expiration:** Holds have a TTL (e.g., 15 minutes) and are cleaned up dynamically to prevent zombie reservations blocking other users.
