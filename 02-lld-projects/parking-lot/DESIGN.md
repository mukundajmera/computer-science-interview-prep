# Design for Parking Lot System

## Design Goals

1. Keep allocation, ticket lifecycle, and pricing concerns decoupled.
2. Make spot assignment deterministic and safe under concurrency.
3. Preserve easy extensibility for pricing and reservation features.
4. Keep Java/Python implementations structurally aligned across `v1 -> v3`.

---

## Requirements and Constraints Mapping

| Requirement | Design Choice |
|-------------|---------------|
| Multi-floor support | `ParkingLot` owns `List<Floor>` |
| Fast lookup by ticket/vehicle | Active maps keyed by ticket id and vehicle id |
| Spot compatibility | Policy/lookup on `VehicleType -> allowed SpotType(s)` |
| Fee flexibility | `PricingStrategy` interface |
| Concurrent entry/exit | Critical-section protection around allocation/release |

---

## Core Components

### `ParkingLot`
- Facade for `parkVehicle`, `unparkVehicle`, lookup, and availability APIs.
- Coordinates floors, active tickets, and pricing strategy.

### `Floor`
- Owns local spot pools and floor-level allocation/release.
- Provides availability by spot type.

### `ParkingSpot`
- Encapsulates occupancy state and compatibility checks.
- Guarantees one active vehicle at a time.

### `Ticket`
- Immutable identity + mutable lifecycle timestamps/status.
- Links vehicle and spot for billing/audit.

### `PricingStrategy`
- Computes fee from ticket lifecycle and policy inputs.
- Enables hourly/flat/tiered/dynamic policies without rewriting core entities.

---

## Suggested Class Skeleton (Conceptual)

```text
ParkingLot
  - floors: List<Floor>
  - activeTickets: Map<String, Ticket>
  - vehicleToTicket: Map<String, Ticket>
  - pricingStrategy: PricingStrategy
  + parkVehicle(vehicle): Ticket?
  + unparkVehicle(ticketId): PaymentResult
  + getAvailability(): AvailabilitySummary

Floor
  - spotsByType: Map<SpotType, Queue<ParkingSpot>>
  + allocate(vehicle): ParkingSpot?
  + release(spot)

PricingStrategy (interface)
  + calculate(ticket): Money
```

---

## Allocation Flow

1. Validate vehicle is not already parked.
2. Iterate floors (or floor-preference policy) and try compatible pools.
3. Atomically claim one spot.
4. Create active ticket and update indexes.

Release flow:
1. Resolve active ticket.
2. Compute fee via pricing strategy.
3. Release spot and clear indexes.
4. Mark ticket as closed.

---

## Data Structure Choices

1. Queue/pool by spot type for efficient assignment.
2. Maps for O(1) active ticket and parked-vehicle lookup.
3. Optional priority queue for reservation or premium allocation in extensions.
4. Counters per floor/type for fast display updates.

---

## Complexity Snapshot

- `parkVehicle`: `O(F)` baseline where `F = number of floors`.
- `unparkVehicle`: `O(1)` average via ticket map.
- `findVehicle`: `O(1)` average via index.

---

## Variants and Extensions

1. Reservation manager with TTL cleanup.
2. Dynamic pricing decorator over base fee strategy.
3. Multi-gate contention handling with per-floor locks/atomic counters.
4. EV charging sessions and blended parking + energy billing.

---

## Determinism Hooks

1. Keep allocation tie-breaking stable (floor and spot ordering).
2. Keep pricing calculations deterministic with injectable time source for tests.
3. Keep release path idempotent for duplicate exit scans.

---

## Cross-Links

- Interview flow: [APPROACH](./APPROACH.md)
- Code mapping: [CODE-WALKTHROUGH](./CODE-WALKTHROUGH.md)
- Evaluation: [RUBRIC](./RUBRIC.md)
- Failure modes: [PITFALLS](./PITFALLS.md)
- Extensions: [FOLLOW-UPS](./FOLLOW-UPS.md)
- Patterns reference: [01-design-patterns](../../01-design-patterns/README.md)
- Related project: [Elevator System](../elevator-system/DESIGN.md)
- Related project: [Amazon Locker](../amazon-locker/DESIGN.md)
