# Code Walkthrough: Parking Lot System

## Overview

This walkthrough maps [DESIGN](./DESIGN.md) to code structure and highlights the interview narrative for `v1`, `v2`, and `v3`.

---

## Requirements and Constraints Trace

| Requirement | Code responsibility |
|-------------|---------------------|
| Spot compatibility | `ParkingSpot.canFit` and allocation policy |
| Ticket lifecycle | `Ticket` + active ticket index in lot/system |
| Fee policy flexibility | `PricingStrategy` implementations |
| Concurrency-safe allocation | synchronized/lock-protected allocation in optimized track |
| Fast lookup | Maps keyed by ticket and vehicle identifiers |

---

## End-to-End Flow

### 1. Entry flow (`parkVehicle`)

1. Validate vehicle identity and duplicate-park conditions.
2. Find compatible floor/spot via floor pools.
3. Claim spot atomically.
4. Create and store active ticket.

### 2. Exit flow (`unparkVehicle`)

1. Resolve active ticket by id.
2. Compute fee using active pricing strategy.
3. Release occupied spot and update availability counters.
4. Mark ticket closed and remove active indexes.

### 3. Lookup flow

1. Resolve vehicle location by ticket or plate.
2. Return floor + spot metadata in O(1) average time.

---

## Version Progression

| Version | Interview signal |
|---------|------------------|
| `v1-basic` | Correct entities and deterministic park/unpark behavior |
| `v2-extended` | Better policy abstraction (pricing/reservation/payment hooks) |
| `v3-optimized` | Safe concurrent operations and operational counters/hooks |

---

## Pattern Usage Anchors

1. `Strategy` for pricing.
2. `Singleton`/system facade where repo implementation uses it.
3. `Factory`/policy map for vehicle-spot compatibility (optional).
4. `Observer` for availability display extensions.

---

## Common Interview Talking Points

1. Why fee policy should not live in `Ticket`.
2. How to avoid double-booking with atomic claim.
3. Locking choice: global lock vs per-floor lock.
4. Full-lot behavior and API return semantics.
5. Reservation and EV support without core rewrites.

---

## Variants and Extension Hooks

1. Reservation TTL sweeper + confirmation flow.
2. Dynamic pricing based on occupancy/time.
3. Multi-gate architecture with shared counters.
4. EV charging session billing integration.

---

## Testability Checklist

1. Keep deterministic token/ticket IDs in tests to avoid random assertions.
2. Keep time-sensitive fee and expiry paths injectable (clock abstraction in advanced variants).
3. Verify idempotency for duplicate exit scans and invalid ticket replays.

---

## Cross-Links

- Problem framing: [PROBLEM](./PROBLEM.md)
- Design details: [DESIGN](./DESIGN.md)
- Scoring expectations: [RUBRIC](./RUBRIC.md)
- Mistakes to avoid: [PITFALLS](./PITFALLS.md)
- Follow-up variants: [FOLLOW-UPS](./FOLLOW-UPS.md)
- Related LLD project: [Elevator System](../elevator-system/CODE-WALKTHROUGH.md)
- Related LLD project: [Amazon Locker](../amazon-locker/CODE-WALKTHROUGH.md)
