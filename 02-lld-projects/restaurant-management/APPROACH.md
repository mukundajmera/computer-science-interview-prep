# Design Approach for Restaurant Management System

## Step 1: Identify Core Entities

| Noun | Class? | Reason |
|------|--------|--------|
| Table | ✅ | Seating resource |
| Reservation | ✅ | Booking record |
| MenuItem | ✅ | Menu offering |
| Order | ✅ | Customer order |
| OrderItem | ✅ | Individual item in order |
| Bill | ✅ | Payment record |

## Step 2: Define Relationships

```
Table 1----* Order
Reservation 1----1 Table
Order 1----* OrderItem
OrderItem *----1 MenuItem
Order 1----1 Bill
```

## Step 3: Choose Design Patterns

| Pattern | Application |
|---------|-------------|
| **Observer** | Kitchen display notifications |
| **State** | Order state management |
| **Command** | Order operations (for undo) |
| **Strategy** | Billing calculations |
| **Singleton** | Restaurant service |

## Step 4: Design Classes

### Table
- **Attributes**: tableId, capacity, status, currentOrder
- **Methods**: occupy(), release(), isAvailable()

### Order
- **Attributes**: orderId, table, items, status, timestamps
- **Methods**: addItem(), prepare(), serve(), complete()
- **Patterns**: State pattern for status

### MenuItem
- **Attributes**: itemId, name, price, category, available
- **Methods**: updatePrice(), toggleAvailability()

### Bill
- **Attributes**: billId, order, subtotal, tax, tip, total
- **Methods**: calculate(), split(), addTip()

## Step 5: Handle Edge Cases

1. **Double Booking**: Lock tables during reservation
2. **Out of Stock**: Check availability before ordering
3. **Order Modifications**: Track changes
4. **Split Bills**: Divide by items or equally
5. **Concurrent Orders**: Per-table locking

## Step 6: Optimization Opportunities

1. **Table Index**: HashMap by capacity for fast search
2. **Kitchen Queue**: Priority queue for order preparation
3. **Concurrent Locks**: Fine-grained per-table locks
