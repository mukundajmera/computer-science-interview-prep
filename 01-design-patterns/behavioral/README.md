# Behavioral Design Patterns

> Patterns that characterize ways in which classes or objects interact and distribute responsibility.

## 🎯 Overview

Behavioral patterns are concerned with algorithms and the assignment of responsibilities between objects. They describe not just patterns of objects or classes but also the patterns of communication between them.

## 📋 Pattern Catalog

| Pattern | Problem It Solves | When to Use | Java (v1/v2/v3) | Python (v1/v2/v3) | Tests (J/P) |
|---------|-------------------|-------------|---|---|---|
| [Strategy](./strategy/) | Need interchangeable algorithms | Multiple algorithms for same task | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Observer](./observer/) | Need to notify multiple objects of changes | Event systems, pub/sub | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Command](./command/) | Need to encapsulate requests as objects | Undo/redo, task queues | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [State](./state/) | Object behavior changes based on internal state | Finite state machines | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Template Method](./template-method/) | Define skeleton, let subclasses fill in | Framework hooks | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Chain of Responsibility](./chain-of-responsibility/) | Pass request along chain of handlers | Middleware, event bubbling | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Iterator](./iterator/) | Sequential access without exposing internals | Custom collections | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Mediator](./mediator/) | Reduce chaotic dependencies between objects | Chat rooms, UI components | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Memento](./memento/) | Capture and restore object state | Undo functionality | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Visitor](./visitor/) | Add operations without modifying classes | AST processing | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |
| [Interpreter](./interpreter/) | Define grammar and interpret sentences | DSLs, expression parsing | ✅/✅/✅ | ✅/✅/✅ | ✅/✅ |

## 🎓 Recommended Learning Order

### Beginner
1. **Strategy** - Cleanest introduction to behavioral patterns
2. **Observer** - Common in frameworks and reactive programming
3. **Command** - Foundation for undo/redo systems

### Intermediate
4. **Template Method** - Key framework pattern
5. **State** - Understanding state machines
6. **Iterator** - Custom collection traversal

### Advanced
7. **Chain of Responsibility** - Middleware architecture
8. **Mediator** - Complex object interactions
9. **Memento** - State snapshot management
10. **Visitor** - Double dispatch technique
11. **Interpreter** - Domain-specific languages

## 🔗 Pattern Relationships

```
Strategy ←→ State (both encapsulate behavior, different intent)
Command ←→ Memento (often used together for undo)
Observer ←→ Mediator (different coupling approaches)
Iterator + Visitor (often combined for tree traversal)
Chain of Responsibility ←→ Decorator (similar structure, different intent)
```

## 📊 Selection Guide

```
Need interchangeable algorithms? → Strategy
Need event notification? → Observer
Need undo/redo? → Command + Memento
Need state-dependent behavior? → State
Need to define algorithm skeleton? → Template Method
Need to pass requests through handlers? → Chain of Responsibility
Need custom iteration? → Iterator
Need to reduce object coupling? → Mediator
Need to add operations to class hierarchy? → Visitor
Need to interpret a language? → Interpreter
```

## 🏗️ Implementation Notes

Each pattern folder contains:
- `README.md` - Quick overview and when to use
- `java/v1-basic/` - Java implementation
- `python/v1-basic/` - Python implementation with Pythonic idioms
- language-specific `tests/` directories where available
- [Completion matrix](../COMPLETION-MATRIX.md) - Exact test and v2/v3 progression status

---

[← Back to Design Patterns](../README.md)
