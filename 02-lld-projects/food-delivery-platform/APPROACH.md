# Approach: Food Delivery Platform

## 1. Requirement Analysis

A food delivery platform coordinates three main actors: Users (Eaters), Restaurants, and Drivers. The critical paths are:
-   **Browsing & Cart**: Building an order.
-   **Order Processing**: Managing the state of the order accurately.
-   **Fulfillment**: Finding the right driver and managing the delivery.
-   **Pricing**: Adapting to real-time market conditions.

## 2. Design Patterns

-   **State Pattern**: To manage the order's lifecycle (CREATED, ACCEPTED, PREPARING, OUT_FOR_DELIVERY, DELIVERED).
-   **Strategy Pattern**: For implementing different dynamic pricing algorithms and driver dispatch strategies (e.g., Nearest Driver, Highest Rated).
-   **Observer Pattern**: To notify users and drivers of order state changes.
-   **Singleton**: For centralized managers like the `OrderManager` or `DriverManager`.

## 3. Data Models

-   **User**: Represents a customer.
-   **Restaurant**: Has a location and a Menu.
-   **MenuItem**: An item on the menu with a price.
-   **Cart**: Holds MenuItems for a User before checkout.
-   **Order**: The central entity, containing items, total price, state, customer, restaurant, and assigned driver.
-   **Driver**: Represents a delivery partner, with a current location and availability status.

## 4. Evolution

-   **v1 (Basic)**: Implement the core entities. Simple cart checkout and basic order state transitions (reservation, payment, restaurant acceptance, courier dispatch). Ensure duplicate requests and failure release inventory/payment/courier at most once.
-   **v2 (Extended)**: Add spatial awareness. Implement a `DriverManager` that tracks driver locations and dispatches the closest available driver. Ensure one courier with barrier-start competing orders accepts at most one active assignment.
-   **v3 (Optimized)**: Introduce `PricingStrategy` to calculate surge prices based on simulated demand. Refine the state machine to be robust against invalid transitions, especially in a concurrent environment. Ensure cancel/late acceptance and unavailable stock preserve exact order totals.