# 🎨 Pattern Decision Tree

A guide to help you choose the right design pattern for your problem.

---

## 🌳 Master Decision Tree

```
What's your primary concern?
│
├── Object Creation is Complex
│   └── [CREATIONAL PATTERNS] → See Section 1
│
├── Object Composition/Structure
│   └── [STRUCTURAL PATTERNS] → See Section 2
│
└── Object Communication/Behavior
    └── [BEHAVIORAL PATTERNS] → See Section 3
```

---

## 1️⃣ Creational Patterns Decision Tree

**Question: How do I create objects?**

```
Need to control object creation?
│
├── Need exactly ONE instance?
│   └── ✅ SINGLETON
│       Example: Database connection, Config manager
│       📁 Related LLD: Connection pools
│
├── Need to create objects WITHOUT specifying exact class?
│   │
│   ├── Creating single product with variants?
│   │   └── ✅ FACTORY METHOD
│   │       Example: Document creators (PDF, Word, HTML)
│   │       📁 Related LLD: VehicleFactory in Parking Lot
│   │
│   └── Creating families of related products?
│       └── ✅ ABSTRACT FACTORY
│           Example: Cross-platform UI (Windows, Mac, Linux)
│           📁 Related LLD: Theme systems
│
├── Object has MANY optional parameters (4+)?
│   └── ✅ BUILDER
│       Example: Pizza builder, SQL query builder
│       📁 Related LLD: Complex object construction
│
└── Object creation is EXPENSIVE, need to clone?
    └── ✅ PROTOTYPE
        Example: Game objects, Document templates
        📁 Related LLD: Caching templates
```

### Quick Reference

| Pattern | Problem Indicator | One-Line Solution |
|---------|-------------------|-------------------|
| **Singleton** | "only one", "global access" | Ensure single instance with global access |
| **Factory Method** | "create without specifying class" | Defer instantiation to subclasses |
| **Abstract Factory** | "families of related objects" | Create related objects without specifying classes |
| **Builder** | "many optional parameters" | Construct complex objects step-by-step |
| **Prototype** | "clone", "copy", "expensive to create" | Clone existing objects |

---

## 2️⃣ Structural Patterns Decision Tree

**Question: How do I compose objects?**

```
Need to compose or structure objects?
│
├── Need to make INCOMPATIBLE interfaces work together?
│   └── ✅ ADAPTER
│       Example: Legacy system integration, Third-party APIs
│       📁 Repo: [01-design-patterns/structural/adapter/](../../01-design-patterns/structural/adapter/)
│
├── Need to SEPARATE abstraction from implementation?
│   └── ✅ BRIDGE
│       Example: Remote control for different devices
│       📁 Repo: [01-design-patterns/structural/bridge/](../../01-design-patterns/structural/bridge/)
│
├── Need to treat INDIVIDUAL and COMPOSITE objects uniformly?
│   └── ✅ COMPOSITE
│       Example: File system (files and folders), UI components
│       📁 Repo: [01-design-patterns/structural/composite/](../../01-design-patterns/structural/composite/)
│
├── Need to ADD behavior DYNAMICALLY without inheritance?
│   └── ✅ DECORATOR
│       Example: Coffee toppings, Stream wrappers
│       📁 Repo: [01-design-patterns/structural/decorator/](../../01-design-patterns/structural/decorator/)
│
├── Need a SIMPLE interface to a complex subsystem?
│   └── ✅ FACADE
│       Example: Home theater system, Library wrapper
│       📁 Repo: [01-design-patterns/structural/facade/](../../01-design-patterns/structural/facade/)
│
├── Need to SHARE common state between many objects?
│   └── ✅ FLYWEIGHT
│       Example: Character rendering, Game objects (trees, bullets)
│       📁 Repo: [01-design-patterns/structural/flyweight/](../../01-design-patterns/structural/flyweight/)
│
└── Need to CONTROL ACCESS to another object?
    └── ✅ PROXY
        Example: Lazy loading, Access control, Logging
        📁 Repo: [01-design-patterns/structural/proxy/](../../01-design-patterns/structural/proxy/)
```

### Adapter vs Bridge vs Decorator

| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| **Adapter** | Make incompatible interfaces compatible | Working with existing code you can't change |
| **Bridge** | Separate abstraction from implementation | Need to vary both independently |
| **Decorator** | Add behavior dynamically | Adding optional features/behaviors |

### Quick Reference

| Pattern | Problem Indicator | One-Line Solution |
|---------|-------------------|-------------------|
| **Adapter** | "incompatible", "legacy", "third-party" | Convert interface to expected interface |
| **Bridge** | "vary independently", "multiple dimensions" | Separate abstraction from implementation |
| **Composite** | "tree structure", "part-whole hierarchy" | Treat leaf and composite uniformly |
| **Decorator** | "add behavior", "wrap", "dynamically" | Attach additional responsibilities |
| **Facade** | "simplify", "unified interface" | Provide simple interface to subsystem |
| **Flyweight** | "many similar objects", "memory" | Share common state |
| **Proxy** | "control access", "lazy", "remote" | Provide surrogate for another object |

---

## 3️⃣ Behavioral Patterns Decision Tree

**Question: How do objects communicate?**

```
Need to define object communication?
│
├── Need to NOTIFY multiple objects of state changes?
│   └── ✅ OBSERVER
│       Example: Event systems, Newsletter subscription
│       📁 Repo: [01-design-patterns/behavioral/observer/](../../01-design-patterns/behavioral/observer/)
│
├── Need to SELECT algorithm at runtime?
│   └── ✅ STRATEGY
│       Example: Payment methods, Sorting algorithms
│       📁 Repo: [01-design-patterns/behavioral/strategy/](../../01-design-patterns/behavioral/strategy/)
│
├── Behavior changes based on INTERNAL STATE?
│   └── ✅ STATE
│       Example: Vending machine, Document workflow
│       📁 Repo: [01-design-patterns/behavioral/state/](../../01-design-patterns/behavioral/state/)
│
├── Need to ENCAPSULATE a request as an object?
│   └── ✅ COMMAND
│       Example: Undo/redo, Task queue, Macro recording
│       📁 Repo: [01-design-patterns/behavioral/command/](../../01-design-patterns/behavioral/command/)
│
├── Need to PASS request along a chain of handlers?
│   └── ✅ CHAIN OF RESPONSIBILITY
│       Example: Middleware, Approval workflow
│       📁 Repo: [01-design-patterns/behavioral/chain-of-responsibility/](../../01-design-patterns/behavioral/chain-of-responsibility/)
│
├── Need to DEFINE skeleton of algorithm, let subclasses fill steps?
│   └── ✅ TEMPLATE METHOD
│       Example: Framework hooks, Data parsers
│       📁 Repo: [01-design-patterns/behavioral/template-method/](../../01-design-patterns/behavioral/template-method/)
│
├── Need to CENTRALIZE complex communication?
│   └── ✅ MEDIATOR
│       Example: Chat room, Air traffic control, Dialog boxes
│       📁 Repo: [01-design-patterns/behavioral/mediator/](../../01-design-patterns/behavioral/mediator/)
│
├── Need to CAPTURE and RESTORE object state?
│   └── ✅ MEMENTO
│       Example: Undo functionality, Save game, Checkpoints
│       📁 Repo: [01-design-patterns/behavioral/memento/](../../01-design-patterns/behavioral/memento/)
│
├── Need to TRAVERSE collection without exposing internals?
│   └── ✅ ITERATOR
│       Example: Custom collections, Tree traversal
│       📁 Repo: [01-design-patterns/behavioral/iterator/](../../01-design-patterns/behavioral/iterator/)
│
└── Need to ADD operations WITHOUT modifying classes?
    └── ✅ VISITOR
        Example: Tax calculator, Code analysis
        📁 Repo: [01-design-patterns/behavioral/visitor/](../../01-design-patterns/behavioral/visitor/)
```

### Strategy vs State

| Aspect | Strategy | State |
|--------|----------|-------|
| **Purpose** | Interchangeable algorithms | Behavior changes with state |
| **Who decides** | Client chooses strategy | Object changes its own state |
| **Transition** | Usually set once | Transitions between states |
| **Example** | Payment method selection | Vending machine states |

### Quick Reference

| Pattern | Problem Indicator | One-Line Solution |
|---------|-------------------|-------------------|
| **Observer** | "notify", "subscribe", "event" | Define one-to-many dependency |
| **Strategy** | "interchangeable", "algorithm", "policy" | Encapsulate algorithms, swap at runtime |
| **State** | "state machine", "behavior changes with state" | Alter behavior when state changes |
| **Command** | "undo", "queue", "history" | Encapsulate request as object |
| **Chain of Responsibility** | "chain", "pipeline", "handler" | Pass request along handlers |
| **Template Method** | "skeleton", "steps vary" | Define algorithm skeleton |
| **Mediator** | "decouple", "coordinate" | Centralize complex communication |
| **Memento** | "snapshot", "restore", "checkpoint" | Capture and restore state |
| **Iterator** | "traverse", "sequential access" | Access elements sequentially |
| **Visitor** | "operations on structure" | Add operations without modifying |

---

## 🎯 Pattern Selection by LLD Problem

| LLD Problem | Patterns Used |
|-------------|---------------|
| **Parking Lot** | Factory (vehicles), Strategy (pricing), Singleton (lot instance) |
| **Elevator System** | State (elevator states), Strategy (scheduling), Observer (floor buttons) |
| **Vending Machine** | State (machine states), Strategy (payment) |
| **Library Management** | Factory (book types), Observer (notifications) |
| **Movie Ticket Booking** | Strategy (pricing), Observer (seat availability) |
| **LRU Cache** | N/A (Data structure design) |
| **Chess Game** | Factory (pieces), Strategy (piece movement) |
| **Hotel Booking** | Strategy (room pricing), Observer (availability) |

---

## 📋 Interview Quick-Select

**When interviewer says...** → **Consider...**

| Keyword | Pattern |
|---------|---------|
| "only one instance" | Singleton |
| "create objects" | Factory, Abstract Factory, Builder |
| "clone", "copy" | Prototype |
| "wrap", "add functionality" | Decorator |
| "simplify interface" | Facade |
| "incompatible interfaces" | Adapter |
| "lazy loading" | Proxy |
| "tree structure" | Composite |
| "save memory" | Flyweight |
| "notify when changed" | Observer |
| "different algorithms" | Strategy |
| "state machine" | State |
| "undo/redo" | Command, Memento |
| "pipeline", "chain" | Chain of Responsibility |
| "traverse collection" | Iterator |
| "coordinate objects" | Mediator |

---

## 🔗 Related Resources

- [01-design-patterns/](../../01-design-patterns/) - Full pattern implementations
- [CONCEPTS.md](../../CONCEPTS.md#-design-patterns-summary) - Pattern summary
- [02-lld-projects/](../../02-lld-projects/) - Patterns in action

---

## 🚦 Interview-First Pattern Lane

If you only have time to discuss a few patterns, prioritize:
- Strategy for runtime behavior variation
- Factory Method for type-based creation
- State for explicit state transitions
- Observer for event fan-out
- Builder for complex object construction
- Decorator for optional runtime capabilities
- Facade for boundary simplification

When asked about Singleton, explain both use-case and testing trade-off.

---

*Use this tree during practice to build pattern recognition! 🌳*
