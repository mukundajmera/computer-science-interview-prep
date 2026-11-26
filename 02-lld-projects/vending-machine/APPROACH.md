# Design Approach for Vending Machine

A step-by-step thought process for designing the vending machine system.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Vending Machine | ✅ Yes | Main system container |
| Product | ✅ Yes | Items being sold |
| Slot | ✅ Yes | Holds products in machine |
| Coin | ✅ Yes | Payment denomination |
| Note | ✅ Yes | Payment denomination |
| Inventory | ✅ Yes | Stock tracking |
| Transaction | ✅ Yes | Current purchase session |
| State | ✅ Yes | Machine's operating state |
| Change | ❌ No | Derived from coins |
| Display | ❌ No | UI concern, out of scope |

**Final Entities**: VendingMachine, Product, Slot, Coin, Currency, Inventory, Transaction, State

---

## Step 2: Define Relationships

```
VendingMachine (1) ──contains──> (n) Slot
Slot (1) ──holds──> (n) Product (same type)
VendingMachine (1) ──has──> (1) Inventory
VendingMachine (1) ──manages──> (1) Transaction (current)
VendingMachine (1) ──in──> (1) State
Transaction (1) ──for──> (0..1) Product
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| VendingMachine → Slot | Composition | Slots don't exist without machine |
| Slot → Product | Aggregation | Products can exist independently |
| VendingMachine → State | Association | State is machine's current mode |
| VendingMachine → Transaction | Composition | Transaction tied to machine |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **State** | ✅ Yes | Machine has distinct states with different behaviors |
| **Strategy** | ✅ Yes | Different payment methods, change calculation |
| **Singleton** | ❌ No | Multiple machines should be supported |
| **Observer** | 🔄 v2 | Inventory alerts when low stock |
| **Factory** | 🔄 v2 | Create different product types |

### Pattern Application:

1. **State Pattern** - VendingMachineState
   - States: IdleState, HasMoneyState, ProductSelectedState, DispensingState
   - Each state handles operations differently
   - Clean state transitions

2. **Strategy Pattern** - PaymentStrategy, ChangeStrategy
   - Different payment method processing
   - Different change calculation algorithms
   - Easy to add new payment types

---

## Step 4: Design Classes

### Core Classes:

#### VendingMachine
- **Attributes**: 
  - `slots: Map<String, Slot>`
  - `currentBalance: double`
  - `currentState: VendingMachineState`
  - `selectedProduct: Product`
  - `coinInventory: Map<Coin, Integer>`
- **Methods**:
  - `insertMoney(currency): void`
  - `selectProduct(slotCode): Product`
  - `dispense(): Product`
  - `cancelTransaction(): double`
  - `getAvailableProducts(): List<Product>`

#### VendingMachineState (Interface)
- **Methods**:
  - `insertMoney(currency): void`
  - `selectProduct(slotCode): Product`
  - `dispense(): Product`
  - `cancelTransaction(): double`
- **Implementations**: IdleState, HasMoneyState, ProductSelectedState, DispensingState

#### Product
- **Attributes**:
  - `code: String`
  - `name: String`
  - `price: double`
  - `category: ProductCategory`
- **Methods**:
  - Getters

#### Slot
- **Attributes**:
  - `code: String`
  - `product: Product`
  - `quantity: int`
  - `maxCapacity: int`
- **Methods**:
  - `dispenseOne(): Product`
  - `restock(quantity): void`
  - `isEmpty(): boolean`

#### Coin (Enum)
- **Values**: PENNY(0.01), NICKEL(0.05), DIME(0.10), QUARTER(0.25), HALF_DOLLAR(0.50), DOLLAR(1.00)

#### Inventory
- **Attributes**:
  - `slots: Map<String, Slot>`
  - `coinStock: Map<Coin, Integer>`
- **Methods**:
  - `getAvailableProducts(): List<Product>`
  - `addCoins(coin, count): void`
  - `removeCoins(coin, count): boolean`
  - `canMakeChange(amount): boolean`

---

## Step 5: Handle Edge Cases

### Input Validation:
- Invalid currency (foreign coins)
- Negative or zero amounts
- Invalid slot codes
- Null product selection

### Business Logic:
- Insufficient payment for selected product
- Out of stock product
- Cannot make exact change
- Transaction timeout
- Double dispense prevention
- Refund when no money inserted

### Concurrency (v3):
- Multiple operations on same machine
- Inventory updates during transaction
- Race condition on last item

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Find product by slot | O(n) scan | O(1) with HashMap |
| Calculate change | O(amount) | Greedy O(denominations) |
| Check stock | O(n) | O(1) with cached counts |

### Change Calculation:
- Greedy algorithm for fewest coins
- Dynamic programming for guaranteed solution
- Track available denominations

### Caching:
- Cache available products list
- Update on stock changes

---

## Step 7: Version Progression

### v1-basic
- Core State pattern implementation
- Coin insertion and balance tracking
- Basic product selection and dispensing
- Simple change return
- Single-threaded

### v2-extended
- Multiple payment methods (Strategy pattern)
- Product categories
- Admin operations (restock, collect money)
- Better error handling
- Transaction history

### v3-optimized
- Thread-safe with locks
- Concurrent-safe inventory
- Optimized change calculation
- Timeout handling
- Low stock alerts

---

## Code Organization

```
vending-machine/
├── java/
│   ├── v1-basic/
│   │   ├── VendingMachine.java
│   │   ├── VendingMachineState.java
│   │   ├── Product.java
│   │   ├── Slot.java
│   │   ├── Coin.java
│   │   ├── Inventory.java
│   │   └── VendingMachineDemo.java
│   ├── v2-extended/
│   │   ├── [All v1 classes enhanced]
│   │   ├── PaymentStrategy.java
│   │   ├── ProductCategory.java
│   │   └── TransactionHistory.java
│   └── v3-optimized/
│       └── [Thread-safe versions]
└── python/
    └── [Same structure]
```

---

## Interview Discussion Points

1. **Why State Pattern?**
   - Clear separation of behavior per state
   - Easy to add new states
   - Prevents invalid operations (can't dispense without payment)
   - Self-documenting state transitions

2. **How to handle "exact change only"?**
   - Check if machine can make change before accepting payment
   - Display warning to user
   - Reject payment if change impossible

3. **Concurrency concerns?**
   - Lock on transaction operations
   - Atomic inventory updates
   - Prevent race conditions on last item

4. **Extensibility for new products?**
   - Add new ProductCategory enum values
   - No code changes needed for new products
   - Just add to inventory
