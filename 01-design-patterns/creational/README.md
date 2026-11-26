# Creational Design Patterns

> Patterns that deal with object creation mechanisms, trying to create objects in a manner suitable to the situation.

## 🎯 Overview

Creational patterns abstract the instantiation process. They help make a system independent of how its objects are created, composed, and represented.

## 📋 Pattern Catalog

| Pattern | Problem It Solves | When to Use | Java (v1/v2/v3) | Python (v1/v2/v3) | Tests (J/P) |
|---------|-------------------|-------------|---|---|---|
| [Singleton](./singleton/) | Need exactly one instance globally | Config, logging, pools | ✅/✅/✅ | ✅/✅/✅ | ❌/✅ |
| [Factory Method](./factory-method/) | Creating objects without specifying exact class | Plugin systems, frameworks | ✅/✅/✅ | ✅/✅/✅ | ❌/✅ |
| [Abstract Factory](./abstract-factory/) | Creating families of related objects | Cross-platform UI, themes | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Builder](./builder/) | Complex object with many optional parameters | Objects with 4+ optional params | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Prototype](./prototype/) | Expensive object creation, need cloning | Object templates, caching | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |

## 🎓 Recommended Learning Order

### Beginner
1. **Singleton** - Simplest creational pattern
2. **Factory Method** - Foundation for other factory patterns

### Intermediate
3. **Builder** - Common in modern APIs
4. **Prototype** - Cloning objects efficiently

### Advanced
5. **Abstract Factory** - Creating product families

## 🔗 Pattern Relationships

```
Singleton → often used with other creational patterns

Abstract Factory → uses Factory Method internally
                → products often created via Prototype

Builder → may use Abstract Factory to build parts
       → often implemented as Singleton

Factory Method → can evolve into Abstract Factory
              → similar intent as Prototype

Prototype → alternative to Factory Method subclassing
```

## 📊 Selection Guide

```
Need exactly one instance?
└── Use SINGLETON

Need to create objects without specifying exact class?
└── Many product types? → ABSTRACT FACTORY
└── One product type? → FACTORY METHOD

Need step-by-step construction?
└── Use BUILDER

Need to copy existing objects?
└── Use PROTOTYPE
```

## 🏗️ Implementation Notes

Each pattern folder contains:
- `README.md` - Overview, class diagram, and when to use
- `java/v1-basic/` - Java implementation
- `python/v1-basic/` - Python implementation
- [Completion matrix](../COMPLETION-MATRIX.md) - Test and v2/v3 progression status

---

[← Back to Design Patterns](../README.md)
