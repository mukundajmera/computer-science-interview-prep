# Structural Design Patterns

Structural patterns explain how to assemble objects and classes into larger structures while keeping these structures flexible and efficient.

---

## 📋 Pattern Index

| Pattern | Description | Java (v1/v2/v3) | Python (v1/v2/v3) | Tests (J/P) |
|---------|-------------|---|---|---|
| [Adapter](./adapter/) | Convert interface of a class into another interface clients expect | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Bridge](./bridge/) | Separate abstraction from implementation | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Composite](./composite/) | Compose objects into tree structures | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Decorator](./decorator/) | Add responsibilities to objects dynamically | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Facade](./facade/) | Provide unified interface to subsystem | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Flyweight](./flyweight/) | Share objects to support large quantities | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Proxy](./proxy/) | Provide surrogate to control access | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |

---

## 🎯 Pattern Selection Guide

```
Need to work with incompatible interfaces?
└── Use ADAPTER

Need to separate abstraction from implementation?
└── Use BRIDGE

Need to treat individual objects and compositions uniformly?
└── Use COMPOSITE

Need to add behavior without modifying classes?
└── Use DECORATOR

Need to simplify a complex subsystem?
└── Use FACADE

Need to share objects to save memory?
└── Use FLYWEIGHT

Need to control access to an object?
└── Use PROXY
```

---

## 📊 Comparison Table

| Pattern | Intent | Relationship |
|---------|--------|--------------|
| Adapter | Make incompatible interfaces work together | Wraps ONE object |
| Bridge | Separate abstraction from implementation | Connects TWO hierarchies |
| Composite | Tree structures, uniform treatment | Contains MANY objects |
| Decorator | Add behavior dynamically | Wraps ONE object, stacks |
| Facade | Simplify subsystem | Wraps MANY objects |
| Flyweight | Share common state | Pool of shared objects |
| Proxy | Control access | Same interface as real |

---

## 🔗 Quick Links

Each pattern folder contains:
- `README.md` - Overview and structure
- `java/v1-basic/` - Java implementation
- `python/v1-basic/` - Python implementation
- language-specific `tests/` directories where available
- [Completion matrix](../COMPLETION-MATRIX.md) - Exact test and v2/v3 progression status
