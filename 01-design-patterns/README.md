# 🎨 Design Patterns

A comprehensive catalog of Gang of Four (GoF) design patterns with implementations in Java and Python.

Coverage note: all 23 GoF patterns currently have theory plus Java/Python `v1-basic` examples, and the completion matrix tracks which patterns also have source-backed v2/v3 progression and tests. Use the [completion matrix](./COMPLETION-MATRIX.md) for exact status.

---

## 📚 Pattern Categories

| Category | Count | Description |
|----------|-------|-------------|
| [Creational](./creational/) | 5 | Object creation mechanisms |
| [Structural](./structural/) | 7 | Object composition and relationships |
| [Behavioral](./behavioral/) | 11 | Object communication and responsibility |

---

## 📋 Pattern Catalog

### Creational Patterns
*Control how objects are created*

| Pattern | Problem It Solves | When to Use | Coverage |
|---------|-------------------|-------------|----------|
| [Singleton](./creational/singleton/) | Need exactly one instance globally | Config managers, Connection pools | V1-V3 |
| [Factory Method](./creational/factory-method/) | Creating objects without specifying exact class | Multiple product variants, Plugin systems | V1-V3 |
| [Abstract Factory](./creational/abstract-factory/) | Creating families of related objects | Cross-platform UI, Themed components | V1 + theory |
| [Builder](./creational/builder/) | Complex object with many optional parameters | Objects with 4+ optional params | V1 + theory |
| [Prototype](./creational/prototype/) | Expensive object creation, need cloning | Caching, Object templates | V1 + theory |

### Structural Patterns
*Compose objects into larger structures*

| Pattern | Problem It Solves | When to Use | Coverage |
|---------|-------------------|-------------|----------|
| [Adapter](./structural/adapter/) | Incompatible interfaces need to work together | Legacy integration, Third-party APIs | V1-V3 + tests |
| [Bridge](./structural/bridge/) | Decouple abstraction from implementation | Multi-platform support | V1-V3 + tests |
| [Composite](./structural/composite/) | Treat individual objects and compositions uniformly | Tree structures, File systems | V1-V3 + tests |
| [Decorator](./structural/decorator/) | Add behavior dynamically without inheritance | Feature toggles, Middleware | V1-V3 + tests |
| [Facade](./structural/facade/) | Provide simple interface to complex subsystem | Library wrappers, API simplification | V1-V3 + tests |
| [Flyweight](./structural/flyweight/) | Share common state to save memory | Large object counts, Caching | V1-V3 + tests |
| [Proxy](./structural/proxy/) | Control access to another object | Lazy loading, Access control, Logging | V1-V3 + tests |

### Behavioral Patterns
*Define how objects communicate*

| Pattern | Problem It Solves | When to Use | Coverage |
|---------|-------------------|-------------|----------|
| [Chain of Responsibility](./behavioral/chain-of-responsibility/) | Multiple handlers for a request | Request pipelines, Middleware | V1 + theory |
| [Command](./behavioral/command/) | Encapsulate actions as objects | Undo/redo, Task queuing | V1-V3 + tests |
| [Interpreter](./behavioral/interpreter/) | Define grammar and interpret sentences | DSLs, expression parsing | V1 + theory |
| [Iterator](./behavioral/iterator/) | Traverse collection without exposing internals | Custom collections | V1 + theory |
| [Mediator](./behavioral/mediator/) | Reduce coupling between communicating objects | Chat rooms, Event coordinators | V1 + theory |
| [Memento](./behavioral/memento/) | Capture and restore object state | Undo functionality, Snapshots | V1-V3 + tests |
| [Observer](./behavioral/observer/) | Notify dependents of state changes | Event systems, Pub/sub | V1-V3 + tests |
| [State](./behavioral/state/) | Object behavior changes with internal state | State machines, Workflows | V1-V3 + tests |
| [Strategy](./behavioral/strategy/) | Interchangeable algorithms | Payment methods, Sorting | V1-V3 + tests |
| [Template Method](./behavioral/template-method/) | Define algorithm skeleton, let subclasses fill steps | Framework hooks | V1 + theory |
| [Visitor](./behavioral/visitor/) | Add operations without modifying classes | Report generation, Serialization | V1 + theory |

---

## 🎯 Recommended Learning Order

For optimal understanding, follow this sequence:

### Phase 1: Foundation (Week 1)
```
Singleton → Factory Method → Strategy → Observer
```
These are the most commonly used and asked patterns.

### Phase 2: Intermediate (Week 2)
```
Builder → Decorator → Adapter → Command
```
Build on fundamentals with structural and behavioral patterns.

### Phase 3: Advanced (Week 3-4)
```
Abstract Factory → Facade → State → Chain of Responsibility → Template Method
```
Complete your knowledge with remaining patterns.

### Phase 4: Specialized (Optional)
```
Flyweight → Proxy → Memento → Visitor → Bridge → Composite → Iterator → Mediator
```
For deep understanding and specific use cases.

---

## 📖 Each Pattern Includes

Every pattern document contains:

1. **📚 Theory**
   - Problem & Motivation
   - Solution approach
   - Structure (UML diagram)
   - Participants

2. **🏗️ Implementation**
   - Java `v1-basic` example
   - Python `v1-basic` example
   - Tests where listed in the completion matrix

3. **🎯 Real-World Examples**
   - Where it's used in popular frameworks
   - Common interview scenarios

4. **❓ Interview Q&A**
   - Frequently asked questions
   - Common variations
   - Comparison with similar patterns

5. **🔗 Cross-References**
   - Related patterns
   - Usage in LLD projects

---

## 🎯 Interview Usage Guidance

All 23 GoF patterns are covered in this repository. In LLD interviews, prioritize clear pattern-fit over pattern count:

- Start from change pressure in requirements, then choose pattern.
- Prefer 1-3 well-justified patterns over broad pattern stacking.
- Explain trade-offs and when a simpler design is enough.

Most frequent interview patterns in this repo:
- [Factory Method](./creational/factory-method/)
- [Builder](./creational/builder/)
- [Strategy](./behavioral/strategy/)
- [State](./behavioral/state/)
- [Observer](./behavioral/observer/)
- [Decorator](./structural/decorator/)
- [Facade](./structural/facade/)

---

## 🔗 Pattern Relationships

```
                        ┌──────────────┐
                        │   Abstract   │
                        │   Factory    │
                        └──────┬───────┘
                               │ uses
                               ▼
┌──────────┐         ┌──────────────┐
│ Prototype│◄────────│   Factory    │
└──────────┘ similar │    Method    │
                     └──────────────┘
                               │
                               │ often combined with
                               ▼
┌──────────┐         ┌──────────────┐
│ Singleton│────────►│    Builder   │
└──────────┘         └──────────────┘

┌──────────┐         ┌──────────────┐
│  Adapter │         │   Decorator  │
└────┬─────┘         └──────┬───────┘
     │ similar              │ similar
     ▼                      ▼
┌──────────┐         ┌──────────────┐
│   Proxy  │         │    Bridge    │
└──────────┘         └──────────────┘

┌──────────┐         ┌──────────────┐
│ Strategy │────────►│    State     │
└──────────┘ similar └──────────────┘
```

---

## ✅ Coverage Checklist

This checklist tracks theory plus dual-language `v1-basic` coverage. It does not imply v2/v3 progression or test coverage; see the [completion matrix](./COMPLETION-MATRIX.md) for that.

### Creational
- [x] Singleton
- [x] Factory Method
- [x] Abstract Factory
- [x] Builder
- [x] Prototype

### Structural
- [x] Adapter
- [x] Bridge
- [x] Composite
- [x] Decorator
- [x] Facade
- [x] Flyweight
- [x] Proxy

### Behavioral
- [x] Chain of Responsibility
- [x] Command
- [x] Iterator
- [x] Mediator
- [x] Memento
- [x] Observer
- [x] State
- [x] Strategy
- [x] Template Method
- [x] Visitor
- [x] Interpreter

---

## 🧭 Section Navigation

| | |
|---|---|
| **Prerequisites** | [Theory & Fundamentals ←](../00-theory/) — OOP, SOLID principles |
| **What's Next** | [LLD Projects →](../02-lld-projects/) — apply patterns to real problems |
| **Related** | [Flashcards](../flashcards/design-patterns.md) · [Quiz](../quizzes/design-patterns-quiz.md) |

---

## 📌 Study Tips

1. **Understand the problem first** - Know what problem the pattern solves before memorizing structure
2. **Draw the UML** - Sketching helps solidify understanding
3. **Code it yourself** - Don't just read, implement from scratch
4. **Find real examples** - Look for patterns in code you use daily
5. **Compare similar patterns** - Understand subtle differences

---

*🏗️ Explore each pattern folder above for Java and Python implementations.*


---

## 💻 Running on Windows

If you encounter `UnicodeEncodeError` when running Python demos on Windows default command prompt, you can force Python to use UTF-8 by setting an environment variable before running your scripts:

```cmd
set PYTHONIOENCODING=utf-8
python observer_demo.py
```
Or in PowerShell:
```powershell
$env:PYTHONIOENCODING="utf-8"
python observer_demo.py
```
