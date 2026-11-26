# 🔧 How to Approach LLD Problems

A structured framework for tackling Low-Level Design interview problems.

---

## 🎯 The 7-Step Framework

### Step 1: Clarify Requirements (5 min)

**Ask clarifying questions to understand scope:**

#### Functional Requirements
- What are the core features needed?
- What actions can users perform?
- What are the inputs and expected outputs?

#### Non-Functional Requirements
- Is concurrency a concern?
- Do we need persistence?
- What's the expected scale (users, transactions)?

#### Example Questions to Ask:
```
- "Should the parking lot support multiple floors?"
- "Do we need to handle different payment methods?"
- "Should the system support multiple elevators?"
- "Is there a time limit for book reservations?"
```

---

### Step 2: Identify Core Entities (5 min)

**Find the nouns in the problem statement:**

```
Problem: "Design a parking lot system where vehicles can park in spots.
The lot has multiple floors and different spot sizes for different vehicles."

Entities identified:
- ParkingLot
- Floor
- ParkingSpot
- Vehicle (Car, Motorcycle, Truck)
- Ticket
```

**For each entity, note:**
- Attributes (what data does it hold?)
- Behaviors (what can it do?)
- Relationships (how does it relate to others?)

---

### Step 3: Define Relationships (5 min)

**Map how entities connect:**

| Relationship | Type | Example |
|--------------|------|---------|
| **Has-A** (Composition) | Strong ownership | ParkingLot HAS Floors |
| **Uses-A** (Aggregation) | Weak ownership | ParkingSpot references Vehicle |
| **Is-A** (Inheritance) | Type hierarchy | Car IS-A Vehicle |

**Draw a simple diagram:**
```
ParkingLot
├── Floor (1..n)
│   └── ParkingSpot (1..n)
│       └── Vehicle (0..1)
└── EntryPanel
    └── generates Ticket
```

---

### Step 4: Choose Design Patterns (5 min)

**Match problems to patterns:**

| If You Need To... | Consider Using... |
|-------------------|-------------------|
| Create objects without specifying class | Factory |
| Ensure only one instance | Singleton |
| Change behavior based on state | State |
| Select algorithm at runtime | Strategy |
| Notify multiple objects of changes | Observer |
| Build complex objects step-by-step | Builder |
| Add behavior dynamically | Decorator |

**Common LLD Pattern Combinations:**
- **Parking Lot**: Factory (vehicle types) + Strategy (pricing)
- **Elevator**: State (elevator states) + Strategy (scheduling)
- **Vending Machine**: State (machine states) + Strategy (payment)

---

### Step 5: Design Classes (15-20 min)

**For each class, define:**

```java
public class ParkingSpot {
    // Attributes
    private String spotId;
    private SpotSize size;
    private Vehicle currentVehicle;
    private boolean isAvailable;
    
    // Constructor
    public ParkingSpot(String spotId, SpotSize size) { }
    
    // Behaviors
    public boolean canFitVehicle(Vehicle vehicle) { }
    public void parkVehicle(Vehicle vehicle) { }
    public void removeVehicle() { }
    
    // Getters/Setters as needed
}
```

**Class Design Checklist:**
- [ ] Single Responsibility - each class does one thing
- [ ] Encapsulation - private fields, public methods
- [ ] Clear naming - self-documenting code
- [ ] Appropriate data types - enum for fixed options

---

### Step 6: Handle Edge Cases (5-10 min)

**Always consider:**

| Category | Examples |
|----------|----------|
| **Null/Empty** | What if vehicle is null? Empty parking lot? |
| **Boundaries** | First spot? Last spot? Full capacity? |
| **Concurrency** | Two cars trying same spot? |
| **Invalid Input** | Wrong vehicle type? Negative values? |
| **Error States** | Payment failed? System offline? |

**Add validation:**
```java
public void parkVehicle(Vehicle vehicle) {
    if (vehicle == null) {
        throw new IllegalArgumentException("Vehicle cannot be null");
    }
    if (!isAvailable) {
        throw new SpotNotAvailableException("Spot already occupied");
    }
    if (!canFitVehicle(vehicle)) {
        throw new InvalidVehicleException("Vehicle too large for spot");
    }
    // ... proceed with parking
}
```

---

### Step 7: Optimize (5-10 min)

**Review for improvements:**

| Aspect | Check For |
|--------|-----------|
| **Time Complexity** | Any O(n²) that could be O(n) or O(1)? |
| **Space Complexity** | Unnecessary data storage? |
| **Data Structures** | Using HashMap for O(1) lookups? |
| **Caching** | Frequently computed values? |

**Example Optimization:**
```java
// Before: O(n) to find available spot
for (ParkingSpot spot : allSpots) {
    if (spot.isAvailable() && spot.canFit(vehicle)) {
        return spot;
    }
}

// After: O(1) with proper data structure
Queue<ParkingSpot> availableSpots = new LinkedList<>();
return availableSpots.poll();
```

---

## 📝 Example Walkthrough: Parking Lot

### Problem
Design a parking lot system with multiple floors, different spot sizes, and automatic spot assignment.

### Step 1: Requirements
**Functional:**
- Park vehicles of different types (car, motorcycle, truck)
- Assign appropriate spot size
- Track occupied vs available spots
- Generate parking tickets
- Calculate parking fees

**Non-Functional:**
- Handle concurrent parking requests
- Quick spot lookup

### Step 2: Entities
```
- ParkingLot
- Floor
- ParkingSpot (Small, Medium, Large)
- Vehicle (Motorcycle, Car, Truck)
- Ticket
- ParkingRate
```

### Step 3: Relationships
```
ParkingLot (1) ─────contains───── (n) Floor
Floor (1) ─────contains───── (n) ParkingSpot
ParkingSpot (1) ─────holds───── (0..1) Vehicle
Ticket ─────references───── ParkingSpot
Ticket ─────references───── Vehicle
```

### Step 4: Patterns
- **Factory**: Create different vehicle types
- **Strategy**: Different pricing strategies
- **Singleton**: ParkingLot instance

### Step 5: Key Classes

```java
// Enums
enum VehicleType { MOTORCYCLE, CAR, TRUCK }
enum SpotSize { SMALL, MEDIUM, LARGE }

// Core Classes
class Vehicle {
    String licensePlate;
    VehicleType type;
}

class ParkingSpot {
    String id;
    SpotSize size;
    Vehicle vehicle;
    boolean available;
    
    boolean canFit(Vehicle v);
    void park(Vehicle v);
    void unpark();
}

class Floor {
    int floorNumber;
    List<ParkingSpot> spots;
    
    ParkingSpot findAvailableSpot(VehicleType type);
}

class ParkingLot {
    List<Floor> floors;
    
    Ticket parkVehicle(Vehicle v);
    double unparkVehicle(Ticket t);
}
```

### Step 6: Edge Cases
- Parking lot is full
- Vehicle already parked
- Invalid ticket on exit
- Double unparking

### Step 7: Optimizations
- Use `Map<SpotSize, Queue<ParkingSpot>>` for O(1) spot finding
- Cache available spot counts per floor

---

## Requirements and constraints

Use this as a fixed pre-coding contract in interviews:

- Functional scope: list only the 4-6 must-have flows for v1.
- Non-functional expectations: concurrency, persistence, and performance assumptions.
- Time constraint: 45-60 minute round means class-model clarity over exhaustive code.
- Explicit exclusions: call out what is intentionally out of scope.

Suggested one-line framing:

> "I will design for correctness and extensibility first, then optimize specific bottlenecks if we still have time."

---

## Scoring rubric

| Dimension | Weak signal | Strong signal |
|---|---|---|
| Requirements & scope | Starts coding immediately | Confirms FR/NFR and out-of-scope first |
| Entity modeling | Misses core domain objects | Clean entity set with clear responsibilities |
| Class/API design | Vague methods and mutable sprawl | Focused APIs, encapsulated state, clear invariants |
| Pattern usage | Pattern name-dropping | Uses 1-3 patterns where they reduce change-risk |
| Edge-case handling | Happy-path only | Covers null/invalid/concurrency/state-transition issues |
| Communication | Disorganized narrative | Structured walkthrough with tradeoffs and recap |

---

## Common pitfalls

- Over-scoping requirements and leaving no time for core class design.
- Modeling every noun as a class without responsibility boundaries.
- Introducing patterns before proving the simpler design is insufficient.
- Ignoring state transition guards (e.g., invalid operation sequence).
- Failing to discuss how design evolves for new requirements.

---

## Follow-up questions

1. Which class would change first if pricing logic becomes configurable per tenant?
2. What fails first under concurrent requests, and what lock/atomic boundary do you choose?
3. Which method contracts must become idempotent?
4. How would you support audit history without bloating core domain classes?
5. What extension points did you add to avoid rewriting existing code?

---

## Variants and extensions

- Multi-tenant variant: enforce tenant-isolated state and configuration.
- Scale variant: add read-heavy optimization and write-contention safeguards.
- Reliability variant: add retry-safe operations and failure recovery hooks.
- Product variant: introduce feature toggles that alter behavior by policy.

---

## Cross-References

- [LLD Interview Q&A](./INTERVIEW-QA.md)
- [LLD Checklist](../resources/interview-tips/lld-checklist.md)
- [LLD Practice Template](../resources/templates/practice-lld.md)
- [SOLID Principles](../00-theory/oop-principles/solid-principles.md)
- [DRY/KISS/YAGNI](../00-theory/oop-principles/dry-kiss-yagni.md)

---

## 📌 Interview Tips

1. **Think out loud** - Explain your reasoning as you design
2. **Start simple** - Get basic design working, then add complexity
3. **Ask before assuming** - Requirements clarification shows maturity
4. **Trade-offs** - Discuss alternatives you considered
5. **Be ready to extend** - Interviewers often ask "what if we add..."

---

## 📋 Quick Checklist

Before presenting your solution:

- [ ] All core requirements addressed
- [ ] Classes have single responsibility
- [ ] Appropriate patterns applied
- [ ] Edge cases handled
- [ ] Code is clean and readable
- [ ] Can explain trade-offs

---

*Use the [LLD Template](../resources/templates/lld-template.md) for practice!*
