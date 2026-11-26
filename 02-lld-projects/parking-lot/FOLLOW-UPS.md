# Parking Lot — Follow-Up Questions

Use these variants to probe depth after baseline parking-lot design.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md)

---

## 1. How would you add reservations?

- Introduce `Reservation` entity with lifecycle and expiry.
- Reserve a spot or quota by type/floor with TTL cleanup.
- Merge reservation and walk-in allocation policies safely.

## 2. How would you support dynamic pricing?

- Wrap base pricing strategy with occupancy/time-aware multiplier.
- Keep pricing context decoupled from core entities.
- Define customer transparency rule (entry-time vs exit-time pricing).

## 3. How do you make allocation thread-safe?

- Protect check-and-claim as one atomic operation.
- Compare global lock vs per-floor lock trade-offs.
- Add contention metrics to validate design choices.

## 4. How do you support EV charging?

- Add EV-capable spot type and charging session lifecycle.
- Combine parking-time fee and energy fee policies.
- Define fallback behavior when chargers are unavailable.

## 5. How do you support multiple entry/exit gates?

- Keep consistent shared availability state.
- Use gate-level services with centralized or partitioned allocators.
- Ensure idempotent ticket close and payment completion.

## 6. What would real-time display/monitoring include?

- Per-floor availability by spot type.
- Entry queue time and failed-allocation counts.
- Event stream hooks for displays and operations dashboard.

---

## Follow-Up Scoring Signals

1. Candidate preserves core boundaries while extending functionality.
2. Candidate names trade-offs and failure modes explicitly.
3. Candidate keeps deterministic and testable behavior under concurrency.

---

## Additional Variants

1. Monthly subscriptions with reserved capacity quotas.
2. Valet workflow with asynchronous handoff.
3. Fraud/lost-ticket dispute handling.
4. Deterministic replay mode for entry/exit audit simulation.

---

## Cross-Links

- Approach flow: [APPROACH](./APPROACH.md)
- Related LLD extension set: [Elevator Follow-Ups](../elevator-system/FOLLOW-UPS.md)
- Related reservation/lifecycle set: [Amazon Locker Follow-Ups](../amazon-locker/FOLLOW-UPS.md)
- Pattern library: [01-design-patterns](../../01-design-patterns/README.md)
