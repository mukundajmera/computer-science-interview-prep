# Design: Food Delivery Platform

## Class Diagram

```mermaid
classDiagram
    class User {
        -String id
        -Location location
    }

    class Restaurant {
        -String id
        -Location location
        -Menu menu
    }

    class Menu {
        -List~MenuItem~ items
    }

    class MenuItem {
        -String id
        -String name
        -double price
    }

    class Cart {
        -List~MenuItem~ items
        -double total
        +addItem()
        +checkout()
    }

    class Order {
        -String id
        -OrderState state
        -User user
        -Restaurant restaurant
        -Driver driver
        -double finalPrice
        +transitionState()
    }

    class Driver {
        -String id
        -Location location
        -boolean available
    }

    class OrderState {
        <<enumeration>>
        RESERVED
        PAYMENT_PROCESSED
        ACCEPTED
        PREPARING
        DISPATCHED
        OUT_FOR_DELIVERY
        DELIVERED
        CANCELLED
    }

    class DispatchStrategy {
        <<interface>>
        +dispatch(Order order, List~Driver~ drivers)
    }

    class PricingStrategy {
        <<interface>>
        +calculatePrice(Order order, Context context)
    }

    Order "1" *-- "1" OrderState
    Restaurant "1" *-- "1" Menu
    Cart "1" *-- "*" MenuItem
```

## Core Components

1.  **Cart & Menu**: Manage the selection of items.
2.  **Order Manager**: Coordinates the creation and state transitions of orders.
3.  **Dispatch Engine**: Evaluates available drivers and assigns the optimal one using a `DispatchStrategy`.
4.  **Pricing Engine**: Calculates the final cost, applying a `PricingStrategy` (e.g., base fee + distance fee + surge multiplier).
