# Code Walkthrough: Vending Machine

## Overview

Classic State Pattern interview question. Demonstrates finite state machine design.

---

## File Structure

```
java/v1-basic/
├── VendingMachineState.java  # State Pattern - all states
├── VendingMachine.java       # Context class
├── Inventory.java            # Product inventory management
├── Product.java              # Product entity
├── Slot.java                 # Physical slot in machine
├── Coin.java                 # Currency enum
└── VendingMachineDemo.java   # Demo entry point
```

```
python/v1-basic/
├── vending_machine_state.py  # State classes
├── vending_machine.py        # Context + demo
├── inventory.py              # Inventory management
├── product.py                # Product model
└── coin.py                   # Currency enum
```

---

## Design Pattern: State

### State Diagram

```
┌─────────────┐   insertCoin    ┌─────────────────┐
│    IDLE     │ ──────────────→ │  HAS_MONEY      │
└─────────────┘                 └────────┬────────┘
       ↑                                 │
       │        selectProduct           │
       │             ┌──────────────────┘
       │             ▼
       │    ┌─────────────────┐
       │    │  DISPENSING     │
       │    └────────┬────────┘
       │             │ dispenseProduct
       └─────────────┘
```

### Implementation

```java
// Location: VendingMachineState.java
interface VendingMachineState {
    void insertCoin(Coin coin);
    void selectProduct(String code);
    void dispense();
    void cancel();
}

class IdleState implements VendingMachineState { ... }
class HasMoneyState implements VendingMachineState { ... }
class DispensingState implements VendingMachineState { ... }
```

---

## Key Classes

| Class | Responsibility | Pattern |
|-------|---------------|---------|
| VendingMachine | Context, delegates to state | State (Context) |
| VendingMachineState | State interface | State |
| Inventory | Track products/slots | Composite |
| Product | Value object | - |

---

## Interview Questions

### 1. "Why State Pattern over if-else?"

- Each state has clear responsibilities
- Easy to add new states (e.g., MAINTENANCE)
- Avoids nested conditionals
- State transition logic localized

### 2. "How to handle concurrent access?"

- Synchronized state transitions
- AtomicReference for current state
- Thread-safe inventory with locks

### 3. "How to add refund functionality?"

Add to each state's `cancel()` method:
```java
void cancel() {
    context.returnBalance();
    context.setState(new IdleState());
}
```

### 4. "How to add payment types (card/mobile)?"

Use Strategy Pattern for payment:
```java
interface PaymentStrategy {
    boolean process(double amount);
}
```

---

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| insertCoin | O(1) | O(1) |
| selectProduct | O(1) | O(1) |
| dispense | O(1) | O(1) |
| getInventory | O(S) | O(1) |

Where S = number of slots

---

## Interview Extension Hooks (v3)

For follow-up variants, review:
- `java/v3-optimized/DispenseWorkflowPolicy.java`
- `python/v3-optimized/dispense_workflow_policy.py`

These contracts isolate payment application, inventory reservation, and state transition behavior.
