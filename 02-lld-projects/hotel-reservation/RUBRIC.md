# Hotel Reservation System — Interview Scoring Rubric

Use this rubric to score solution quality consistently across design depth, correctness, and communication.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Interview Timeline (45 Minutes)

- **00:00 - 05:00**: Requirements gathering and scope alignment. Clarifying ambiguity (single hotel vs chain).
- **05:00 - 10:00**: Core domain modeling (identifying entities, relationships) and API contract definition.
- **10:00 - 30:00**: Detailed LLD implementation. Writing code, defining class structures, search logic.
- **30:00 - 40:00**: Addressing concurrency, edge cases (overbooking), data consistency.
- **40:00 - 45:00**: Follow-up questions, scalability discussions, alternative approaches, and Q&A.

---

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|-----------|--------|--------------------------|
| Requirements and constraints clarity | 20% | Distinguishes Room vs RoomType, understands scale. Validates assumptions early. |
| Domain modeling | 20% | Clean separation of concerns: inventory, pricing, reservation, payment. |
| Behavioral correctness | 25% | Valid state transitions, robust double-booking prevention, proper date overlap logic. |
| Extensibility and variants | 20% | Strategy swapping for pricing/cancellation, clean abstractions. |
| Code and communication quality | 15% | Clear APIs, articulate narrative, structured code, trade-off articulation. |

---

## 1 to 5 Guidance

### 1. Requirements and constraints clarity
- **1**: Starts coding immediately without scoping or clarifying requirements.
- **3**: Captures basic functional requirements but misses non-functional constraints or scale.
- **5**: Explicitly separates must-have vs deferred features, validates assumptions.

### 2. Domain modeling
- **1**: Produces a "God object" with mixed responsibilities; poor database schema.
- **3**: Core entities exist, but boundaries are fuzzy, fails to separate Room and RoomType.
- **5**: Strong Single Responsibility Principle boundaries. Design patterns are applied naturally.

### 3. Behavioral correctness
- **1**: Flawed core logic, inconsistent states, ignores concurrency entirely (double bookings allowed).
- **3**: Mostly correct happy path flow, but leaves some edge cases or failure scenarios unhandled.
- **5**: Handles state transitions flawlessly, robust concurrency control, robust invalid input validation.

### 4. Extensibility and variants
- **1**: Hard-coded pricing algorithms; no extension points.
- **3**: Mentions variants or patterns conceptually but fails to provide structural hooks in the code.
- **5**: Concrete hooks for strategy switching (pricing, cancellation), easy to add new integrations.

### 5. Code and communication quality
- **1**: Confusing narrative, long mixed methods, poorly named variables.
- **3**: Understandable design with moderate justification. Code is generally readable.
- **5**: Crisp explanation, focused APIs, clean and readable code.

---

## Hard Gates (Failing Any Gate Caps Score)

1. Fails to prevent double-booking (no concurrency strategy).
2. Fails to separate the concept of a `RoomType` (for booking) from a physical `Room`.
3. Highly inefficient date-range searching algorithm.
4. No viable answer for handling critical failure modes (e.g., payment gateway outages).
