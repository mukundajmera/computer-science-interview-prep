# Visitor Pattern - Theory & Interview Guide

## 📚 Core Concept

The Visitor pattern lets you separate algorithms from the objects on which they operate. It allows adding new operations without modifying the classes.

### Key Components

1. **Visitor (Interface)**: Declares visit methods for each element type
2. **ConcreteVisitor**: Implements operations for each element type
3. **Element (Interface)**: Declares accept(Visitor) method
4. **ConcreteElement**: Implements accept by calling visitor.visit(this)

## 🎯 Problem It Solves

**Without Visitor:**
```java
// Adding new operation requires modifying all element classes
class Circle {
    double area() { ... }
    void draw() { ... }
    String toSVG() { ... }      // New operation - must add to all shapes!
    String toJSON() { ... }     // Another operation - modify all again!
}
```

**With Visitor:**
```java
// New operations without touching element classes
interface ShapeVisitor {
    void visit(Circle c);
    void visit(Rectangle r);
}

class SVGExportVisitor implements ShapeVisitor { ... }
class JSONExportVisitor implements ShapeVisitor { ... }  // New!
class AreaCalculatorVisitor implements ShapeVisitor { ... }  // New!
```

## 🏗️ Double Dispatch Mechanism

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  1. Client calls:         element.accept(visitor)          │
│                                  │                         │
│                                  ▼                         │
│  2. Element calls:        visitor.visit(this)              │
│     (passes itself)              │                         │
│                                  ▼                         │
│  3. Visitor knows:        - concrete element type          │
│                           - what operation to perform      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## ✅ When to Use

1. **Many unrelated operations** on object structure
2. **Element classes rarely change** (stable hierarchy)
3. **Operations frequently added**
4. Examples: Compilers (AST visitors), document export, permissions

## ❌ When NOT to Use

1. Element hierarchy changes frequently (breaks all visitors)
2. Elements have complex private state (encapsulation issues)
3. Small number of operations

## 🎤 Interview Q&A

### Q1: What is Double Dispatch?

**A:** Determining method at runtime based on TWO objects:
1. **First dispatch**: `element.accept(visitor)` - selects element type
2. **Second dispatch**: `visitor.visit(this)` - selects visitor operation

Java/Python only support single dispatch, so Visitor pattern simulates double dispatch.

### Q2: Visitor vs Iterator?

**A:**
| Visitor | Iterator |
|---------|----------|
| Adds operations | Navigates structure |
| Type-specific behavior | Uniform access |
| Complex operations | Simple traversal |

Often used together: Iterator traverses, Visitor operates.

### Q3: How do you handle new element types?

**A:** This is the weakness! Adding new element type requires:
1. Add new visit(NewElement) to Visitor interface
2. Implement in ALL concrete visitors

### Q4: Acyclic Visitor?

**A:** Alternative that handles new elements better:
- Use empty marker interface instead of overloaded visits
- Cast to specific visitor if available
- More flexible, but loses compile-time checking

## 💻 Code Patterns

### Java
```java
interface Shape {
    void accept(ShapeVisitor visitor);
}

class Circle implements Shape {
    double radius;
    
    public void accept(ShapeVisitor visitor) {
        visitor.visit(this);  // Pass self to visitor
    }
}

interface ShapeVisitor {
    void visit(Circle circle);
    void visit(Rectangle rectangle);
}

class AreaCalculator implements ShapeVisitor {
    private double totalArea = 0;
    
    public void visit(Circle c) {
        totalArea += Math.PI * c.radius * c.radius;
    }
    
    public void visit(Rectangle r) {
        totalArea += r.width * r.height;
    }
}
```

### Python
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def accept(self, visitor: 'ShapeVisitor') -> None:
        pass

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius
    
    def accept(self, visitor: 'ShapeVisitor') -> None:
        visitor.visit_circle(self)

class ShapeVisitor(ABC):
    @abstractmethod
    def visit_circle(self, circle: Circle) -> None:
        pass
    
    @abstractmethod
    def visit_rectangle(self, rectangle: 'Rectangle') -> None:
        pass

class AreaCalculator(ShapeVisitor):
    def __init__(self):
        self.total_area = 0.0
    
    def visit_circle(self, circle: Circle) -> None:
        self.total_area += 3.14159 * circle.radius ** 2
    
    def visit_rectangle(self, rectangle) -> None:
        self.total_area += rectangle.width * rectangle.height
```

### Python Alternative - Single Dispatch
```python
from functools import singledispatchmethod

class ShapeVisitor:
    @singledispatchmethod
    def visit(self, shape):
        raise NotImplementedError(f"Cannot visit {type(shape)}")
    
    @visit.register
    def _(self, circle: Circle):
        return 3.14159 * circle.radius ** 2
    
    @visit.register
    def _(self, rectangle: Rectangle):
        return rectangle.width * rectangle.height
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Composite** | Visitor often visits composites |
| **Iterator** | Traverses structure for visitor |
| **Interpreter** | Visitor can interpret expressions |

---

[← Back to Visitor](./README.md)
