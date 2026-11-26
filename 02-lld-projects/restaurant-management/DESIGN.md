# Design for Restaurant Management System

## Mermaid Class Diagram

```mermaid
classDiagram
    class Restaurant {
        <<Singleton>>
        -String restaurantId
        -String name
        -List~Table~ tables
        -Menu menu
        -List~Waiter~ staff
        -List~Reservation~ reservations
        +getAvailableTables(int, LocalDateTime) List~Table~
        +makeReservation(String, int, LocalDateTime) Reservation
        +assignTable(int) Table
        +createOrder(Table) Order
        +getMenu() Menu
    }

    class Table {
        -String tableId
        -int capacity
        -TableStatus status
        -Order currentOrder
        +occupy() void
        +release() void
        +isAvailable() boolean
        +setCurrentOrder(Order) void
    }

    class Reservation {
        -String reservationId
        -String customerName
        -String customerPhone
        -int partySize
        -LocalDateTime dateTime
        -Table table
        -ReservationStatus status
        +confirm() void
        +cancel() void
        +checkIn() void
    }

    class Menu {
        -String menuId
        -List~MenuItem~ items
        -Map~String, List~ categories
        +getItemsByCategory(String) List~MenuItem~
        +getItem(String) MenuItem
        +addItem(MenuItem) void
        +removeItem(String) void
    }

    class MenuItem {
        -String itemId
        -String name
        -String description
        -double price
        -String category
        -boolean isAvailable
        -int preparationTime
        +getPrice() double
        +isAvailable() boolean
        +setAvailable(boolean) void
    }

    class Order {
        -String orderId
        -Table table
        -Waiter waiter
        -List~OrderItem~ items
        -OrderStatus status
        -LocalDateTime createdAt
        -LocalDateTime completedAt
        +addItem(MenuItem, int, String) void
        +removeItem(String) void
        +submit() void
        +prepare() void
        +serve() void
        +getTotal() double
    }

    class OrderItem {
        -String orderItemId
        -MenuItem menuItem
        -int quantity
        -String modifications
        -double price
        -OrderItemStatus status
        +getSubtotal() double
    }

    class Bill {
        -String billId
        -Order order
        -double subtotal
        -double taxRate
        -double tax
        -double tip
        -double total
        -PaymentStatus paymentStatus
        +calculate() void
        +addTip(double) void
        +split(int) List~Bill~
        +pay(PaymentMethod) boolean
    }

    class Waiter {
        -String waiterId
        -String name
        -List~Table~ assignedTables
        +assignTable(Table) void
        +takeOrder(Table) Order
        +serveOrder(Order) void
    }

    class Kitchen {
        -Queue~Order~ orderQueue
        -List~Order~ inProgress
        +receiveOrder(Order) void
        +prepareOrder(Order) void
        +markReady(Order) void
        +getNextOrder() Order
    }

    class TableStatus {
        <<enumeration>>
        AVAILABLE
        OCCUPIED
        RESERVED
        CLEANING
    }

    class OrderStatus {
        <<enumeration>>
        PLACED
        PREPARING
        READY
        SERVED
        BILLED
        COMPLETED
    }

    class ReservationStatus {
        <<enumeration>>
        PENDING
        CONFIRMED
        CHECKED_IN
        COMPLETED
        CANCELLED
        NO_SHOW
    }

    Restaurant "1" *-- "n" Table : has
    Restaurant "1" *-- "1" Menu : has
    Restaurant "1" *-- "n" Waiter : employs
    Restaurant "1" *-- "n" Reservation : manages
    Restaurant "1" *-- "1" Kitchen : has
    Menu "1" *-- "n" MenuItem : contains
    Table "1" --> "0..1" Order : currentOrder
    Order "1" *-- "n" OrderItem : contains
    Order --> Table
    Order --> Waiter
    OrderItem --> MenuItem
    Order --> Bill : generates
    Reservation --> Table
    Waiter "1" --> "n" Table : serves
    Kitchen "1" --> "n" Order : processes
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    RESTAURANT ||--o{ TABLE : has
    RESTAURANT ||--|| MENU : has
    MENU ||--o{ MENU_ITEM : contains
    TABLE ||--o{ ORDER : has
    TABLE ||--o{ RESERVATION : reserved_for
    CUSTOMER ||--o{ RESERVATION : makes
    ORDER ||--o{ ORDER_ITEM : contains
    MENU_ITEM ||--o{ ORDER_ITEM : ordered_as
    ORDER ||--|| BILL : generates
    WAITER ||--o{ ORDER : takes
    WAITER ||--o{ TABLE : serves

    RESTAURANT {
        string restaurant_id PK
        string name
        string address
        string phone
        time opening_time
        time closing_time
    }

    TABLE {
        string table_id PK
        string restaurant_id FK
        int table_number
        int capacity
        string status
        string section
    }

    MENU {
        string menu_id PK
        string restaurant_id FK
        string name
        boolean is_active
    }

    MENU_ITEM {
        string item_id PK
        string menu_id FK
        string name
        text description
        decimal price
        string category
        boolean is_available
        int prep_time_minutes
    }

    RESERVATION {
        string reservation_id PK
        string table_id FK
        string customer_name
        string customer_phone
        int party_size
        datetime reserved_for
        string status
        timestamp created_at
    }

    CUSTOMER {
        string customer_id PK
        string name
        string email
        string phone
        int visit_count
    }

    ORDER {
        string order_id PK
        string table_id FK
        string waiter_id FK
        string status
        timestamp created_at
        timestamp completed_at
    }

    ORDER_ITEM {
        string order_item_id PK
        string order_id FK
        string menu_item_id FK
        int quantity
        text modifications
        decimal price
        string status
    }

    BILL {
        string bill_id PK
        string order_id FK
        decimal subtotal
        decimal tax_rate
        decimal tax
        decimal tip
        decimal total
        string payment_status
        string payment_method
        timestamp paid_at
    }

    WAITER {
        string waiter_id PK
        string restaurant_id FK
        string name
        string phone
        boolean is_active
    }
```

**Schema Notes:**
- `ORDER` flows through states: PLACED → PREPARING → READY → SERVED → BILLED
- `ORDER_ITEM.modifications` stores special requests (no onions, extra sauce)
- `RESERVATION` links customer to table for specific datetime
- `BILL` supports tips and multiple payment methods

---

## Class Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      Table      │     │   Reservation   │     │    MenuItem     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ - tableId       │◄────│ - reservationId │     │ - itemId        │
│ - capacity      │     │ - customerName  │     │ - name          │
│ - status        │     │ - partySize     │     │ - price         │
│ - currentOrder  │     │ - dateTime      │     │ - category      │
└────────┬────────┘     └─────────────────┘     └────────┬────────┘
         │                                               │
         │1                                              │*
         │                                               │
         ▼*                                              ▼
┌─────────────────┐                            ┌─────────────────┐
│      Order      │◄───────────────────────────│    OrderItem    │
├─────────────────┤                            ├─────────────────┤
│ - orderId       │                            │ - menuItem      │
│ - table         │                            │ - quantity      │
│ - items         │                            │ - modifications │
│ - status        │                            │ - price         │
│ - createdAt     │                            └─────────────────┘
└────────┬────────┘
         │1
         │
         ▼1
┌─────────────────┐
│      Bill       │
├─────────────────┤
│ - billId        │
│ - subtotal      │
│ - tax           │
│ - tip           │
│ - total         │
└─────────────────┘
```

## Core Classes

### Table
- **Attributes**: tableId, capacity, status (AVAILABLE/OCCUPIED/RESERVED)
- **Methods**: occupy(), release(), isAvailable()

### TableStatus (Enum)
- AVAILABLE, OCCUPIED, RESERVED, CLEANING

### Order
- **Attributes**: orderId, table, items, status, createdAt
- **Methods**: addItem(), removeItem(), submit(), prepare(), serve()
- **Patterns Used**: State pattern

### OrderStatus (Enum)
- PLACED, PREPARING, READY, SERVED, BILLED, COMPLETED

### MenuItem
- **Attributes**: itemId, name, description, price, category
- **Methods**: getPrice(), isAvailable()

### Bill
- **Attributes**: billId, order, subtotal, taxRate, tip, total
- **Methods**: calculate(), addTip(), split()

## Key Design Decisions

1. **State for Orders**: Clean order workflow transitions
2. **Observer for Kitchen**: Real-time updates to kitchen display
3. **Strategy for Billing**: Different tax and tip calculations

## Complexity Analysis

- **Table search by capacity**: O(T) where T = tables
- **Order operations**: O(1)
- **Bill calculation**: O(I) where I = items in order
