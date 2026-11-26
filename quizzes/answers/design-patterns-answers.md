# 🎨 Design Patterns Quiz - Answer Key

> **Detailed explanations for all 50 questions**

---

## Section 1: Pattern Identification

### Question 1
**Answer: B) Singleton**

Singleton ensures only one instance of a class exists and provides a global access point. This is ideal for shared resources like database connections, configuration managers, or logging services.

*Why others are wrong:*
- Factory Method creates objects but doesn't limit instances
- Prototype creates copies of objects
- Builder constructs complex objects step by step

---

### Question 2
**Answer: C) Decorator**

Decorator adds new functionality by wrapping objects without modifying the original class. It follows the Open/Closed Principle - open for extension, closed for modification.

*Why others are wrong:*
- Adapter changes interface, doesn't add functionality
- Proxy controls access, doesn't add behavior
- Facade simplifies complex subsystems

---

### Question 3
**Answer: B) Abstract Factory**

Abstract Factory creates families of related objects (buttons, checkboxes, menus) that work together. Each concrete factory (WindowsFactory, MacFactory) produces platform-consistent components.

*Why others are wrong:*
- Factory Method creates single products, not families
- Builder constructs one complex object
- Prototype clones existing objects

---

### Question 4
**Answer: B) Adapter**

Adapter converts one interface to another, allowing incompatible systems to work together. It wraps the legacy XML API and exposes a JSON-compatible interface.

*Why others are wrong:*
- Bridge separates abstraction from implementation
- Facade provides simplified interface to complex system
- Proxy controls access to an object

---

### Question 5
**Answer: C) Observer**

Observer defines a one-to-many dependency where subjects notify all registered observers of state changes. Stock price changes trigger updates to all subscribed dashboards.

*Why others are wrong:*
- Mediator centralizes communication between objects
- Chain of Responsibility passes requests along a chain
- Command encapsulates requests as objects

---

### Question 6
**Answer: D) Both A and B**

Command encapsulates operations as objects with execute/undo methods. Memento captures and externalizes object state for restoration. Together they provide robust undo/redo.

*Why others are wrong:*
- Command alone can support undo but Memento adds state snapshots
- State manages object state transitions, not history

---

### Question 7
**Answer: B) State**

State allows an object to alter behavior when internal state changes. The vending machine's behavior depends on its current state (HasItems, WaitingPayment, Dispensing).

*Why others are wrong:*
- Strategy swaps algorithms, not behavior based on state
- Command encapsulates requests
- Template Method defines algorithm skeleton

---

### Question 8
**Answer: C) Builder**

Builder separates complex object construction from representation. It's ideal for objects with many optional parameters like SQL queries with optional clauses.

*Why others are wrong:*
- Factory Method creates objects without optional configuration
- Abstract Factory creates families of objects
- Prototype clones existing objects

---

### Question 9
**Answer: C) Facade**

Facade provides a unified interface to a set of interfaces in a subsystem. It hides complexity of database, cache, and logging behind a simple API.

*Why others are wrong:*
- Adapter converts interfaces
- Bridge separates abstraction from implementation
- Composite treats groups as individuals

---

### Question 10
**Answer: B) Composite**

Composite composes objects into tree structures. Files and folders form a tree where folders can contain files or other folders, all treated uniformly.

*Why others are wrong:*
- Decorator adds behavior to individual objects
- Flyweight shares common state
- Bridge separates abstraction from implementation

---

### Question 11
**Answer: C) Proxy**

Proxy provides a surrogate or placeholder for another object to control access. Virtual Proxy defers creation; Remote Proxy handles network access.

*Why others are wrong:*
- Decorator adds behavior, doesn't control access
- Adapter converts interfaces
- Facade simplifies complex systems

---

### Question 12
**Answer: B) Strategy**

Strategy defines a family of algorithms, encapsulates each one, and makes them interchangeable. Sorting algorithms can be swapped at runtime.

*Why others are wrong:*
- State changes behavior based on internal state
- Template Method defines algorithm skeleton with overridable steps
- Command encapsulates requests

---

### Question 13
**Answer: B) Iterator**

Iterator provides a way to access elements of a collection sequentially without exposing the underlying representation (array, linked list, tree).

*Why others are wrong:*
- Visitor adds operations to object structures
- Composite treats groups uniformly
- Mediator centralizes communication

---

### Question 14
**Answer: B) Flyweight**

Flyweight shares common state (intrinsic) across many objects to save memory. Character symbols are shared; position and formatting are extrinsic.

*Why others are wrong:*
- Prototype creates copies, doesn't share state
- Singleton creates single instance, not shared instances
- Object Pool recycles objects, Flyweight shares state

---

### Question 15
**Answer: C) Chain of Responsibility**

Chain of Responsibility passes requests along a chain of handlers. Each handler decides to process or pass to the next, allowing dynamic processing chains.

*Why others are wrong:*
- Command encapsulates single requests
- Mediator centralizes communication
- Observer notifies multiple objects of changes

---

## Section 2: Code Recognition

### Question 16
**Answer: B) Singleton**

Classic Singleton with private constructor, static instance, and synchronized getInstance(). The lazy initialization creates instance only when first needed.

---

### Question 17
**Answer: B) Strategy**

PaymentStrategy interface with multiple implementations (CreditCard, PayPal). ShoppingCart uses composition and can switch strategies at runtime.

---

### Question 18
**Answer: C) Decorator**

MilkDecorator wraps Coffee, implementing the same interface. getCost() adds to wrapped object's cost, allowing stacking of multiple decorators.

---

### Question 19
**Answer: B) Observer**

Subject interface with attach/detach/notify. StockMarket notifies all registered observers when stockPrice changes. Classic push-model Observer.

---

### Question 20
**Answer: B) Factory Method**

Abstract DocumentFactory with createDocument() method. Subclasses (PdfFactory, WordFactory) override to create specific document types.

---

### Question 21
**Answer: C) Builder**

Static inner Builder class with fluent setters returning 'this'. Private constructor takes Builder, ensuring object is built only through Builder.

---

### Question 22
**Answer: B) Command**

Command interface with execute() and undo(). LightOnCommand encapsulates receiver (Light) and action. RemoteControl is the Invoker.

---

### Question 23
**Answer: B) Chain of Responsibility**

Handler interface with setNext() and handle(). Each handler decides to process or delegate. AuthenticationHandler passes unhandled requests to next.

---

### Question 24
**Answer: B) State**

State interface with methods for each action. Concrete states (NoCoinState, HasCoinState) handle actions and trigger state transitions via context.

---

### Question 25
**Answer: B) Adapter**

RectangleAdapter implements new Shape interface, wraps LegacyRectangle, and translates new method signature (x, y, width, height) to legacy (x1, y1, x2, y2).

---

### Question 26
**Answer: C) Template Method**

Abstract class with final process() method defining algorithm skeleton. Abstract methods (readData, processData) are overridden by subclasses.

---

### Question 27
**Answer: C) Proxy**

ImageProxy implements Image, creates RealImage only on first display() call. This is Virtual Proxy for lazy loading of expensive resources.

---

### Question 28
**Answer: B) Abstract Factory**

GUIFactory interface creates families of related products (Button, Checkbox, Menu). Each platform factory creates consistent components.

---

### Question 29
**Answer: B) Flyweight**

CharacterFactory maintains a pool (e.g., a Map keyed by java.lang.Character values) that returns shared instances of the custom CharacterFlyweight objects. Intrinsic state (symbol) is shared; extrinsic state (fontSize, color) is passed at runtime.

---

### Question 30
**Answer: B) Memento**

TextEditor creates Memento objects containing state snapshot. Memento has private state accessible only to originator. Enables undo/restore.

---

## Section 3: Scenario Application

### Question 31
**Answer: B) Strategy**

Strategy allows swapping notification algorithms at runtime. Each method (Email, SMS, Push, Slack) is a strategy implementing NotificationStrategy interface.

*Reasoning:* Users can change notification preference without modifying NotificationService.

---

### Question 32
**Answer: B) Decorator**

Decorator wraps base Coffee and adds toppings dynamically. Each topping is a decorator that adds its price to the wrapped object's cost.

*Reasoning:* Allows unlimited combinations without class explosion.

---

### Question 33
**Answer: C) Factory Method**

Factory Method lets subclasses decide which document type to create. Each format has its own factory with specific rendering and save logic.

*Reasoning:* Adding new format requires only new factory, no changes to client code.

---

### Question 34
**Answer: C) Chain of Responsibility**

Each stage (validation, payment, inventory, shipping) is a handler that can approve, reject, or pass to next handler.

*Reasoning:* Stages can be added/removed/reordered without modifying other stages.

---

### Question 35
**Answer: B) Observer**

Trading platform (Subject) notifies dashboards, alerts, analytics (Observers) when stock price changes.

*Reasoning:* New subscribers can be added without modifying the trading platform.

---

### Question 36
**Answer: B) Adapter**

Each payment gateway has different API. Adapters wrap each gateway to implement a common PaymentGateway interface.

*Reasoning:* Application code uses uniform interface; adapters handle translation.

---

### Question 37
**Answer: C) Visitor**

Visitor allows adding new operations (save, render, AI) without modifying entity classes. Each visitor implements operation for each entity type.

*Reasoning:* Double dispatch enables operation selection based on both visitor and element types.

---

### Question 38
**Answer: B) Command**

Each device action is a Command with execute() and undo(). Remote stores command history for undo functionality.

*Reasoning:* Commands decouple remote from devices, enable macro commands and undo.

---

### Question 39
**Answer: B) State**

ATM states (CardInserted, PinEntered, Withdrawing) handle inputs differently. State transitions happen based on user actions.

*Reasoning:* Eliminates complex conditionals, each state encapsulates its behavior.

---

### Question 40
**Answer: C) Template Method**

Report generation follows same steps: gather → format → export. Template Method defines skeleton; subclasses override format-specific steps.

*Reasoning:* Common algorithm, varied implementations for each output format.

---

### Question 41
**Answer: C) Chain of Responsibility**

Log handlers (console, file, remote) form a chain. Each handler can log and/or pass to next based on log level or criteria.

*Reasoning:* Easy to add new handlers without modifying existing ones.

---

### Question 42
**Answer: B) Composite**

Shapes and groups implement same interface. Groups contain shapes or other groups, enabling recursive operations like move, resize, draw.

*Reasoning:* Uniform treatment of individual shapes and groups.

---

### Question 43
**Answer: C) Proxy**

Caching Proxy intercepts calls to real database. Checks cache first, only queries database on miss. Same interface as real service.

*Reasoning:* Proxy controls access and adds caching without modifying client or database code.

---

### Question 44
**Answer: B) Builder**

Builder allows step-by-step character creation with validation. Director can enforce valid combinations of race, class, weapon, armor.

*Reasoning:* Builder handles complex construction with validation, unlike factories.

---

### Question 45
**Answer: B) Strategy**

Each audio format has a decoding strategy. Player uses uniform interface; strategy handles format-specific decoding logic.

*Reasoning:* Strategy swaps decoding algorithms while maintaining consistent playback interface.

---

### Question 46
**Answer: C) Command + Memento**

Command provides undo capability for operations. Memento stores complete document state snapshots for restore points.

*Reasoning:* Command for granular undo; Memento for snapshots at key points.

---

### Question 47
**Answer: B) Mediator**

Chat server acts as mediator between users. Users communicate only through mediator, not directly with each other.

*Reasoning:* Mediator reduces dependencies; users only know the server, not other users.

---

### Question 48
**Answer: C) Chain of Responsibility**

Each approver (auto, manager, director) handles requests within their authority, passing higher amounts up the chain.

*Reasoning:* Dynamic chain based on amount; easy to add new approval levels.

---

### Question 49
**Answer: B) Bridge**

Bridge separates rendering abstraction (OpenGL, DirectX) from shape types (2D, 3D). Both hierarchies can evolve independently.

*Reasoning:* Avoids cartesian product explosion of shape × platform combinations.

---

### Question 50
**Answer: B) Flyweight**

Font objects (intrinsic: font family, weight) are shared. Character position, size, color (extrinsic) are passed at render time.

*Reasoning:* Dramatically reduces memory by sharing common font data across characters.

---

<p align="center">
  <b>Score Interpretation</b><br>
  45-50: Excellent | 38-44: Good | 30-37: Fair | 0-29: Review needed
</p>
