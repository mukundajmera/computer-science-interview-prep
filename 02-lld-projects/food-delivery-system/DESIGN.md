# Food Delivery System Design

## Class Diagram

Below is the class diagram illustrating the core entities and the application of Strategy, State, and Observer patterns.

```mermaid
classDiagram
    %% Core Entities & Users
    class User {
        <<abstract>>
        -String id
        -String name
        -String contactInfo
        +getId()
        +getName()
    }

    class Customer {
        -Address deliveryAddress
        +update(Order)
    }

    class RestaurantOwner {
        -Restaurant restaurant
        +update(Order)
    }

    class Driver {
        -Location currentLocation
        -boolean isAvailable
        +update(Order)
    }

    User <|-- Customer
    User <|-- RestaurantOwner
    User <|-- Driver

    %% Restaurant & Menu
    class Restaurant {
        -String id
        -String name
        -Menu menu
        +getMenu()
    }

    class Menu {
        -List~MenuItem~ items
        +addItem(MenuItem)
        +removeItem(MenuItem)
    }

    class MenuItem {
        -String id
        -String name
        -double price
        -String description
        +getPrice()
    }

    Restaurant --> Menu
    Menu *-- MenuItem

    %% Order & Cart
    class OrderItem {
        -MenuItem menuItem
        -int quantity
        +getCost()
    }

    class Order {
        -String id
        -Customer customer
        -Restaurant restaurant
        -Driver driver
        -List~OrderItem~ items
        -OrderState state
        -PricingStrategy pricingStrategy
        -List~Observer~ observers
        +addObserver(Observer)
        +notifyObservers()
        +setState(OrderState)
        +calculateTotal() double
    }

    Order *-- OrderItem
    Order --> Customer
    Order --> Restaurant
    Order --> Driver

    %% Observer Pattern
    class Observer {
        <<interface>>
        +update(Order)
    }
    Observer <|.. Customer
    Observer <|.. RestaurantOwner
    Observer <|.. Driver
    Order --> Observer : notifies

    %% State Pattern
    class OrderState {
        <<interface>>
        +nextState(Order)
        +cancel(Order)
        +getStatus() String
    }

    class PlacedState {
        +nextState(Order)
        +cancel(Order)
    }
    class PreparingState {
        +nextState(Order)
        +cancel(Order)
    }
    class ReadyForPickupState {
        +nextState(Order)
        +cancel(Order)
    }
    class OutForDeliveryState {
        +nextState(Order)
        +cancel(Order)
    }
    class DeliveredState {
        +nextState(Order)
        +cancel(Order)
    }

    OrderState <|.. PlacedState
    OrderState <|.. PreparingState
    OrderState <|.. ReadyForPickupState
    OrderState <|.. OutForDeliveryState
    OrderState <|.. DeliveredState
    Order --> OrderState : uses

    %% Strategy Pattern
    class PricingStrategy {
        <<interface>>
        +calculateTotal(List~OrderItem~) double
    }

    class StandardPricingStrategy {
        +calculateTotal(List~OrderItem~) double
    }

    class SurgePricingStrategy {
        +calculateTotal(List~OrderItem~) double
    }

    PricingStrategy <|.. StandardPricingStrategy
    PricingStrategy <|.. SurgePricingStrategy
    Order --> PricingStrategy : uses
```

## State Diagram

This state diagram shows the lifecycle of an `Order`.

```mermaid
stateDiagram
    [*] --> Placed : Customer places order
    Placed --> Preparing : Restaurant accepts
    Placed --> Cancelled : Restaurant rejects / Customer cancels
    Preparing --> ReadyForPickup : Restaurant finishes food
    ReadyForPickup --> OutForDelivery : Driver picks up
    OutForDelivery --> Delivered : Driver delivers to Customer
    Delivered --> [*]
    Cancelled --> [*]
```
