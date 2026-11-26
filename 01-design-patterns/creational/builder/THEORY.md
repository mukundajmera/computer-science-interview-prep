# Builder Pattern - Theory & Interview Guide

## 📚 Core Concept

The Builder pattern separates the construction of a complex object from its representation, allowing the same construction process to create different representations.

### Key Components

1. **Builder (Interface)**: Specifies steps to build product parts
2. **ConcreteBuilder**: Implements construction steps, provides result
3. **Director**: Orchestrates building using Builder interface
4. **Product**: The complex object being built

## 🎯 Problem It Solves

**Without Builder (Telescoping Constructor):**
```java
// Constructor with many parameters - confusing and error-prone!
Pizza pizza = new Pizza("large", true, true, false, true, false, 
                         "tomato", "mozzarella", true, false);
// What do all these booleans mean?!
```

**Problems:**
- Too many constructor parameters
- Unclear parameter meaning
- Must provide all parameters (even optional ones)
- Parameter order errors
- Immutability requires complex constructors

**With Builder:**
```java
Pizza pizza = new Pizza.Builder("large")
    .addCheese("mozzarella")
    .addTopping("pepperoni")
    .addTopping("mushrooms")
    .extraSauce()
    .build();
// Clear, readable, type-safe!
```

## 🏗️ UML Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    ┌─────────────┐          ┌─────────────────┐            │
│    │   Director  │          │   «interface»   │            │
│    ├─────────────┤          │     Builder     │            │
│    │ - builder   │          ├─────────────────┤            │
│    │+construct() │─────────▶│ +buildPartA()  │            │
│    └─────────────┘          │ +buildPartB()  │            │
│                             │ +getResult()   │            │
│                             └────────┬────────┘            │
│                                      │                     │
│                       ┌──────────────┼──────────────┐      │
│                       │              │              │      │
│              ┌────────┴───────┐    ┌─┴──────────────┴─┐   │
│              │ConcreteBuilder1│    │ ConcreteBuilder2 │   │
│              ├────────────────┤    ├──────────────────┤   │
│              │+buildPartA()   │    │ +buildPartA()    │   │
│              │+buildPartB()   │    │ +buildPartB()    │   │
│              │+getResult()    │    │ +getResult()     │   │
│              └───────┬────────┘    └────────┬─────────┘   │
│                      │                      │              │
│                      ▼                      ▼              │
│                 ┌─────────┐            ┌─────────┐        │
│                 │Product1 │            │Product2 │        │
│                 └─────────┘            └─────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✅ When to Use

1. **Complex object construction** with many parts or steps
2. **Many optional parameters** (4+ constructor parameters)
3. **Different representations** of the same construction process
4. **Immutable objects** with many properties
5. **Fluent interface** for readability

## ❌ When NOT to Use

1. Simple objects with few parameters
2. Objects with no optional configuration
3. When a simple constructor suffices

## 🎤 Interview Q&A

### Q1: Builder vs Factory - when to use each?

**A:**
| Builder | Factory |
|---------|---------|
| Step-by-step construction | Single-step creation |
| Many optional parameters | Few required parameters |
| Returns same type differently configured | Returns different subtypes |
| Focus: HOW to build | Focus: WHAT to build |

### Q2: How do you ensure a valid object is built?

**A:** 
1. **Validate in build()** - Check required fields before returning
2. **Required parameters in constructor** - Builder(size) makes size mandatory
3. **State machine** - Enforce order of method calls
4. **Fail-fast** - Throw immediately if invalid state

### Q3: Thread-safety of Builder?

**A:** Builders are typically NOT thread-safe (mutable during construction). For thread-safety:
- Create new builder per thread
- Make builder immutable (each method returns new builder)
- Synchronize externally

### Q4: How does Builder support immutability?

**A:** Builder collects all values mutably, then creates an immutable Product in build():
```java
public Product build() {
    return new Product(name, size, options); // Product is immutable
}
```

### Q5: Inner class vs separate class for Builder?

**A:** 
- **Inner class (recommended)**: `new Pizza.Builder()` - tightly coupled, access to private constructor
- **Separate class**: More flexible, testable independently, but looser coupling

## 💻 Code Patterns

### Java - Fluent Builder (Inner Class)
```java
public class Pizza {
    private final String size;
    private final List<String> toppings;
    
    private Pizza(Builder builder) {
        this.size = builder.size;
        this.toppings = List.copyOf(builder.toppings);
    }
    
    public static class Builder {
        private final String size; // Required
        private List<String> toppings = new ArrayList<>();
        
        public Builder(String size) {
            this.size = size;
        }
        
        public Builder addTopping(String topping) {
            toppings.add(topping);
            return this;
        }
        
        public Pizza build() {
            return new Pizza(this);
        }
    }
}
```

### Python - Fluent Builder
```python
class Pizza:
    def __init__(self, builder):
        self.size = builder.size
        self.toppings = list(builder.toppings)
    
    class Builder:
        def __init__(self, size):
            self.size = size
            self.toppings = []
        
        def add_topping(self, topping):
            self.toppings.append(topping)
            return self
        
        def build(self):
            return Pizza(self)
```

### Python - Dataclass + Builder
```python
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class Pizza:
    size: str
    toppings: List[str] = field(default_factory=list)
    
    @classmethod
    def builder(cls, size: str):
        return PizzaBuilder(size)

class PizzaBuilder:
    def __init__(self, size: str):
        self._size = size
        self._toppings = []
    
    def add_topping(self, topping: str):
        self._toppings.append(topping)
        return self
    
    def build(self) -> Pizza:
        return Pizza(self._size, tuple(self._toppings))
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Abstract Factory** | Can use builders to create products |
| **Composite** | Builder often builds composites |
| **Singleton** | Director can be Singleton |
| **Prototype** | Alternative - clone instead of build |

## 📁 Implementations

| Version | Description | Location |
|---------|-------------|----------|
| v1-basic | Inner class fluent builder | [Java](./java/v1-basic/) / [Python](./python/v1-basic/) |
| v2-variant | Director with reusable builders | [Java](./java/v2-variant/) / [Python](./python/v2-variant/) |
| v3-advanced | Type-safe builder with validation | [Java](./java/v3-advanced/) / [Python](./python/v3-advanced/) |

---

[← Back to Builder](./README.md)

---

## Interview Lens

- Use when construction has multiple optional fields or ordering constraints.
- Do not force Builder for tiny objects with simple constructors.
- Explain readability and validation benefits, then show fluent construction.
