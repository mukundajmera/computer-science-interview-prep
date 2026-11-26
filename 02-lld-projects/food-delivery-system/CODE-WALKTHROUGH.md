# Code Walkthrough: Food Delivery System

This document explains the core implementation components for the Food Delivery System, focusing on the usage of design patterns.

## 1. Entities and Users

The system uses a straightforward OOP model for users. `User` is the base class, and `Customer`, `RestaurantOwner`, and `Driver` inherit from it. 
Restaurants contain a `Menu`, which is composed of `MenuItem`s. These are simple POJOs/Data Classes.

## 2. The Order and State Pattern

The `Order` class is the central orchestrator. Instead of having a large `switch(this.state)` inside `Order`, we delegate behavior to an `OrderState` object.

```java
public interface OrderState {
    void nextState(Order order);
    void cancel(Order order);
}
```

When an order is created, it initializes in the `PlacedState`.

```java
public class PlacedState implements OrderState {
    @Override
    public void nextState(Order order) {
        order.setState(new PreparingState());
        order.notifyObservers();
    }
    
    @Override
    public void cancel(Order order) {
        order.setState(new CancelledState());
        order.notifyObservers();
    }
}
```

If a user tries to cancel an order that is already in `OutForDeliveryState`, the `cancel()` method in `OutForDeliveryState` can throw an exception or return a message indicating cancellation is no longer possible.

## 3. The Observer Pattern for Notifications

The `Order` implements a Subject/Observable interface.

```java
public class Order {
    private List<Observer> observers = new ArrayList<>();
    
    public void addObserver(Observer o) {
        observers.add(o);
    }
    
    public void notifyObservers() {
        for(Observer o : observers) {
            o.update(this);
        }
    }
}
```

`Customer`, `RestaurantOwner`, and `Driver` (or dedicated notification services) implement `Observer`. Whenever `order.setState()` is called, `order.notifyObservers()` is triggered, pushing real-time updates to all interested parties.

## 4. The Strategy Pattern for Pricing

Calculating the total cost can vary. We inject a `PricingStrategy` into the `Order` or `CheckoutService`.

```java
public interface PricingStrategy {
    double calculateTotal(List<OrderItem> items);
}

public class StandardPricingStrategy implements PricingStrategy {
    public double calculateTotal(List<OrderItem> items) {
        double total = items.stream().mapToDouble(i -> i.getMenuItem().getPrice() * i.getQuantity()).sum();
        return total + 5.0; // Flat delivery fee
    }
}

public class SurgePricingStrategy implements PricingStrategy {
    public double calculateTotal(List<OrderItem> items) {
        double total = items.stream().mapToDouble(i -> i.getMenuItem().getPrice() * i.getQuantity()).sum();
        return total + 15.0; // High surge fee
    }
}
```

At checkout, the system determines the current context (e.g., weather, time of day) and assigns the appropriate `PricingStrategy` to calculate the final price.

## 5. Thread Safety and Concurrency

In a real implementation, accepting an order by a driver must be atomic. 

```java
public synchronized boolean assignDriver(Order order, Driver driver) {
    if (order.getDriver() == null && order.getState() instanceof ReadyForPickupState) {
        order.setDriver(driver);
        return true;
    }
    return false;
}
```
Alternatively, using concurrent data structures or database transactions with optimistic locking (e.g., checking a version number when updating the driver ID) is necessary in a distributed environment.
