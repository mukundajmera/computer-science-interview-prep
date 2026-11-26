# Code Walkthrough: Restaurant Management

## Overview

Order management with kitchen and billing.

---

## Core Flow

```
Table → Menu Browse → Order → Kitchen → Serve → Bill → Payment
```

---

## Key Classes

```java
class Restaurant {
    List<Table> tables;
    Menu menu;
    Kitchen kitchen;
    
    Order createOrder(Table table, List<MenuItem> items);
}

class Order {
    Table table;
    List<OrderItem> items;
    OrderStatus status;
    
    void addItem(MenuItem item, int qty);
    void submit();  // Send to kitchen
}

class Kitchen {
    Queue<Order> pendingOrders;
    void processOrder(Order order);
}
```

---

## Interview Questions

### 1. "How to handle table reservations?"

```java
class Reservation {
    Table table;
    Customer customer;
    LocalDateTime time;
    int partySize;
}

boolean bookTable(int partySize, LocalDateTime time) {
    Table available = findAvailableTable(partySize, time);
    if (available != null) {
        reservations.add(new Reservation(...));
        return true;
    }
    return false;
}
```

### 2. "How to split bills?"

```java
List<Bill> splitBill(Order order, int ways) {
    double perPerson = order.getTotal() / ways;
    return IntStream.range(0, ways)
        .mapToObj(i -> new Bill(perPerson))
        .collect(toList());
}
```

### 3. "How to handle order modifications?"

Only allow changes before kitchen processing:
```java
void modifyOrder(Order order, MenuItem item, int newQty) {
    if (order.status == PENDING) {
        order.updateItem(item, newQty);
    } else {
        throw new IllegalStateException("Order already in kitchen");
    }
}
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Observer** | Kitchen notifies when ready |
| **State** | Order status transitions |
| **Command** | Order modifications |
