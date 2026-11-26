# Vending Machine System

## Problem Statement

Design a vending machine system that handles product selection, payment processing, product dispensing, and change management.

---

## Functional Requirements

1. **Product Selection**: Display available products and allow selection
2. **Multiple Payment Methods**: Accept coins, notes, and digital payments
3. **Product Dispensing**: Dispense selected product after successful payment
4. **Change Calculation**: Return correct change to the customer
5. **Inventory Management**: Track product stock levels
6. **Refund Processing**: Allow cancellation and full refund before dispensing
7. **Admin Operations**: Restock products and collect money
8. **Product Categories**: Support different product types (snacks, beverages, etc.)

---

## Non-Functional Requirements

1. **Concurrency**: Handle multiple users at different machines
2. **Reliability**: No money loss during transactions
3. **Availability**: Graceful handling of out-of-stock scenarios
4. **Maintainability**: Easy to add new products and payment methods
5. **Real-time**: Instant feedback on all operations

---

## Constraints & Assumptions

- Machine has limited slots for products
- Each slot holds one product type with multiple quantities
- Coins accepted: 1c, 5c, 10c, 25c, 50c, $1
- Notes accepted: $1, $5, $10, $20
- Machine maintains minimum change reserve
- Products cannot be reserved
- One transaction at a time per machine

---

## Sample Interactions

```
1. User approaches machine
2. Machine displays available products with prices
3. User inserts $5 note
4. Machine shows current balance: $5.00
5. User selects Chips ($2.50)
6. Machine validates:
   - Product in stock? ✓
   - Sufficient payment? ✓ ($5.00 >= $2.50)
   - Can give change? ✓ ($2.50)
7. Machine dispenses Chips
8. Machine returns $2.50 in change (2x $1, 2x 25c)
9. Transaction complete
```

---

## Clarifying Questions to Ask

1. "What payment methods should be supported?"
2. "What denominations of coins/notes are accepted?"
3. "How is change calculated - fewest coins or available coins?"
4. "Should the machine support product reservations?"
5. "How are out-of-stock situations handled?"
6. "Is there an admin interface for restocking?"
7. "Should we track sales statistics?"
8. "How do we handle exact change only scenarios?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| VendingMachine | Main system, manages state and operations |
| Product | Item being sold |
| Slot | Container holding products |
| Coin/Note | Currency denominations |
| Inventory | Stock management |
| Transaction | Current purchase session |
| State | Machine's current operating state |

---

## State Machine

```
          [IDLE] ──────────────────────────────────────┐
             │                                          │
             │ insertMoney()                            │ cancelTransaction()
             ▼                                          │
        [HAS_MONEY] ────────────────────────────────────┤
             │                                          │
             │ selectProduct()                          │
             ▼                                          │
      [PRODUCT_SELECTED] ──────────────────────────────┤
             │                                          │
             │ dispense()                               │
             ▼                                          │
       [DISPENSING] ───────────────────────────────────┘
             │
             │ returnChange()
             ▼
          [IDLE]
```

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Core states, coin insertion, product selection, dispense |
| v2-extended | Multiple payment methods, refund, product categories, admin |
| v3-optimized | Thread-safe operations, concurrent transactions, optimized change calculation |
