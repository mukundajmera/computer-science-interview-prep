# Strong Answer: Vending Machine System

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Vending Machine System, I will first clarify the requirements to establish our system's boundaries. Based on the problem statement, our core requirements include supporting multiple product categories (snacks, beverages) and multiple payment methods (coins, notes). The machine must reliably handle product selection, ensure accurate change calculation, and manage inventory levels effectively. I will prioritize consistency and thread safety under concurrent operations, ensuring no money is lost during race conditions like double-dispensing."

### Explicit Clarifications
- **Payment & Denominations**: We accept coins (1c, 5c, 10c, 25c, 50c, $1) and notes ($1, $5, $10, $20).
- **Change Strategy**: Change is calculated using available inventory coins (fewest coins strategy, bounded by inventory).
- **Failure Handling**: If an item is out of stock, the transaction cannot proceed. If an error occurs, the exact inserted funds must be rolled back (refunded) to the user.

## 2. Entity Modeling & Core Components (5-15 minutes)

**Say:** "Let's define the core entities and APIs. The `VendingMachine` acts as the context orchestrator. It manages a `VendingMachineState` to handle the lifecycle of operations. Inside, an `Inventory` tracks available `Slot`s (which hold a specific `Product` and quantity) and the currency stock."

### Key Entities
| Entity | Responsibility |
|--------|---------------|
| `VendingMachine` | Manages state, delegates user actions, and holds global context (balance, selected slot). |
| `Inventory` | Manages both product `Slot`s and currency stock, enforcing capacity limits. |
| `Slot` | Holds a `Product`, tracks quantity (0 to `max_capacity`), handles `dispenseOne()` operations. |
| `VendingMachineState` | Abstract interface defining `insertMoney`, `selectProduct`, `dispense`, and `cancel`. |
| `Coin` | Enum/Value object representing currency denominations. |

### Public APIs
- **Insert Money**: Java: `insertMoney(Coin coin)`, Python: `insert_money(coin: Coin)`
  - Adds money, updates balance, and transitions state to `HAS_MONEY`.
- **Select Product**: Java: `selectProduct(String slotCode)`, Python: `select_product(slot_code: str)`
  - Checks if the slot is valid, has stock, and if the current balance is sufficient. Verifies that exact change can be made if required.
- **Dispense**: Java: `dispense()`, Python: `dispense() -> Optional[Product]`
  - Decrements stock, adds inserted coins to inventory, calculates and returns change, dispenses product.
- **Cancel Transaction**: Java: `cancelTransaction()`, Python: `cancel_transaction() -> List[Coin]`
  - Refunds the inserted balance and resets the state to `IDLE`.

## 3. Design Pattern Justifications (15-25 minutes)

**Say:** "To manage the machine's operational lifecycle, I will utilize the **State Pattern**. The machine transitions sequentially: `IDLE` -> `HAS_MONEY` -> `PRODUCT_SELECTED`."

### Design Alternatives
1. **State Pattern vs. Switch Statements**: Using `if/switch` inside a single machine class for state management creates brittle, tightly coupled code that violates the Open-Closed Principle. The State pattern isolates the logic for each phase (`IdleState`, `HasMoneyState`, `ProductSelectedState`), making it robust against missing edge cases (e.g., trying to dispense without paying).
2. **Strategy Pattern for Change Calculation**: While the current implementation computes change linearly using greedy selection, a Strategy Pattern could allow us to hot-swap change calculation policies (e.g., fewest coins vs. prioritizing overstocked coins) without touching core logic.

## 4. Correctness, Complexity & Acceptance Criteria (25-35 minutes)

**Say:** "Our solution ensures strict correctness across core operations. For instance, **normal use-cases** correctly deduct stock and return accurate change. **Empty/invalid inputs** (like selecting an invalid or empty slot) safely reject the action without altering state. **Duplicate operations** are handled idempotently where appropriate. The system respects the **capacity boundary**; a slot cannot exceed its `maxCapacity` during restock."

### Explicit Reference Contracts
To satisfy robustness guarantees, the system enforces the following explicit reference contracts natively in both Java and Python:
- **Normal Use-Case**: Inserting $2.00 for a $1.50 item correctly dispenses the item, decrements stock, and returns exactly $0.50 in change.
- **Empty/Invalid Input**: Attempting to select an invalid slot code ("Z9") or an out-of-stock item rejects the action safely (early exit), leaving the machine in `HAS_MONEY` state with the balance intact.
- **Duplicate Operation**: Duplicate operations (e.g., rapid double-clicking `dispense()`) are handled idempotently where appropriate, mitigated by transaction locks and state transitions in both Java and Python versions.
- **Capacity Boundary**: Restocking a slot beyond its limit safely rejects the overflow. Adding 10 items to a slot with 5 items (max capacity 10) only adds 5 and ignores the rest.
- **Failure Rollback**: The `cancelTransaction()` flow guarantees an all-or-nothing rollback, safely refunding all inserted coins and returning the state to `IDLE`, leaving inventory untouched.

## 5. Version-Specific Feature Deltas & Testing
The system evolves across iterations (Answer and source code version deltas agree):
- **v1-basic**: Single-threaded implementation using the standard State Pattern.
- **v2-extended**: Adds more product categories and denominations.
- **v3-optimized**: Introduces explicit transaction locks for thread safety.

**Testing Strategy**: Focused tests target the specific version (`v3-optimized`) rather than silently importing `v1`. The Python test suite isolates paths to target `v3-optimized`, and Java tests compile against the target directory to ensure strict version alignment.

## 6. Failure and Concurrency Discussion (35-45 minutes)

**Say:** "The hardest problem in vending systems is concurrent state mutations—specifically, two users attempting to purchase the last item simultaneously, or a user cancelling a transaction at the exact moment a dispense is triggered."

### Concrete Concurrency Implementation (v3-optimized)
To guarantee thread-safety, the `VendingMachine` introduces a **transaction lock** (`threading.Lock` in Python, or monitor locks in Java). 

- **Thread-Safety Strategy**: The transaction lock serializes full purchase sequences. When a user calls `insert_money()`, the machine acquires the lock and binds it to the current thread identifier. 
- **Atomic Operations**: Subsequent actions like `select_product()` execute under the already-held lock. Finally, `dispense()` or `cancel_transaction()` release the lock upon completion.

**Implementation Highlight (Java/Python Code)**:
The Python v3 implementation demonstrates this directly:
```python
    def dispense(self) -> Optional[Product]:
        """Dispense the selected product. Releases transaction lock."""
        self._acquire_transaction()
        try:
            return self._current_state.dispense(self)
        finally:
            self._release_transaction()
```
The Java implementation mirrors this behavior via state transition guards.

- **Failure Scenario**: Without this lock, two concurrent threads could both verify that `quantity == 1`, deduct the balance, and both attempt to dispense, leading to a double-dispense and corrupted inventory. By forcing the lock to wrap the entire logical transaction (insert -> select -> dispense), the state remains absolutely consistent.

---

*This canonical answer directly maps to the `v3-optimized` implementations in both Java and Python.*

