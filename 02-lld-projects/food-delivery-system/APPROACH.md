# Approach to Food Delivery System Design

## 1. Core Entities

*   **User (Customer, RestaurantOwner, Driver)**: Represents the actors in the system.
*   **Restaurant**: Represents an eatery. Contains a Menu and is managed by a RestaurantOwner.
*   **MenuItem**: An item available to order from a restaurant.
*   **Menu**: A collection of MenuItems for a Restaurant.
*   **Order**: The central entity representing a customer's request. Contains OrderItems, belongs to a Customer, is fulfilled by a Restaurant, and delivered by a Driver.
*   **OrderItem**: Represents a specific quantity of a MenuItem in an Order.
*   **Cart (optional but helpful)**: Holds items before placing an Order.

## 2. Key Relationships

*   A `Restaurant` has one `Menu`.
*   A `Menu` has many `MenuItem`s.
*   An `Order` belongs to one `Customer`.
*   An `Order` is prepared by one `Restaurant`.
*   An `Order` is delivered by one (or zero, if unassigned) `Driver`.
*   An `Order` contains many `OrderItem`s.

## 3. Design Patterns Applied

### a. State Pattern
**Problem**: An `Order` goes through numerous states (Placed, Accepted, Preparing, ReadyForPickup, OutForDelivery, Delivered). The behavior of the order (like cancellation rules, or who can update it) changes based on its state.
**Solution**: Implement the State Pattern. Create an `OrderState` interface with methods like `cancel()`, `nextState()`. Concrete classes (`PlacedState`, `PreparingState`, etc.) implement these methods. This avoids massive `if/else` or `switch` statements in the `Order` class.

### b. Observer Pattern
**Problem**: When an `Order` changes state, we need to notify the `Customer`, `Restaurant`, and potentially `Driver`.
**Solution**: The `Order` acts as the `Subject` (Observable). `Customer`, `RestaurantOwner`, and `Driver` (or a dedicated `NotificationService`) act as `Observer`s. When the `Order` state updates, it calls `notifyObservers()`.

### c. Strategy Pattern
**Problem**: Pricing can be complex. Delivery fees might vary by distance, surge pricing might apply during peak hours, and discounts/coupons could alter the final cost.
**Solution**: Use the Strategy Pattern for pricing. Define a `PricingStrategy` interface (e.g., `calculateTotal(Order)`). Implementations could include `StandardPricingStrategy`, `SurgePricingStrategy`, or `DiscountPricingStrategy`.

### d. Factory Pattern
**Problem**: We have different types of users (Customer, Driver, Owner) and potentially different types of Notifications (SMS, Push, Email).
**Solution**: Use a `UserFactory` or `NotificationFactory` to abstract the creation logic, ensuring the creation process is decoupled from the business logic.

## 4. Concurrency & Synchronization
*   Multiple drivers might try to accept the same order simultaneously. This can be handled in code using synchronized blocks/methods or concurrent data structures (like `ConcurrentHashMap` for storing available orders), ensuring atomic state updates (e.g., changing from `ReadyForPickup` to `OutForDelivery` assigned to Driver A).

## 5. Summary of Flow
1. Customer browses Restaurants and adds MenuItems to Cart.
2. Customer checks out, creating an Order.
3. Order is in `Placed` state. Observers (Restaurant) are notified.
4. Restaurant accepts Order -> `Accepted` state -> `Preparing` state.
5. Restaurant finishes -> `ReadyForPickup` state. Observers (Drivers) notified.
6. Driver accepts delivery.
7. Driver picks up -> `OutForDelivery` state.
8. Driver delivers -> `Delivered` state.
