# Strategy Pattern - Theory & Interview Guide

## 📚 Core Concept

The Strategy pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

### Key Components

1. **Strategy (Interface)**: Declares operations common to all supported algorithms
2. **ConcreteStrategy**: Implements the algorithm using the Strategy interface
3. **Context**: Maintains a reference to a Strategy object and delegates to it

## 🎯 Problem It Solves

**Without Strategy:**
```java
class PaymentProcessor {
    void processPayment(String type, double amount) {
        if (type.equals("credit_card")) {
            // Credit card logic
        } else if (type.equals("paypal")) {
            // PayPal logic
        } else if (type.equals("crypto")) {
            // Crypto logic
        }
        // More conditionals as payment methods grow...
    }
}
```

**Problems:**
- Violates Open/Closed Principle (must modify class to add payment methods)
- Growing conditional complexity
- Hard to test individual payment methods
- Duplicated code across conditionals

**With Strategy:**
```java
interface PaymentStrategy {
    void pay(double amount);
}

class PaymentProcessor {
    private PaymentStrategy strategy;
    
    void setStrategy(PaymentStrategy strategy) {
        this.strategy = strategy;
    }
    
    void processPayment(double amount) {
        strategy.pay(amount);  // Delegation
    }
}
```

## 🏗️ UML Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    ┌─────────────────┐          ┌─────────────────┐        │
│    │     Client      │          │    «interface»  │        │
│    └────────┬────────┘          │    Strategy     │        │
│             │                   ├─────────────────┤        │
│             │ uses              │ + algorithm()   │        │
│             ▼                   └────────┬────────┘        │
│    ┌─────────────────┐                   │                 │
│    │     Context     │◆─────────────────▶│                 │
│    ├─────────────────┤    strategy       │                 │
│    │ - strategy      │          ┌────────┴────────┐        │
│    │ + setStrategy() │          │                 │        │
│    │ + execute()     │  ┌───────┴─────┐  ┌───────┴─────┐  │
│    └─────────────────┘  │ StrategyA   │  │ StrategyB   │  │
│                         ├─────────────┤  ├─────────────┤  │
│                         │+ algorithm()│  │+ algorithm()│  │
│                         └─────────────┘  └─────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Benefits

1. **Open/Closed Principle**: Add new strategies without modifying existing code
2. **Single Responsibility**: Each strategy class handles one algorithm
3. **Runtime Flexibility**: Swap algorithms dynamically
4. **Eliminates Conditionals**: No switch/if-else chains
5. **Easy Testing**: Test each strategy in isolation

## ❌ Drawbacks

1. **Class Explosion**: Many strategy classes for many algorithms
2. **Client Awareness**: Clients must understand different strategies
3. **Overhead**: May be overkill for simple scenarios

## 🎤 Interview Q&A

### Q1: How does Strategy differ from State pattern?
**A:** Both use similar structures (context + interface + implementations), but:
- **Strategy**: Client chooses strategy; algorithms are interchangeable alternatives
- **State**: Object changes its own state; behavior depends on internal state

### Q2: When would you NOT use Strategy?
**A:** 
- Only 2-3 algorithms that never change
- No runtime switching needed
- Simple inline conditionals suffice
- Algorithms require access to context's private data

### Q3: How does Strategy support Open/Closed Principle?
**A:** New strategies can be added by creating new classes implementing the interface, without modifying existing Context or Strategy code.

### Q4: Strategy vs Dependency Injection?
**A:** Strategy is a design pattern focused on interchangeable algorithms. DI is a technique for providing dependencies. They're complementary—DI can be used to inject strategies.

### Q5: How would you implement Strategy in a functional language?
**A:** Use first-class functions instead of strategy classes:
```python
def pay_with_credit(amount): ...
def pay_with_paypal(amount): ...

def process_payment(strategy_fn, amount):
    strategy_fn(amount)
```

## 🔍 Common Mistakes

1. **God Context**: Context does too much instead of delegating
2. **Leaky Abstractions**: Strategy interface too specific to one implementation
3. **Wrong Pattern Choice**: Using Strategy when State is more appropriate
4. **Over-Engineering**: Creating strategies for single-use algorithms

## 💻 Code Patterns

### Java - Interface-based
```java
interface Strategy {
    int execute(int a, int b);
}

class Add implements Strategy {
    @Override
    public int execute(int a, int b) { return a + b; }
}
```

### Python - First-class functions
```python
def add(a, b): return a + b
def subtract(a, b): return a - b

def calculate(strategy, a, b):
    return strategy(a, b)

calculate(add, 5, 3)  # 8
```

### Python - Protocol-based
```python
from typing import Protocol

class Strategy(Protocol):
    def execute(self, a: int, b: int) -> int: ...
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **State** | Similar structure, different intent |
| **Factory** | Can create strategy instances |
| **Decorator** | Both modify behavior; Strategy replaces, Decorator wraps |
| **Template Method** | Template Method uses inheritance; Strategy uses composition |

---

[← Back to Strategy](./README.md)

---

## Interview Lens

- Use when behavior varies by policy or algorithm and must be replaceable.
- Context should depend on strategy abstraction, not concrete implementations.
- In follow-ups, demonstrate adding one strategy without modifying context logic.
