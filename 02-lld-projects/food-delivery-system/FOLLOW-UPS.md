# Follow-up Questions: Food Delivery System

After establishing the core Low-Level Design, interviewers often ask follow-up questions to test your ability to extend the system and handle real-world complexities.

## 1. Handling Order Cancellations
**Question:** How would you modify the system to handle order cancellations? What if the restaurant has already started preparing the food?
**Expected Approach:**
*   Leverage the State Pattern. The `cancel()` method behavior should depend on the current state.
*   If `PlacedState`, cancel immediately and refund.
*   If `PreparingState`, cancel but perhaps charge a penalty, or require manual Restaurant approval.
*   If `OutForDelivery`, cancellation might not be allowed through the app, requiring customer support intervention.

## 2. Advanced Pricing Strategies (Coupons & Discounts)
**Question:** How would you apply multiple discounts to an order (e.g., "$5 off delivery" AND "10% off the food")?
**Expected Approach:**
*   Extend the Strategy Pattern using the **Decorator Pattern**.
*   Start with a `BasePricingStrategy`. Wrap it in a `TenPercentDiscountDecorator`, then wrap that in a `FreeDeliveryDecorator`. Each layer modifies the total returned by the inner layer.

## 3. Batched Deliveries
**Question:** How would you handle a driver picking up two orders from the same restaurant going to nearby customers?
**Expected Approach:**
*   Modify the `Driver` entity to hold a `List<Order>` instead of a single `Order`.
*   Introduce a `DeliveryBatch` or `Route` entity that contains multiple orders and manages the state of the batch as a whole (e.g., verifying all items are picked up before marking the batch as OutForDelivery).

## 4. Matching Algorithm (HLD/LLD Hybrid)
**Question:** How does the system find the best driver for an order?
**Expected Approach:**
*   In LLD, abstract this behind a `DriverMatchingStrategy` interface.
*   Implementations could be `ClosestDriverStrategy` or `HighestRatedDriverStrategy`.
*   Acknowledge that in reality, this involves geospatial queries (Quadtrees/Geohashes) and is often handled by a dedicated microservice.

## 5. Idempotency in Payments
**Question:** If the customer's app loses network connection right as they click "Place Order", and they click it again, how do you prevent double-charging?
**Expected Approach:**
*   Discuss **Idempotency Keys**. The client generates a unique UUID for the checkout attempt.
*   The backend checks if an order with that Idempotency Key already exists before processing the payment and creating the order.
