# Prototype Pattern - Theory & Interview Guide

## 📚 Core Concept

The Prototype pattern creates new objects by cloning existing instances (prototypes) rather than creating from scratch. It's useful when object creation is expensive or complex.

### Key Components

1. **Prototype (Interface)**: Declares the cloning method
2. **ConcretePrototype**: Implements cloning, copying its own state
3. **Client**: Creates new objects by requesting clones from prototypes

## 🎯 Problem It Solves

**Without Prototype:**
```java
// Creating similar objects is expensive and repetitive
Document doc1 = loadDocumentFromDatabase("template-1"); // Slow!
Document doc2 = loadDocumentFromDatabase("template-1"); // Same slow query again!
Document doc3 = loadDocumentFromDatabase("template-1"); // And again!
```

**With Prototype:**
```java
Document prototype = loadDocumentFromDatabase("template-1"); // Load once
Document doc1 = prototype.clone(); // Fast clone
Document doc2 = prototype.clone(); // Fast clone
Document doc3 = prototype.clone(); // Fast clone
```

## 🏗️ Structure

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌─────────────────┐          ┌─────────────────────┐      │
│  │ «interface»     │          │      Client         │      │
│  │   Prototype     │◀─────────│                     │      │
│  ├─────────────────┤  uses    ├─────────────────────┤      │
│  │ + clone()       │          │ + operation()       │      │
│  └────────┬────────┘          └─────────────────────┘      │
│           │                                                 │
│           │ implements                                      │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ConcretePrototype│                                        │
│  ├─────────────────┤                                        │
│  │ - field1        │                                        │
│  │ - field2        │                                        │
│  │ + clone()       │ ─── returns copy of self               │
│  └─────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✅ When to Use

1. **Expensive object creation** - DB queries, file parsing
2. **Many similar objects needed** - Game sprites, document templates
3. **Avoiding constructor complexity** - Object with complex initialization
4. **Hiding concrete classes** - Factory returns cloned prototypes
5. **Runtime configuration** - Objects configured at runtime, then cloned

## ❌ When NOT to Use

1. Simple objects that are easy to construct
2. Objects with many circular references (complex deep copy)
3. When objects should not be modified after creation

## 🎤 Interview Q&A

### Q1: Shallow Copy vs Deep Copy?

**A:**
| Shallow Copy | Deep Copy |
|--------------|-----------|
| Copies primitive values | Copies everything |
| References point to same objects | Creates new copies of referenced objects |
| Fast, simple | Slower, complex |
| Changes to nested objects affect both copies | Completely independent copies |

### Q2: How does Java's `clone()` work?

**A:** 
1. Class must implement `Cloneable` interface
2. Override `clone()` method
3. Call `super.clone()` for shallow copy
4. Manually clone mutable objects for deep copy

```java
@Override
public Object clone() throws CloneNotSupportedException {
    MyClass copy = (MyClass) super.clone(); // Shallow
    copy.list = new ArrayList<>(this.list); // Deep for list
    return copy;
}
```

### Q3: How does Python handle cloning?

**A:** Python's `copy` module provides:
- `copy.copy()` - Shallow copy
- `copy.deepcopy()` - Deep copy (handles circular refs)

Or implement `__copy__()` and `__deepcopy__()` methods.

### Q4: Prototype vs Factory Method?

**A:**
| Prototype | Factory Method |
|-----------|----------------|
| Clone existing objects | Create new from scratch |
| Runtime prototypes | Compile-time class hierarchy |
| Good for expensive creation | Good for type selection |
| No need for parallel class hierarchy | Requires creator subclasses |

### Q5: What's a Prototype Registry?

**A:** A central registry that stores prototypes by name/key. Clients request clones by key:
```java
PrototypeRegistry.register("circle", new Circle(10));
Shape shape = PrototypeRegistry.getClone("circle");
```

## 💻 Code Patterns

### Java - Cloneable
```java
public class Shape implements Cloneable {
    private String color;
    
    @Override
    public Shape clone() {
        try {
            return (Shape) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }
}
```

### Java - Copy Constructor (Preferred)
```java
public class Shape {
    private String color;
    
    // Copy constructor
    public Shape(Shape source) {
        this.color = source.color;
    }
    
    public Shape clone() {
        return new Shape(this);
    }
}
```

### Python - Copy Module
```python
import copy

class Shape:
    def __init__(self, color):
        self.color = color
    
    def clone(self):
        return copy.deepcopy(self)
```

### Python - Custom Clone
```python
class Shape:
    def __init__(self, color):
        self.color = color
    
    def __copy__(self):
        return Shape(self.color)
    
    def __deepcopy__(self, memo):
        return Shape(copy.deepcopy(self.color, memo))
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Factory Method** | Can use Prototype internally |
| **Abstract Factory** | Can store prototypes instead of factories |
| **Composite** | Clone complex composites |
| **Decorator** | Clone decorated objects |

## 📁 Implementations

| Version | Description | Location |
|---------|-------------|----------|
| v1-basic | Shape cloning with registry | [Java](./java/v1-basic/) / [Python](./python/v1-basic/) |

---

[← Back to Prototype](./README.md)
