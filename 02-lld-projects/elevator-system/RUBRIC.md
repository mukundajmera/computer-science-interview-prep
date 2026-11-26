# Elevator System — Interview Scoring Rubric

Use this rubric to score solution quality consistently across design depth, correctness, and communication.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [CODE-WALKTHROUGH](./CODE-WALKTHROUGH.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|-----------|--------|--------------------------|
| Requirements and constraints clarity | 20% | Distinguishes hall vs cabin requests, concurrency, safety, fairness |
| Domain modeling | 20% | Clean separation: system, elevator, request, dispatcher, strategy |
| Behavioral correctness | 25% | Direction-aware dispatch, valid state transitions, queue fairness |
| Extensibility and variants | 20% | Strategy swapping, maintenance/emergency, high-rise adaptations |
| Code and communication quality | 15% | Clear APIs, deterministic testing narrative, trade-off articulation |

---

## 1 to 5 Guidance

### 1. Requirements and constraints clarity
- **1**: Starts coding with no scoping.
- **3**: Captures basic requirements and mentions constraints.
- **5**: Explicitly separates must-have vs deferred features and validates assumptions.

### 2. Domain modeling
- **1**: God object with mixed responsibilities.
- **3**: Core entities exist but boundaries are fuzzy.
- **5**: Strong SRP boundaries and strategy/state abstractions are natural.

### 3. Behavioral correctness
- **1**: Distance-only assignment and inconsistent states.
- **3**: Mostly correct flow with some edge gaps.
- **5**: Handles direction, queueing, out-of-service behavior, and invalid transitions robustly.

### 4. Extensibility and variants
- **1**: Hard-coded algorithm and no extension points.
- **3**: Mentions variants but no structural hooks.
- **5**: Concrete hooks for strategy switching, priority, zoning, observability.

### 5. Code and communication quality
- **1**: Confusing narrative and long mixed methods.
- **3**: Understandable design with moderate justification.
- **5**: Crisp explanation, focused APIs, and deterministic test strategy.

---

## Hard Gates (Failing Any Gate Caps Score)

1. No clear separation between dispatch and elevator movement logic.
2. No explicit state model for elevator lifecycle.
3. No handling for concurrent request intake in optimized design.
4. No answer for full-system failure mode (maintenance/emergency).

---

## Follow-Up Scoring Boosters

1. Proposes fairness guard (aging, bounded wait target).
2. Compares SCAN vs LOOK with practical trade-offs.
3. Adds zone-aware design for high-rise scale.
4. Mentions telemetry and operational diagnostics.
5. Explains deterministic test strategy without relying on wall-clock delays.

---

## Cross-Links

- Pattern recap: [01-design-patterns](../../01-design-patterns/README.md)
- Theory recap: [00-theory](../../00-theory/README.md)
- Related LLD comparison: [Parking Lot Rubric](../parking-lot/RUBRIC.md)
