# Strong Answer: Food Delivery System LLD

This document provides a comprehensive, end-to-end example of a strong answer to the Food Delivery System Low-Level Design interview question, incorporating the Strategy, Observer, State, and Factory patterns.

## 1. Requirements Gathering & Scope

**Functional Requirements:**
*   Customers can view menus, place orders, and track status.
*   Restaurants can manage menus and update order prep status.
*   Drivers can accept delivery requests and update delivery status.
*   The system must calculate total costs (including surge pricing).
*   Users must be notified of order state changes.

**Non-Functional Requirements:**
*   Thread safety for order acceptance (preventing multiple drivers from accepting the same order).
*   Extensibility for new pricing models and order states.

## 2. Core Entities and Domain Model

*   **User Hierarchy**: `User` (abstract) -> `Customer`, `RestaurantOwner`, `Driver`.
*   **Restaurant Domain**: `Restaurant` has a `Menu`, which has a list of `MenuItem`s.
*   **Order Domain**: `Order` contains `OrderItem`s. It references a `Customer`, `Restaurant`, and `Driver`.
*   **State & Strategies**: `OrderState` interface, `PricingStrategy` interface.

## 3. Java Implementation

### Step 1: Base Entities and Users

```java
public abstract class User {
    protected String id;
    protected String name;
    public User(String id, String name) { this.id = id; this.name = name; }
    public String getId() { return id; }
    public String getName() { return name; }
}

public class Customer extends User implements Observer {
    public Customer(String id, String name) { super(id, name); }
    @Override
    public void update(Order order) {
        System.out.println("Notify Customer " + name + ": Order is now " + order.getState().getStatus());
    }
}

public class Driver extends User implements Observer {
    private boolean isAvailable = true;
    public Driver(String id, String name) { super(id, name); }
    @Override
    public void update(Order order) {
        if (order.getState().getStatus().equals("READY_FOR_PICKUP")) {
            System.out.println("Notify Driver " + name + ": New order available for pickup!");
        }
    }
}

public class RestaurantOwner extends User implements Observer {
    private Restaurant restaurant;
    public RestaurantOwner(String id, String name, Restaurant restaurant) { 
        super(id, name); 
        this.restaurant = restaurant;
    }
    @Override
    public void update(Order order) {
        System.out.println("Notify Restaurant " + restaurant.getName() + ": Order update - " + order.getState().getStatus());
    }
}
```

### Step 2: The Observer Pattern (Subject)

```java
public interface Observer {
    void update(Order order);
}

public interface Subject {
    void addObserver(Observer o);
    void removeObserver(Observer o);
    void notifyObservers();
}
```

### Step 3: The State Pattern

```java
public interface OrderState {
    void nextState(Order order);
    void cancel(Order order);
    String getStatus();
}

public class PlacedState implements OrderState {
    public void nextState(Order order) {
        order.setState(new PreparingState());
        order.notifyObservers();
    }
    public void cancel(Order order) {
        order.setState(new CancelledState());
        order.notifyObservers();
    }
    public String getStatus() { return "PLACED"; }
}

public class PreparingState implements OrderState {
    public void nextState(Order order) {
        order.setState(new ReadyForPickupState());
        order.notifyObservers();
    }
    public void cancel(Order order) {
        System.out.println("Cannot cancel after preparation has started without manager approval.");
    }
    public String getStatus() { return "PREPARING"; }
}

public class ReadyForPickupState implements OrderState {
    public void nextState(Order order) {
        order.setState(new OutForDeliveryState());
        order.notifyObservers();
    }
    public void cancel(Order order) { System.out.println("Cannot cancel. Food is ready."); }
    public String getStatus() { return "READY_FOR_PICKUP"; }
}

public class OutForDeliveryState implements OrderState {
    public void nextState(Order order) {
        order.setState(new DeliveredState());
        order.notifyObservers();
    }
    public void cancel(Order order) { System.out.println("Cannot cancel. Out for delivery."); }
    public String getStatus() { return "OUT_FOR_DELIVERY"; }
}

public class DeliveredState implements OrderState {
    public void nextState(Order order) { System.out.println("Order already delivered."); }
    public void cancel(Order order) { System.out.println("Cannot cancel. Already delivered."); }
    public String getStatus() { return "DELIVERED"; }
}

public class CancelledState implements OrderState {
    public void nextState(Order order) { System.out.println("Order is cancelled."); }
    public void cancel(Order order) { System.out.println("Already cancelled."); }
    public String getStatus() { return "CANCELLED"; }
}
```

### Step 4: The Strategy Pattern (Pricing)

```java
public interface PricingStrategy {
    double calculateTotal(List<OrderItem> items);
}

public class StandardPricingStrategy implements PricingStrategy {
    public double calculateTotal(List<OrderItem> items) {
        double subtotal = items.stream().mapToDouble(i -> i.getMenuItem().getPrice() * i.getQuantity()).sum();
        return subtotal + 5.0; // $5 delivery fee
    }
}

public class SurgePricingStrategy implements PricingStrategy {
    public double calculateTotal(List<OrderItem> items) {
        double subtotal = items.stream().mapToDouble(i -> i.getMenuItem().getPrice() * i.getQuantity()).sum();
        return subtotal + 15.0; // $15 delivery fee
    }
}
```

### Step 5: Domain Entities (Menu, Order)

```java
public class MenuItem {
    private String id, name;
    private double price;
    public MenuItem(String id, String name, double price) {
        this.id = id; this.name = name; this.price = price;
    }
    public double getPrice() { return price; }
}

public class OrderItem {
    private MenuItem item;
    private int quantity;
    public OrderItem(MenuItem item, int quantity) {
        this.item = item; this.quantity = quantity;
    }
    public MenuItem getMenuItem() { return item; }
    public int getQuantity() { return quantity; }
}

public class Restaurant {
    private String name;
    public Restaurant(String name) { this.name = name; }
    public String getName() { return name; }
}
```

### Step 6: The Core Order Class

```java
import java.util.ArrayList;
import java.util.List;

public class Order implements Subject {
    private String id;
    private Customer customer;
    private Restaurant restaurant;
    private Driver driver;
    private List<OrderItem> items = new ArrayList<>();
    private OrderState state;
    private PricingStrategy pricingStrategy;
    private List<Observer> observers = new ArrayList<>();

    public Order(String id, Customer customer, Restaurant restaurant, PricingStrategy strategy) {
        this.id = id;
        this.customer = customer;
        this.restaurant = restaurant;
        this.pricingStrategy = strategy;
        this.state = new PlacedState();
    }

    public void addItem(OrderItem item) { items.add(item); }
    
    public double getTotal() { return pricingStrategy.calculateTotal(items); }

    // State delegation
    public void setState(OrderState state) { this.state = state; }
    public OrderState getState() { return state; }
    public void nextState() { state.nextState(this); }
    public void cancel() { state.cancel(this); }

    // Driver assignment with basic synchronization to prevent race conditions
    public synchronized boolean assignDriver(Driver driver) {
        if (this.driver == null) {
            this.driver = driver;
            return true;
        }
        return false;
    }

    // Observer implementation
    public void addObserver(Observer o) { observers.add(o); }
    public void removeObserver(Observer o) { observers.remove(o); }
    public void notifyObservers() {
        for (Observer o : observers) {
            o.update(this);
        }
    }
}
```

## 4. Execution Example (Main Method)

```java
public class FoodDeliveryDemo {
    public static void main(String[] args) {
        // 1. Setup Data
        Restaurant res = new Restaurant("Pizza Palace");
        Customer cust = new Customer("C1", "Alice");
        RestaurantOwner owner = new RestaurantOwner("O1", "Bob", res);
        Driver driver = new Driver("D1", "Charlie");

        MenuItem pizza = new MenuItem("M1", "Pepperoni Pizza", 15.0);
        
        // 2. Create Order
        Order order = new Order("ORD-1", cust, res, new StandardPricingStrategy());
        order.addItem(new OrderItem(pizza, 2));

        System.out.println("Total Cost: $" + order.getTotal());

        // 3. Register Observers
        order.addObserver(cust);
        order.addObserver(owner);
        order.addObserver(driver);

        // 4. Simulate Flow
        System.out.println("--- Restaurant Accepts Order ---");
        order.nextState(); // PREPARING

        System.out.println("--- Food is Ready ---");
        order.nextState(); // READY_FOR_PICKUP

        System.out.println("--- Driver Accepts ---");
        if(order.assignDriver(driver)) {
            System.out.println("Driver assigned successfully.");
        }

        System.out.println("--- Driver Picks Up ---");
        order.nextState(); // OUT_FOR_DELIVERY

        System.out.println("--- Driver Delivers ---");
        order.nextState(); // DELIVERED
    }
}
```
