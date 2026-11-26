# Common Pitfalls: Food Delivery System LLD

When designing a Food Delivery System in an interview setting, candidates often fall into several traps. 

## 1. The `switch(state)` Anti-Pattern
The most common mistake is managing the Order lifecycle using a giant `switch` or `if/else` block inside the `Order` class.
*   **Why it's bad**: It violates the Open/Closed Principle. Adding a new state (e.g., `DelayedState`) requires modifying the core `Order` class. It also makes the code difficult to read and test.
*   **The Fix**: Use the **State Pattern**.

## 2. Tight Coupling for Notifications
Hardcoding notifications inside the `Order` class methods.
```java
// Anti-pattern
public void setReady() {
    this.state = "READY";
    customer.sendSms("Food is ready!");
    driver.sendPush("Pick up food!");
}
```
*   **Why it's bad**: The `Order` class now knows about SMS APIs, Push Notification APIs, and specific user preferences. It violates the Single Responsibility Principle.
*   **The Fix**: Use the **Observer Pattern**. Let the `Order` just say "my state changed" and let registered listeners handle the actual communication.

## 3. Ignoring Concurrency on Driver Assignment
Assuming that finding an available order and assigning a driver happens in a vacuum.
*   **Why it's bad**: In a real system, multiple drivers might see the same "Ready for Pickup" order and tap "Accept" simultaneously. If the system doesn't handle concurrency, two drivers might be assigned to the same order.
*   **The Fix**: Discuss atomic operations, database constraints (Optimistic Locking/Version columns), or `synchronized` blocks (if keeping the scope strictly in-memory LLD).

## 4. Poor Abstraction of Pricing
Hardcoding delivery fees or tax calculations into the checkout flow.
*   **Why it's bad**: Pricing logic changes frequently (surge pricing, coupons, distance-based fees). Hardcoding it makes the system inflexible.
*   **The Fix**: Use the **Strategy Pattern** to abstract pricing calculations.

## 5. Merging Cart and Order
Using the same entity for a user's shopping cart and the final placed order.
*   **Why it's bad**: A cart is highly mutable; users add and remove things constantly. An order is an immutable snapshot of intent at checkout. Merging them leads to complex validation logic.
*   **The Fix**: Keep `Cart` and `Order` as distinct entities.

## 6. Over-engineering Live Location Tracking
Spending 30 minutes designing a real-time WebSockets/Kafka pipeline for GPS pings.
*   **Why it's bad**: This is a High-Level Design (HLD) concern. In an LLD interview, focus on the domain model, interfaces, and state transitions.
*   **The Fix**: Abstract location updates behind a simple `updateLocation(Location l)` method or treat it as an external service out of scope.
