# Parking Lot — Common Interview Pitfalls

Common failure patterns and stronger alternatives.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. God-Class `ParkingLot`

- **Pitfall**: Allocation, pricing, ticketing, and payment all in one class.
- **Why it hurts**: Hard to test and extend.
- **Better**: Delegate to floor/spot manager + pricing strategy + ticket service.

## 2. Hard-Coded Compatibility Rules

- **Pitfall**: Repeated if/else checks for vehicle-to-spot fit.
- **Why it hurts**: New vehicle/spot types require invasive edits.
- **Better**: Compatibility map/policy abstraction.

## 3. Non-Atomic Spot Allocation

- **Pitfall**: Check available spot, then assign in separate unsynchronized steps.
- **Why it hurts**: Double-booking under concurrent entries.
- **Better**: Atomic claim under lock/CAS in optimized version.

## 4. Pricing Logic Embedded in Core Entities

- **Pitfall**: Fee formulas inside `Ticket`/`ParkingLot` core flow.
- **Why it hurts**: Policy changes ripple through core domain.
- **Better**: Strategy-based fee calculators.

## 5. Weak Error Semantics

- **Pitfall**: Full lot or invalid ticket returns ambiguous null/boolean.
- **Why it hurts**: API consumers cannot reason about failure.
- **Better**: Explicit error/result types and documented behaviors.

## 6. No Multi-Floor Scaling Story

- **Pitfall**: Flat list of spots with no floor-level ownership.
- **Why it hurts**: Poor scalability and observability.
- **Better**: `ParkingLot -> Floor -> Spot` hierarchy with per-floor counters.

## 7. Non-Deterministic Time in Tests

- **Pitfall**: Uses wall-clock sleeps for billing and expiry behavior.
- **Why it hurts**: Flaky tests and hidden race bugs.
- **Better**: Inject clock/time providers in advanced variants.

---

## Quick Self-Check Before You Present

1. Can your design prevent double-booking under simultaneous entry?
2. Can pricing policy change without rewriting park/unpark flow?
3. Is full-lot behavior explicit and testable?
4. Can you add reservations without breaking base APIs?

---

## Variants and Extensions You Should Mention

1. Reservation TTL and confirmation flow.
2. Dynamic occupancy-based pricing.
3. Multi-gate distributed consistency.
4. EV charging and energy billing.

---

## Cross-Links

- Pattern refresher: [01-design-patterns](../../01-design-patterns/README.md)
- Related pitfalls: [Elevator Pitfalls](../elevator-system/PITFALLS.md)
- Related pitfalls: [Amazon Locker Pitfalls](../amazon-locker/PITFALLS.md)
