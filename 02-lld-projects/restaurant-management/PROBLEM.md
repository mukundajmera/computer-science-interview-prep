# Restaurant Management System

## Problem Statement

Design a restaurant management system that handles table reservations, order management, kitchen workflow, and billing operations.

---

## Functional Requirements

1. **Table Management**: Track tables with capacity and status
2. **Reservations**: Book tables for specific time slots
3. **Menu Management**: Maintain menu items with prices
4. **Order Taking**: Create and manage customer orders
5. **Kitchen Workflow**: Track order states through preparation
6. **Billing**: Calculate bills with taxes, tips, split options
7. **Inventory**: Track ingredient availability
8. **Waitlist**: Handle walk-in customers when full

---

## Non-Functional Requirements

1. **Concurrency**: Handle multiple simultaneous reservations
2. **Real-time**: Kitchen display updates immediately
3. **Availability**: Critical during peak hours
4. **Performance**: Fast table availability checks

---

## Order States

```
Placed → Preparing → Ready → Served → Billed → Completed
```

---

## Sample Interactions

```
1. Customer reserves table for 4 at 7 PM
2. Host confirms reservation and assigns table
3. Server takes order (2 appetizers, 4 mains)
4. Order sent to kitchen display
5. Kitchen prepares dishes, marks ready
6. Server delivers food, marks served
7. Customer requests bill, pays with tip
8. Table cleared and marked available
```

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| Table | Capacity, status, current order |
| Reservation | Time slot, party size, table |
| MenuItem | Name, price, category, availability |
| Order | Items, status, table, timestamps |
| OrderItem | MenuItem, quantity, modifications |
| Bill | Order total, tax, tip, payment |
| RestaurantService | Main facade |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Tables, menu, orders, simple billing |
| v2-extended | Reservations, order modifications, split bills |
| v3-optimized | Concurrent reservations, kitchen queue, waitlist |
