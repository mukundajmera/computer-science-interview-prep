# 📋 LLD Interview Checklist

A step-by-step framework for acing Low-Level Design interviews.

---

## 📊 Overview

| Phase | Time (45-60 min) | Focus |
|-------|------------------|-------|
| 1. Requirements | 5 min | Clarify scope and constraints |
| 2. Core Entities | 5 min | Identify classes/objects |
| 3. Relationships | 5 min | Map entity connections |
| 4. Design Patterns | 5 min | Choose applicable patterns |
| 5. Class Design | 15-20 min | Attributes, methods, responsibilities |
| 6. Edge Cases | 5-10 min | Validation, errors, concurrency |
| 7. Complexity Analysis | 5 min | Time/space, optimizations |

---

## 1️⃣ Clarify Requirements (5 min)

### What to Do
- **Listen carefully** to the problem statement
- **Take notes** on key requirements
- **Ask clarifying questions** before designing

### Questions to Ask

#### Functional Requirements
- "What are the core features we need to support?"
- "What actions can users perform?"
- "What are the inputs and outputs?"
- "Should we handle [specific feature]?"

#### Non-Functional Requirements
- "Do we need to handle concurrent access?"
- "What's the expected scale?"
- "Do we need persistence?"
- "Are there any performance requirements?"

#### Scope Boundaries
- "Should I focus on [specific area] or the entire system?"
- "Are we including [optional feature]?"
- "What's out of scope for this discussion?"

### Example Dialogue

**Problem:** Design a Parking Lot System

> **You:** "Before I start designing, I have a few clarifying questions. First, should the parking lot support multiple floors?"
>
> **Interviewer:** "Yes, multiple floors with different spot types."
>
> **You:** "Should we handle payment and ticketing, or just the parking management?"
>
> **Interviewer:** "Include ticketing and basic payment calculation."
>
> **You:** "Any concurrency concerns? Multiple cars entering simultaneously?"
>
> **Interviewer:** "Yes, handle concurrent parking requests."

### ✅ Checklist
- [ ] Understood core functionality
- [ ] Clarified scope boundaries
- [ ] Noted non-functional requirements
- [ ] Asked about edge cases upfront

### ⚠️ Red Flags to Avoid
- ❌ Jumping straight into design without questions
- ❌ Assuming requirements without confirming
- ❌ Spending too long on this phase

---

## 2️⃣ Identify Core Entities (5 min)

### What to Do
- **Find the nouns** in the problem statement
- **List candidate entities** (classes/objects)
- **Filter to core entities** needed for MVP

### Technique: Noun Extraction

Read the problem statement and underline nouns:

> "Design a **parking lot** system where **vehicles** can park in **spots**. 
> The **lot** has multiple **floors** and different **spot** sizes for different **vehicles**.
> Generate **tickets** and calculate **fees**."

**Entities identified:**
- ParkingLot
- Floor
- ParkingSpot
- Vehicle (Car, Motorcycle, Truck)
- Ticket
- Fee/Payment

### For Each Entity, Note:

| Entity | Attributes | Behaviors |
|--------|------------|-----------|
| ParkingSpot | id, size, isOccupied | park(), unpark(), isAvailable() |
| Vehicle | licensePlate, type | getType() |
| Ticket | id, entryTime, spot | calculateFee() |

### What to Say

> "Based on the requirements, I've identified the following core entities: ParkingLot, Floor, ParkingSpot, Vehicle with subtypes, and Ticket. Let me describe what each one represents..."

### ✅ Checklist
- [ ] Identified all core entities
- [ ] Noted key attributes for each
- [ ] Noted key behaviors for each
- [ ] Confirmed with interviewer

---

## 3️⃣ Define Relationships (5 min)

### What to Do
- Map how entities connect
- Identify relationship types
- Draw a simple hierarchy

### Relationship Types

| Type | Symbol | Description | Example |
|------|--------|-------------|---------|
| **Composition** | ◆ | Strong ownership (part-of) | ParkingLot HAS Floors |
| **Aggregation** | ◇ | Weak ownership (has-a) | ParkingSpot references Vehicle |
| **Inheritance** | △ | Is-a relationship | Car IS-A Vehicle |
| **Association** | — | Uses or knows about | Ticket references ParkingSpot |

### Draw the Hierarchy

```
ParkingLot (Singleton)
├── Floor (1..n) [Composition]
│   └── ParkingSpot (1..n) [Composition]
│       └── Vehicle (0..1) [Aggregation - vehicle can leave]
└── EntryPanel
    └── generates → Ticket [Association]
        └── references → ParkingSpot [Association]
```

### Relationship Questions

| Question | Type |
|----------|------|
| "Can child exist without parent?" | Composition (No) vs Aggregation (Yes) |
| "Is child a type of parent?" | Inheritance |
| "Does object just use another?" | Association |

### What to Say

> "The relationships here are: ParkingLot contains Floors through composition - floors can't exist without the lot. Each Floor contains ParkingSpots. When a vehicle parks, the spot references it through aggregation since the vehicle existed before parking."

### ✅ Checklist
- [ ] Mapped all entity relationships
- [ ] Identified composition vs aggregation
- [ ] Identified inheritance hierarchies
- [ ] Drew simple diagram

---

## 4️⃣ Choose Design Patterns (5 min)

### What to Do
- Match problems to patterns
- Justify pattern choices
- Don't force patterns where not needed

### Pattern Quick Reference

| If You Need To... | Consider... |
|-------------------|-------------|
| Ensure only one instance | **Singleton** |
| Create objects without specifying class | **Factory** |
| Build complex objects step-by-step | **Builder** |
| Change behavior based on state | **State** |
| Select algorithm at runtime | **Strategy** |
| Notify multiple objects of changes | **Observer** |
| Add behavior dynamically | **Decorator** |
| Control access to object | **Proxy** |

### Common LLD Pattern Combinations

| Problem | Patterns |
|---------|----------|
| **Parking Lot** | Factory (vehicles), Strategy (pricing), Singleton (lot) |
| **Elevator** | State (elevator states), Strategy (scheduling), Observer (floor buttons) |
| **Vending Machine** | State (machine states), Strategy (payment) |
| **Library** | Factory (books), Observer (notifications) |
| **Hotel Booking** | Strategy (pricing), Factory (rooms) |

### What to Say

> "For this problem, I'll use the Factory pattern to create different vehicle types without exposing creation logic. I'll also use Strategy pattern for pricing calculations - this allows us to easily add new pricing strategies like hourly, daily, or membership rates."

### When NOT to Use Patterns

- Problem is simple enough without them
- Pattern adds unnecessary complexity
- You can't justify why it helps

> "I considered using [pattern], but it would add complexity without much benefit here since [reason]."

### ✅ Checklist
- [ ] Identified applicable patterns
- [ ] Justified each pattern choice
- [ ] Didn't force unnecessary patterns
- [ ] Mentioned where patterns apply

---

## 5️⃣ Design Classes (15-20 min)

### What to Do
- Define class structure
- Specify attributes (private)
- Specify methods (public interface)
- Apply SOLID principles

### Class Design Template

```java
public class ParkingSpot {
    // Attributes (private)
    private String spotId;
    private SpotSize size;
    private Vehicle currentVehicle;
    private boolean isAvailable;
    
    // Constructor
    public ParkingSpot(String spotId, SpotSize size) {
        this.spotId = spotId;
        this.size = size;
        this.isAvailable = true;
    }
    
    // Behaviors (public)
    public boolean canFitVehicle(Vehicle vehicle) {
        return isAvailable && this.size.canAccommodate(vehicle.getType().getRequiredSize());
    }
    
    public void parkVehicle(Vehicle vehicle) {
        if (!canFitVehicle(vehicle)) {
            throw new IllegalStateException("Cannot park this vehicle");
        }
        this.currentVehicle = vehicle;
        this.isAvailable = false;
    }
    
    public void removeVehicle() {
        this.currentVehicle = null;
        this.isAvailable = true;
    }
    
    // Getters as needed
    public boolean isAvailable() { return isAvailable; }
}
```

### SOLID Checklist

| Principle | Check |
|-----------|-------|
| **S - Single Responsibility** | Does class have one reason to change? |
| **O - Open/Closed** | Can we extend without modifying? |
| **L - Liskov Substitution** | Can subtypes replace base types? |
| **I - Interface Segregation** | Are interfaces focused? |
| **D - Dependency Inversion** | Do we depend on abstractions? |

### Key Classes to Cover

1. **Main entity class** (ParkingSpot, Elevator)
2. **Container class** (ParkingLot, Building)
3. **Supporting classes** (Ticket, Payment)
4. **Interfaces** (for patterns)
5. **Enums** (for fixed options)

### What to Say

> "For the ParkingSpot class, I'm keeping attributes private for encapsulation. The canFitVehicle method checks both availability and size compatibility. Note that I'm throwing an exception for invalid operations rather than silently failing."

### ✅ Checklist
- [ ] Core classes designed
- [ ] Attributes are private
- [ ] Methods have clear responsibilities
- [ ] SOLID principles applied
- [ ] Enums used for fixed values
- [ ] Interfaces defined where needed

---

## 6️⃣ Handle Edge Cases (5-10 min)

### What to Do
- Identify potential edge cases
- Add validation
- Handle errors gracefully
- Consider concurrency

### Common Edge Cases

| Category | Examples |
|----------|----------|
| **Null/Empty** | Null inputs, empty collections |
| **Boundaries** | Full capacity, zero items, max size |
| **Invalid Input** | Wrong type, negative values |
| **Concurrency** | Two users taking same resource |
| **State Errors** | Invalid state transitions |
| **Duplicate** | Same item added twice |

### Validation Example

```java
public void parkVehicle(Vehicle vehicle) {
    // Null check
    if (vehicle == null) {
        throw new IllegalArgumentException("Vehicle cannot be null");
    }
    
    // Availability check
    if (!isAvailable) {
        throw new SpotNotAvailableException("Spot already occupied");
    }
    
    // Size compatibility check
    if (!canFitVehicle(vehicle)) {
        throw new InvalidVehicleException("Vehicle too large for spot");
    }
    
    // Happy path
    this.currentVehicle = vehicle;
    this.isAvailable = false;
}
```

---

## Requirements and constraints

- Confirm 4-6 functional requirements before writing class code.
- Capture non-functional constraints: concurrency, persistence, performance target.
- Declare one-sentence scope boundary for out-of-scope features.
- Lock assumptions explicitly if interviewer leaves requirements open-ended.

Checklist:
- [ ] Functional scope confirmed
- [ ] NFR assumptions stated
- [ ] Out-of-scope noted
- [ ] Time budget acknowledged

---

## Scoring rubric

| Dimension | 1-2 | 3 | 4-5 |
|---|---|---|---|
| Problem framing | Unclear scope | Baseline FR/NFR clarity | Crisp scope with assumptions and tradeoffs |
| Class design | Missing boundaries | Reasonable entities/methods | Strong invariants and extensible contracts |
| Pattern usage | Forced/incorrect | Relevant but shallow | Clear rationale tied to change scenarios |
| Edge cases | Minimal | Covers common cases | Covers correctness + concurrency + transitions |
| Communication | Reactive | Organized flow | Proactive and interviewer-friendly narrative |

---

## Common pitfalls

- Coding before requirements are constrained.
- Treating every noun as a top-level class.
- Using patterns as labels instead of change-management tools.
- Missing invalid state-transition handling.
- No recap of design decisions and tradeoffs.

---

## Follow-up questions

1. Which class changes if pricing policy becomes tenant-specific?
2. What lock/atomic boundary guarantees correctness under contention?
3. Which operations should become idempotent?
4. How would you add auditability without coupling core classes to infrastructure?
5. What part of the design would you optimize first at 10x load?

---

## Variants and extensions

- Multi-tenant behavior with policy injection.
- Pluggable algorithms for routing/pricing/validation.
- Event log + replay support for audit/recovery.
- Feature-tier based behavior gates.
- Read-heavy scaling with cached projections.

### Concurrency Handling

```java
// For concurrent access
public synchronized void parkVehicle(Vehicle vehicle) {
    // ... validation and parking logic
}

// Or use locks
private final ReentrantLock lock = new ReentrantLock();

public void parkVehicle(Vehicle vehicle) {
    lock.lock();
    try {
        // ... parking logic
    } finally {
        lock.unlock();
    }
}
```

### What to Say

> "Let me handle some edge cases. What if someone tries to park when the spot is occupied? I'll throw a SpotNotAvailableException. For concurrency, if two cars try to take the same spot, I'll use synchronized methods to ensure thread safety."

### ✅ Checklist
- [ ] Handled null inputs
- [ ] Validated boundary conditions
- [ ] Added appropriate exceptions
- [ ] Considered concurrent access
- [ ] Covered invalid state transitions

---

## 7️⃣ Discuss Complexity (5 min)

### What to Do
- Analyze time complexity of key operations
- Analyze space complexity
- Suggest optimizations if asked

### Analysis Example

| Operation | Current | Optimized | Data Structure |
|-----------|---------|-----------|----------------|
| Find available spot | O(n) | O(1) | Queue of available spots |
| Park vehicle | O(n) | O(1) | HashMap for spot lookup |
| Unpark vehicle | O(1) | O(1) | Direct reference |

### Optimization Example

```java
// Before: O(n) to find available spot
for (ParkingSpot spot : allSpots) {
    if (spot.isAvailable() && spot.canFit(vehicle)) {
        return spot;
    }
}

// After: O(1) with proper data structure
// Maintain queues by spot size
Map<SpotSize, Queue<ParkingSpot>> availableSpots = new HashMap<>();

public ParkingSpot findSpot(VehicleType type) {
    SpotSize requiredSize = type.getRequiredSize();
    Queue<ParkingSpot> queue = availableSpots.get(requiredSize);
    return queue.poll();  // O(1)
}
```

### What to Say

> "For complexity, finding an available spot is currently O(n) where n is total spots. We can optimize to O(1) by maintaining a queue of available spots per size. The trade-off is additional memory for the queue structure."

### ✅ Checklist
- [ ] Analyzed time complexity
- [ ] Analyzed space complexity
- [ ] Identified optimization opportunities
- [ ] Discussed trade-offs

---

## 📊 Summary Checklist

Before wrapping up, verify:

- [ ] All core requirements addressed
- [ ] Classes have single responsibility
- [ ] Appropriate patterns applied and justified
- [ ] Edge cases handled
- [ ] Complexity analyzed
- [ ] Can explain trade-offs
- [ ] Code is clean and readable

---

## 🗣️ Closing the Interview

### What to Say

> "To summarize, I've designed a Parking Lot system with core entities: ParkingLot, Floor, ParkingSpot, Vehicle types, and Ticket. I used Factory pattern for vehicles, Strategy for pricing, and handled concurrency with synchronized methods. The main trade-off is between lookup speed and memory usage for the available spot queues."

### Questions to Ask

- "Are there any areas you'd like me to dive deeper into?"
- "Would you like me to code any specific method?"
- "Any edge cases I might have missed?"

---

## 🔗 Related Resources

- [HOW-TO-APPROACH.md](../../02-lld-projects/HOW-TO-APPROACH.md) - Full LLD framework
- [lld-template.md](../templates/lld-template.md) - Practice template
- [pattern-decision-tree.md](../cheatsheets/pattern-decision-tree.md) - Pattern selection

---

*Follow this checklist systematically and you'll cover all the important points! 📋*
