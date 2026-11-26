# Factory Method Pattern - Theory & Interview Guide

## 📚 Core Concept

The Factory Method pattern defines an interface for creating objects, but lets subclasses decide which class to instantiate. It delegates the instantiation logic to child classes.

### Key Components

1. **Product (Interface)**: Common interface for all objects the factory creates
2. **ConcreteProduct**: Specific implementation of the Product
3. **Creator (Abstract)**: Declares the factory method
4. **ConcreteCreator**: Overrides factory method to return ConcreteProduct

## 🎯 Problem It Solves

**Without Factory Method:**
```java
// Tight coupling - code must know all concrete classes
Document doc;
if (type.equals("pdf")) {
    doc = new PDFDocument();
} else if (type.equals("word")) {
    doc = new WordDocument();
} else if (type.equals("excel")) {
    doc = new ExcelDocument();
}
// Must modify this code for every new document type!
```

**Problems:**
- Violates Open/Closed Principle
- Client code tightly coupled to concrete classes
- Adding new types requires changing existing code
- Difficult to test (can't mock creation)

**With Factory Method:**
```java
Document doc = documentFactory.createDocument(type);
// Factory handles creation, client code doesn't change
```

## 🏗️ UML Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    ┌─────────────────┐          ┌─────────────────┐        │
│    │    Creator      │          │    «interface»  │        │
│    │   (Abstract)    │          │     Product     │        │
│    ├─────────────────┤          ├─────────────────┤        │
│    │ +factoryMethod()│ creates  │ + operation()   │        │
│    │ +someOperation()│─────────▶└────────┬────────┘        │
│    └────────┬────────┘                   │                 │
│             │                   ┌────────┴────────┐        │
│    ┌────────┴────────┐          │                 │        │
│    │                 │  ┌───────┴─────┐  ┌───────┴─────┐  │
│    │ ConcreteCreatorA│  │ConcreteProductA│ │ConcreteProductB│
│    ├─────────────────┤  ├─────────────┤  ├─────────────┤  │
│    │+factoryMethod() │  │+ operation()│  │+ operation()│  │
│    │ → returns A     │  └─────────────┘  └─────────────┘  │
│    └─────────────────┘                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✅ When to Use

1. **Unknown concrete types at compile time** - Type determined at runtime
2. **Subclasses should decide** - Which class to instantiate
3. **Centralized creation logic** - Keep object creation in one place
4. **Framework/library design** - Users extend your classes

## ❌ When NOT to Use

1. Simple object creation with no variation
2. Object types known at compile time and won't change
3. Would result in many subclasses for simple selection

## 🎤 Interview Q&A

### Q1: Factory Method vs Simple Factory vs Abstract Factory?

**A:**
| Pattern | Purpose | Example |
|---------|---------|---------|
| **Simple Factory** | Static method creates objects | `ShapeFactory.create("circle")` |
| **Factory Method** | Subclasses decide what to create | Abstract `createDocument()` |
| **Abstract Factory** | Create families of related objects | UIFactory → Button + Checkbox |

### Q2: How does Factory Method support Open/Closed Principle?

**A:** To add a new product type, you create a new ConcreteProduct and ConcreteCreator without modifying existing code. The system is open for extension (new creators) and closed for modification.

### Q3: Can you give a real-world example?

**A:** 
- **Logistics**: `TransportFactory` → Truck, Ship, Plane
- **Documents**: `DocumentCreator` → PDF, Word, HTML
- **Payments**: `PaymentProcessor` → CreditCard, PayPal, Crypto
- **Notifications**: `NotificationFactory` → Email, SMS, Push

### Q4: Factory Method vs Dependency Injection?

**A:** 
- **Factory Method**: Object creation delegated to subclasses via inheritance
- **DI**: Dependencies provided from outside (composition over inheritance)

DI is often preferred in modern applications for better testability and flexibility.

### Q5: What's the relationship with Template Method pattern?

**A:** Factory Method is often called within Template Method. The template defines the algorithm structure, and factory method creates the objects needed by that algorithm.

## 🔍 Common Mistakes

1. **Overusing factories** for simple object creation
2. **God factory** that knows about all concrete types
3. **Returning null** instead of throwing exception
4. **Not using interface** for products

## 💻 Code Patterns

### Java - Classic Factory Method
```java
abstract class Creator {
    public abstract Product createProduct();
    
    public void doSomething() {
        Product product = createProduct(); // Factory Method
        product.operation();
    }
}

class ConcreteCreatorA extends Creator {
    @Override
    public Product createProduct() {
        return new ConcreteProductA();
    }
}
```

### Java - Parameterized Factory
```java
class DocumentFactory {
    public Document createDocument(String type) {
        return switch (type) {
            case "pdf" -> new PDFDocument();
            case "word" -> new WordDocument();
            default -> throw new IllegalArgumentException("Unknown type");
        };
    }
}
```

### Python - Factory Method
```python
from abc import ABC, abstractmethod

class Creator(ABC):
    @abstractmethod
    def create_product(self):
        pass
    
    def some_operation(self):
        product = self.create_product()
        return product.operation()

class ConcreteCreatorA(Creator):
    def create_product(self):
        return ConcreteProductA()
```

### Python - Registry-based Factory
```python
class VehicleFactory:
    _registry = {}
    
    @classmethod
    def register(cls, vehicle_type, vehicle_class):
        cls._registry[vehicle_type] = vehicle_class
    
    @classmethod
    def create(cls, vehicle_type, **kwargs):
        if vehicle_type not in cls._registry:
            raise ValueError(f"Unknown type: {vehicle_type}")
        return cls._registry.get(vehicle_type)(**kwargs)

# Usage
VehicleFactory.register("car", Car)
VehicleFactory.register("truck", Truck)
vehicle = VehicleFactory.create("car", color="red")
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Abstract Factory** | Often implemented using Factory Methods |
| **Template Method** | Factory Method often called within Template Method |
| **Prototype** | Alternative - clone instead of create |
| **Singleton** | ConcreteCreator is often a Singleton |

## 📁 Implementations

| Version | Description | Location |
|---------|-------------|----------|
| v1-basic | Classic Factory Method | [Java](./java/v1-basic/) / [Python](./python/v1-basic/) |
| v2-variant | Parameterized Factory | [Java](./java/v2-variant/) / [Python](./python/v2-variant/) |
| v3-advanced | Registry-based Factory | [Java](./java/v3-advanced/) / [Python](./python/v3-advanced/) |

---

[← Back to Factory Method](./README.md)

---

## Interview Lens

- Use when caller logic should not branch on concrete product type.
- Keep creation logic centralized; avoid scattered `new` chains.
- Follow-up ready: add a new product type without modifying existing clients.
