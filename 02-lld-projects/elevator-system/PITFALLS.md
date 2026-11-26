# Elevator System — Common Interview Pitfalls

Common failure patterns and what to do instead.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. Mixing Dispatch and Elevator Movement

- **Pitfall**: `Elevator` class decides global assignment and movement.
- **Why it hurts**: Breaks single responsibility; hard to swap algorithms.
- **Better**: Keep assignment in `Dispatcher` + `DispatchStrategy`.

## 2. Distance-Only Assignment

- **Pitfall**: Picks nearest elevator by absolute floor distance.
- **Why it hurts**: Ignores direction and causes longer waits.
- **Better**: Include direction, pending route cost, and load in scoring.

## 3. No Explicit State Transitions

- **Pitfall**: Boolean flags (`isMoving`, `isDoorOpen`) with conflicting combinations.
- **Why it hurts**: Invalid behavior and brittle branching.
- **Better**: Use explicit `ElevatorState` and transition guards.

## 4. No Concurrency Boundary

- **Pitfall**: Unsynchronized queue and non-atomic assignment.
- **Why it hurts**: Lost/duplicated requests under contention.
- **Better**: Guard assign path and use thread-safe structures in optimized version.

## 5. Missing Maintenance/Emergency Behavior

- **Pitfall**: Ignores out-of-service and emergency overrides.
- **Why it hurts**: Unsafe and unrealistic design.
- **Better**: Add mode transitions and request redistribution rules.

## 6. Weak Fairness Story

- **Pitfall**: No strategy for starvation.
- **Why it hurts**: Far floors can wait indefinitely.
- **Better**: SCAN/LOOK baseline plus aging or bounded-wait guard.

## 7. Time-Dependent Tests

- **Pitfall**: Uses sleeps and wall-clock timing for dispatch tests.
- **Why it hurts**: Creates flaky tests and hides race conditions.
- **Better**: Drive elevator progression with deterministic simulation ticks.

---

## Quick Self-Check Before You Present

1. Can you swap dispatch logic without changing `Elevator`?
2. Is there one authoritative place for state transitions?
3. Do you have a deterministic story for concurrent inputs?
4. Can you explain starvation prevention in one minute?

---

## Variants and Extensions You Should Mention

1. Zone dispatch for high-rise.
2. Peak-hour strategy switching.
3. VIP/priority floors with anti-starvation.
4. Telemetry hooks for operations monitoring.

---

## Cross-Links

- Pattern refresher: [01-design-patterns](../../01-design-patterns/README.md)
- Related pitfalls: [Parking Lot Pitfalls](../parking-lot/PITFALLS.md)
