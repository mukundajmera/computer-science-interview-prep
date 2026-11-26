# Parking Lot — Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [CODE-WALKTHROUGH](./CODE-WALKTHROUGH.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|-----------|--------|--------------------------|
| Requirements and constraints clarity | 20% | Compatibility rules, ticket lifecycle, concurrency expectations |
| Domain modeling | 20% | Clear lot/floor/spot/ticket/pricing separation |
| Behavioral correctness | 25% | No double-booking, accurate release and fee flow |
| Extensibility and variants | 20% | Pricing/reservation/EV/multi-gate hooks |
| Code and communication quality | 15% | Deterministic APIs, readable abstractions, clear trade-offs |

---

## 1 to 5 Guidance

### 1. Requirements and constraints clarity
- **1**: No requirement clarification.
- **3**: Basic scope captured; some constraints implicit.
- **5**: Explicit compatibility, lifecycle, and error-path assumptions.

### 2. Domain modeling
- **1**: God-class model.
- **3**: Core entities exist with partial boundary leaks.
- **5**: Strong SRP boundaries and policy abstractions.

### 3. Behavioral correctness
- **1**: Can allocate same spot twice / weak release logic.
- **3**: Happy path works, edge handling incomplete.
- **5**: Deterministic handling for full lot, duplicates, invalid tickets.

### 4. Extensibility and variants
- **1**: Hard-coded pricing and mapping logic.
- **3**: Mentions extensions without structural support.
- **5**: Clean hooks for pricing, reservation, EV, and multi-gate scaling.

### 5. Code and communication quality
- **1**: Unclear APIs and weak explanation.
- **3**: Reasonable explanation with minor gaps.
- **5**: Crisp narrative, justified trade-offs, and test-first reasoning.

---

## Hard Gates (Failing Any Gate Caps Score)

1. No atomic story for spot assignment.
2. Fee logic tightly coupled to core entities.
3. No explicit full-lot behavior.
4. No strategy for concurrent entry/exit in optimized design.

---

## Follow-Up Scoring Boosters

1. Clear lock granularity decision with trade-offs.
2. Reservation TTL lifecycle design.
3. Dynamic pricing with transparent policy boundaries.
4. Multi-gate consistency strategy.
5. Deterministic testing plan for ticket IDs and time-based billing paths.

---

## Cross-Links

- Pattern recap: [01-design-patterns](../../01-design-patterns/README.md)
- Theory recap: [00-theory](../../00-theory/README.md)
- Related LLD comparison: [Elevator Rubric](../elevator-system/RUBRIC.md)
