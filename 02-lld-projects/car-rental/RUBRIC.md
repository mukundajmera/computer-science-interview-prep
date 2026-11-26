# Car Rental System — Interview Scoring Rubric

Use this rubric to score solution quality consistently across design depth, correctness, and communication.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Interview Timeline (45 Minutes)

- **00:00 - 05:00**: Requirements gathering and scope alignment. Define exact features (e.g., one-way vs round-trip).
- **05:00 - 10:00**: Core domain modeling (Vehicle, Branch, Reservation) and API definition.
- **10:00 - 30:00**: Detailed LLD implementation. Writing code for search, booking, and inventory management.
- **30:00 - 40:00**: Addressing concurrency (double booking), edge cases, and state transitions.
- **40:00 - 45:00**: Follow-up questions, scalability discussions, and Q&A.

---

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|-----------|--------|--------------------------|
| Requirements and constraints clarity | 20% | Distinguishes core entities, vehicle classes vs specific vehicles. Validates assumptions. |
| Domain modeling | 20% | Clean schema: separate inventory, reservation, billing, and user entities. |
| Behavioral correctness | 25% | Solves the double-booking problem. Correct date overlap logic. |
| Extensibility and variants | 20% | Strategy pattern for pricing. Extensible state machine for vehicles. |
| Code and communication quality | 15% | Clear APIs, articulate narrative, well-structured database queries. |

---

## 1 to 5 Guidance

### 1. Requirements and constraints clarity
- **1**: Starts coding immediately without scoping or clarifying requirements.
- **3**: Captures basic functional requirements but misses constraints like timezone handling.
- **5**: Explicitly separates must-have vs deferred features, validates scale assumptions.

### 2. Domain modeling
- **1**: Confuses a 'Car Type' with a physical 'Car'. Poor entity relationships.
- **3**: Core entities exist, but relationships (e.g., Branch to Car) are brittle.
- **5**: Clear distinction between `VehicleClass` and physical `Vehicle`. Strong ER modeling.

### 3. Behavioral correctness
- **1**: Fails to handle concurrent bookings. Buggy date overlap logic.
- **3**: Mostly correct happy path flow, but leaves some edge cases unhandled.
- **5**: Flawless concurrency control, robust availability search logic.

### 4. Extensibility and variants
- **1**: Hard-coded pricing algorithms; rigid vehicle states.
- **3**: Mentions variants conceptually but fails to provide structural hooks.
- **5**: Concrete hooks for strategy switching (pricing), easy to add new vehicle types.

### 5. Code and communication quality
- **1**: Confusing narrative, long methods, unable to explain search time complexity.
- **3**: Understandable design with moderate justification.
- **5**: Crisp explanation, focused APIs, clean and readable code.

---

## Hard Gates (Failing Any Gate Caps Score)

1. Fails to distinguish between a Vehicle Make/Model and a physical Vehicle (Barcode/License).
2. Fails to implement concurrency control (allows double booking).
3. Highly inefficient availability search (e.g., loading all cars into memory).
4. No clear state machine for the Vehicle lifecycle.
