# Abstract Factory Pattern - Theory & Interview Guide

## 📚 Core Concept

The Abstract Factory pattern provides an interface for creating families of related or dependent objects without specifying their concrete classes.

### Key Components

1. **AbstractFactory**: Declares creation methods for each abstract product
2. **ConcreteFactory**: Implements creation methods for a specific family
3. **AbstractProduct**: Interface for a type of product
4. **ConcreteProduct**: Specific implementation created by a ConcreteFactory

## 🎯 Problem It Solves

**Without Abstract Factory:**
```java
// Client must know about platform-specific classes
if (platform.equals("windows")) {
    button = new WindowsButton();
    checkbox = new WindowsCheckbox();
    menu = new WindowsMenu();
} else if (platform.equals("mac")) {
    button = new MacButton();
    checkbox = new MacCheckbox();
    menu = new MacMenu();
}
// Must update this for every new platform!
```

**With Abstract Factory:**
```java
UIFactory factory = getFactoryForPlatform(platform);
Button button = factory.createButton();     // Platform-specific
Checkbox checkbox = factory.createCheckbox(); // Consistent family
```

## 🏗️ UML Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌─────────────────┐                  ┌─────────────────────┐  │
│  │ «interface»     │                  │ «interface»         │  │
│  │ AbstractFactory │                  │ AbstractProductA    │  │
│  ├─────────────────┤                  └──────────┬──────────┘  │
│  │+createProductA()│                             │             │
│  │+createProductB()│         ┌───────────────────┼───────────┐ │
│  └────────┬────────┘         │                   │           │ │
│           │            ┌─────┴─────┐       ┌─────┴─────┐     │ │
│  ┌────────┴────────┐   │ProductA1  │       │ProductA2  │     │ │
│  │                 │   └───────────┘       └───────────┘     │ │
│  ├────────┬────────┤                                          │ │
│  │Factory1│Factory2│   ┌──────────────────────────────────┐  │ │
│  └────┬───┴────┬───┘   │ «interface» AbstractProductB    │  │ │
│       │        │       └──────────────┬───────────────────┘  │ │
│   creates   creates          ┌────────┴────────┐              │ │
│       │        │        ┌────┴────┐       ┌────┴────┐        │ │
│       ▼        ▼        │ProductB1│       │ProductB2│        │ │
│  ProductA1  ProductA2   └─────────┘       └─────────┘        │ │
│  ProductB1  ProductB2                                         │ │
└─────────────────────────────────────────────────────────────────┘
```

## ✅ When to Use

1. **Families of related products** that must be used together
2. **Platform independence** (Windows/Mac/Linux UI)
3. **Consistency** across related products
4. **Decoupling** client from concrete product classes

## ❌ When NOT to Use

1. Products aren't related or dependent
2. Single product type (use Factory Method instead)
3. Simple application without system variants

## 🎤 Interview Q&A

### Q1: Abstract Factory vs Factory Method?

**A:**
| Abstract Factory | Factory Method |
|------------------|----------------|
| Creates **families** of products | Creates **one** product |
| Uses composition (has factory) | Uses inheritance (is factory) |
| Multiple creation methods | Single creation method |
| Runtime family selection | Subclass-based selection |

### Q2: Real-world examples?

**A:**
- **UI Toolkits**: Platform-specific widgets (Windows, Mac, Linux)
- **Database Drivers**: MySQL, PostgreSQL, MongoDB connection families
- **Document Generators**: PDF, HTML, Word document components
- **Game Development**: Themed game assets (medieval, futuristic)

### Q3: How does it enforce consistency?

**A:** A concrete factory only produces products from its family. If you have MacFactory, it only creates MacButton, MacCheckbox, etc. You can't accidentally mix Windows and Mac components.

### Q4: How do you select the right factory?

**A:** Common approaches:
1. **Configuration/Environment**: `if (os.equals("mac")) return new MacFactory()`
2. **Dependency Injection**: Factory provided at startup
3. **Factory of Factories**: Another factory decides
4. **Registry**: Map platform → factory

## 💻 Code Patterns

### Java
```java
interface GUIFactory {
    Button createButton();
    Checkbox createCheckbox();
}

class MacFactory implements GUIFactory {
    public Button createButton() { return new MacButton(); }
    public Checkbox createCheckbox() { return new MacCheckbox(); }
}

// Usage
GUIFactory factory = getFactory();
Button btn = factory.createButton();
```

### Python
```python
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Factory Method** | Abstract Factory often uses Factory Methods |
| **Singleton** | Factories are often Singletons |
| **Prototype** | Alternative - clone prototypes |
| **Builder** | Can build complex products |

## 📁 Implementations

| Version | Description | Location |
|---------|-------------|----------|
| v1-basic | UI Factory example | [Java](./java/v1-basic/) / [Python](./python/v1-basic/) |

---

[← Back to Abstract Factory](./README.md)
