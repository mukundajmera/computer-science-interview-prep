# Contributing Guidelines

Thank you for your interest in contributing to the System Design Interview Prep repository! This document provides comprehensive guidelines for contributing.

---

## 📑 Table of Contents

- [🎯 How to Contribute](#-how-to-contribute)
- [📋 Code Standards](#-code-standards)
- [📖 Documentation Standards](#-documentation-standards)
- [🔢 Versioning Approach](#-versioning-approach)
- [🔄 Pull Request Process](#-pull-request-process)
- [📁 File Naming Conventions](#-file-naming-conventions)
- [🧪 Testing Requirements](#-testing-requirements)
- [📜 Code of Conduct](#-code-of-conduct)

---

## 🎯 How to Contribute

We welcome contributions in the following areas:

### 1. New Content
| Type | Description | Priority |
|------|-------------|----------|
| **Design Patterns** | New patterns with Java & Python implementations | High |
| **LLD Projects** | New problem statements and solutions | High |
| **HLD Projects** | New system designs | High |
| **Theory** | Concept explanations | Medium |
| **Cheatsheets** | Quick reference materials | Medium |
| **Interview Q&A** | Common questions and answers | Medium |

### 2. Improvements
- Fix typos or errors
- Improve explanations for clarity
- Add missing edge cases
- Optimize code examples
- Add diagrams or visualizations
- Improve cross-references

### 3. Translations
- Translate content to other languages
- Add implementations in additional programming languages (Go, TypeScript, etc.)

---

## 📋 Code Standards

### General Principles

Our code should be:
- **Clean** - Easy to read and understand in 30 seconds
- **Interview-Ready** - Can be written in 45 minutes under pressure
- **Commented** - Key decisions explained, not obvious code
- **Tested** - At least happy path and main edge cases

### Java Standards

```java
// Use meaningful, self-documenting names
public class ParkingLot {
    
    // Constants in UPPER_SNAKE_CASE
    private static final int MAX_FLOORS = 5;
    
    // Private fields with descriptive names
    private final List<Floor> floors;
    private final PricingStrategy pricingStrategy;
    
    // Constructor injection for dependencies
    public ParkingLot(int numFloors, PricingStrategy pricingStrategy) {
        this.floors = new ArrayList<>();
        this.pricingStrategy = pricingStrategy;
        initializeFloors(numFloors);
    }
    
    /**
     * Parks a vehicle in the first available spot.
     * 
     * Time Complexity: O(floors * spots) in worst case
     * Space Complexity: O(1)
     * 
     * @param vehicle The vehicle to park
     * @return Ticket if parked successfully, null if lot is full
     * @throws IllegalArgumentException if vehicle is null
     */
    public Ticket parkVehicle(Vehicle vehicle) {
        // Validate input
        if (vehicle == null) {
            throw new IllegalArgumentException("Vehicle cannot be null");
        }
        
        // Find available spot
        for (Floor floor : floors) {
            ParkingSpot spot = floor.findAvailableSpot(vehicle.getType());
            if (spot != null) {
                spot.park(vehicle);
                return new Ticket(vehicle, spot, LocalDateTime.now());
            }
        }
        
        return null; // Lot is full
    }
    
    // Private helper methods
    private void initializeFloors(int numFloors) {
        for (int i = 0; i < numFloors; i++) {
            floors.add(new Floor(i));
        }
    }
}
```

**Java Style Summary:**
- Class names: `PascalCase`
- Method/variable names: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Use `final` where possible
- Prefer constructor injection
- Include Javadoc for public methods
- Document time/space complexity

### Python Standards

```python
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


class ParkingLot:
    """
    Represents a multi-floor parking lot.
    
    Manages parking operations including vehicle parking,
    spot allocation, and fee calculation.
    """
    
    MAX_FLOORS = 5  # Class constants in UPPER_CASE
    
    def __init__(self, num_floors: int, pricing_strategy: PricingStrategy):
        """
        Initialize parking lot with given configuration.
        
        Args:
            num_floors: Number of floors in the parking lot
            pricing_strategy: Strategy for calculating parking fees
        """
        self._floors: List[Floor] = []
        self._pricing_strategy = pricing_strategy
        self._initialize_floors(num_floors)
    
    def park_vehicle(self, vehicle: Vehicle) -> Optional[Ticket]:
        """
        Parks a vehicle in the first available spot.
        
        Time Complexity: O(floors * spots) in worst case
        Space Complexity: O(1)
        
        Args:
            vehicle: The vehicle to park
            
        Returns:
            Ticket if parked successfully, None if lot is full
            
        Raises:
            ValueError: If vehicle is None
        """
        if vehicle is None:
            raise ValueError("Vehicle cannot be None")
        
        # Find available spot
        for floor in self._floors:
            spot = floor.find_available_spot(vehicle.vehicle_type)
            if spot:
                spot.park(vehicle)
                return Ticket(vehicle, spot, datetime.now())
        
        return None  # Lot is full
    
    def _initialize_floors(self, num_floors: int) -> None:
        """Initialize floors for the parking lot."""
        for i in range(num_floors):
            self._floors.append(Floor(i))
```

**Python Style Summary:**
- Class names: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: prefix with `_`
- Use type hints throughout
- Use dataclasses where appropriate
- Include docstrings for public methods
- Document time/space complexity

---

## 📖 Documentation Standards

### Follow Existing Structure

Each content type has a specific format:

#### Design Patterns
```markdown
# Pattern Name

## 📚 Theory
### Problem & Motivation
[Why this pattern exists]

### Structure (UML)
[ASCII or image diagram]

### Participants
- **Component1**: [Role description]
- **Component2**: [Role description]

## 🏗️ Implementation

### Java
```java
[Complete implementation]
```

### Python
```python
[Complete implementation]
```

## 🎯 When to Use
- [Use case 1]
- [Use case 2]

## ⚠️ Trade-offs
- **Pros**: [Benefits]
- **Cons**: [Drawbacks]

## 🔗 Related Patterns
- [Pattern 1]: [Relationship]
- [Pattern 2]: [Relationship]

## ❓ Interview Q&A
**Q: [Common question]?**
A: [Detailed answer]
```

#### LLD Projects
```markdown
# Project Name

## 📋 Problem Statement
[Clear problem description]

## 🎯 Requirements
### Functional Requirements
1. [Requirement 1]
2. [Requirement 2]

### Non-Functional Requirements
1. [Requirement 1]

## 🏗️ Approach
[Step-by-step thinking process]

## 🎨 Design
### Entities
- **Entity1**: [Description]
- **Entity2**: [Description]

### Class Diagram
[ASCII or image diagram]

## 💻 Solution

### v1: Basic Implementation
[Code and explanation]

### v2: Optimized with Patterns
[Code and explanation]

### v3: Production-Ready
[Code and explanation]

## ⚠️ Edge Cases
- [Edge case 1 and how to handle]
- [Edge case 2 and how to handle]

## ❓ Follow-up Questions
**Q: [Extension question]?**
A: [How to extend the design]
```

#### HLD Projects
```markdown
# System Name

## 📋 Problem Statement
[System overview and scale]

## 🎯 Requirements
### Functional Requirements
1. [Feature 1]
2. [Feature 2]

### Non-Functional Requirements
- Scale: [Expected scale]
- Latency: [Target latency]
- Availability: [Target availability]

## 📊 Capacity Estimation
### Traffic
[QPS calculations]

### Storage
[Storage calculations]

### Bandwidth
[Bandwidth calculations]

## 🔌 API Design
### Endpoint 1
```
POST /api/v1/resource
Request: { ... }
Response: { ... }
```

## 💾 Data Model
### Schema
[Database schema]

### Database Choice
[SQL vs NoSQL justification]

## 🏗️ High-Level Architecture
[Architecture diagram]

### Data Flow
1. [Step 1]
2. [Step 2]

## 🔍 Deep Dives
### Scaling
[Scaling approach]

### Caching
[Caching strategy]

## ⚖️ Trade-offs
[Design decisions and alternatives]

## ❓ Follow-up Questions
**Q: [Common question]?**
A: [Detailed answer]
```

---

## 🔢 Versioning Approach

We follow a v1 → v2 → v3 progression for solutions:

| Version | Purpose | Characteristics |
|---------|---------|-----------------|
| **v1** | Basic Solution | Works correctly, straightforward implementation |
| **v2** | Optimized | Design patterns applied, cleaner code structure |
| **v3** | Production-Ready | Edge cases handled, fully documented, tested |

This helps learners understand progressive improvement and interview expectations.

### Version Guidelines

**v1 (Basic)**:
- Solves the core problem
- May have some code duplication
- Simple data structures
- Basic error handling

**v2 (Optimized)**:
- Applies relevant design patterns
- Follows SOLID principles
- Better abstraction
- Improved naming

**v3 (Production-Ready)**:
- Thread-safe where needed
- Comprehensive validation
- Proper exception handling
- Full documentation
- Test coverage

---

## 🔄 Pull Request Process

### Before Submitting

1. **Check existing content** - Avoid duplicates
2. **Follow templates** - Use existing structure
3. **Test your code** - Ensure it compiles/runs
4. **Self-review** - Check for typos and clarity
5. **Update cross-references** - Link to related content

### PR Requirements

| Requirement | Details |
|-------------|---------|
| **Clear title** | "Add Singleton Pattern" or "Fix typo in Parking Lot" |
| **Description** | What you added/changed and why |
| **One focus** | Each PR should address one thing |
| **Complete content** | Don't submit half-finished work |
| **Both languages** | Include Java AND Python implementations |

### Review Process

1. Maintainer reviews within 48-72 hours
2. Address feedback if requested
3. Merge upon approval

### Commit Message Format

```
<type>: <short description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature/content
- `fix`: Bug fix or correction
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding/updating tests

**Examples:**
```
feat: Add Singleton pattern with thread-safe implementation

docs: Fix broken links in CONCEPTS.md

fix: Correct time complexity in LRU Cache
```

---

## 📁 File Naming Conventions

### Folders
- Use lowercase with hyphens: `design-patterns`, `hld-projects`
- Number prefixes for ordering: `00-theory`, `01-design-patterns`
- Descriptive names: `oop-principles` not `oop`

### Files
- Use lowercase with hyphens: `parking-lot.md`, `url-shortener.md`
- Keep names concise but descriptive
- README.md for folder index (capital letters)

### Code Files
| Language | Convention | Example |
|----------|------------|---------|
| Java | PascalCase matching class | `ParkingLot.java`, `Vehicle.java` |
| Python | snake_case | `parking_lot.py`, `vehicle.py` |
| Tests | Same as source + Test/test_ | `ParkingLotTest.java`, `test_parking_lot.py` |

---

## 🧪 Testing Requirements

### For Code Examples

Include basic tests that verify:
- ✅ Happy path works
- ✅ Edge cases handled
- ✅ No runtime errors
- ✅ Expected outputs correct

### Example (Java - JUnit 5)
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

class ParkingLotTest {
    
    private ParkingLot lot;
    
    @BeforeEach
    void setUp() {
        lot = new ParkingLot(3);
    }
    
    @Test
    void testParkVehicle_Success() {
        Vehicle car = new Car("ABC-123");
        
        Ticket ticket = lot.parkVehicle(car);
        
        assertNotNull(ticket);
        assertEquals(car, ticket.getVehicle());
    }
    
    @Test
    void testParkVehicle_LotFull_ReturnsNull() {
        // Fill the lot
        for (int i = 0; i < lot.getTotalCapacity(); i++) {
            lot.parkVehicle(new Car("CAR-" + i));
        }
        
        Ticket ticket = lot.parkVehicle(new Car("XYZ-789"));
        
        assertNull(ticket);
    }
    
    @Test
    void testParkVehicle_NullVehicle_ThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            lot.parkVehicle(null);
        });
    }
}
```

### Example (Python - pytest)
```python
import pytest
from parking_lot import ParkingLot, Car

class TestParkingLot:
    
    @pytest.fixture
    def lot(self):
        return ParkingLot(num_floors=3)
    
    def test_park_vehicle_success(self, lot):
        car = Car("ABC-123")
        
        ticket = lot.park_vehicle(car)
        
        assert ticket is not None
        assert ticket.vehicle == car
    
    def test_park_vehicle_lot_full_returns_none(self, lot):
        # Fill the lot
        for i in range(lot.total_capacity):
            lot.park_vehicle(Car(f"CAR-{i}"))
        
        ticket = lot.park_vehicle(Car("XYZ-789"))
        
        assert ticket is None
    
    def test_park_vehicle_null_raises_exception(self, lot):
        with pytest.raises(ValueError):
            lot.park_vehicle(None)
```

---

## 📜 Code of Conduct

### Our Standards

- **Be respectful and constructive** - Critique ideas, not people
- **Welcome newcomers** - Help others learn and grow
- **Focus on quality** - Aim for excellence in every contribution
- **Give credit** - Acknowledge others' work and contributions
- **Stay on topic** - Keep discussions relevant to system design

### Unacceptable Behavior

- Harassment or discriminatory comments
- Trolling or insulting remarks
- Publishing others' private information
- Spam or self-promotion unrelated to the project

### Enforcement

Project maintainers will remove, edit, or reject contributions that violate this code of conduct.

---

## 🙋 Questions?

If you have questions about contributing:

1. 📋 Check existing [issues](https://github.com/mukundajmera/computer-science-interview-prep/issues)
2. 🆕 Open a new issue with your question
3. 🏷️ Tag it with `question` label

---

Thank you for helping make this a world-class resource for system design interview preparation! 🎯
