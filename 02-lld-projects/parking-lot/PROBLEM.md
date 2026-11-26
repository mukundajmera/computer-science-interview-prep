# Parking Lot System

## Problem Statement

Design a multi-floor parking lot system that allocates compatible spots, issues tickets, calculates charges on exit, and remains correct under concurrent entry/exit traffic.

---

## Functional Requirements

1. Support multiple vehicle categories and compatible spot rules.
2. Allocate a valid spot when a vehicle enters.
3. Generate ticket at entry and close ticket at exit.
4. Compute parking fee from ticket timing and pricing policy.
5. Track available spots by floor and spot type.
6. Prevent duplicate parking for the same vehicle.
7. Support vehicle lookup by ticket id or license plate.
8. Expose capacity and occupancy metrics.

---

## Non-Functional Requirements

1. Deterministic spot allocation under concurrent requests.
2. O(1) or near-O(1) lookup for active ticket and parked vehicle location.
3. Extensible pricing policies (hourly/flat/tiered/dynamic).
4. Clean support for new spot types and reservation/payment variants.
5. Testable design with clear boundaries and predictable behavior.

---

## Requirements and Constraints

- Floors and per-type spot counts are configurable.
- Spot compatibility policy must be explicit (for example, motorcycle in compact allowed/not allowed).
- Allocation must avoid double-booking.
- Ticket lifecycle should be explicit (`ACTIVE`, `PAID`, `CANCELLED/LOST` as needed).
- Fee calculation should be policy-driven, not embedded in entity objects.
- Baseline scope excludes external payment gateway integration details.

---

## Clarifying Questions to Ask Early

1. What vehicle categories and spot compatibility rules are required?
2. Is nearest-floor preference required, or any-first available spot?
3. Which pricing model is in scope now vs future?
4. How many entry/exit gates and what concurrency load?
5. Should reservations or EV charging be included in base scope?
6. What should happen for lost/invalid tickets?

---

## Core Entities

| Entity | Responsibility |
|--------|----------------|
| `ParkingLot` | Orchestrates floors, ticket lifecycle, and pricing policy |
| `Floor` | Owns spot pools and local allocation |
| `ParkingSpot` | Occupancy + compatibility checks |
| `Vehicle` | Type + identity |
| `Ticket` | Entry/exit timestamps and assignment |
| `PricingStrategy` | Fee calculation policy |

---

## Variants and Extensions

1. Reservation flow with expiry windows.
2. Dynamic pricing based on occupancy/time-of-day.
3. Multi-gate distributed allocation counters.
4. EV charging spots and charging-session fees.
5. Subscription/monthly-pass handling.

---

## Version Roadmap

| Version | Scope |
|---------|-------|
| `v1-basic` | Core park/unpark flow with deterministic fee policy |
| `v2-extended` | Reservation/payment variants and richer policies |
| `v3-optimized` | Thread-safe allocation and operational scaling hooks |

---

## Cross-Links

- LLD practice flow: [HOW-TO-APPROACH](../HOW-TO-APPROACH.md)
- Repo LLD index: [02-lld-projects README](../README.md)
- Pattern refresh: [01-design-patterns](../../01-design-patterns/README.md)
- Theory refresh: [00-theory](../../00-theory/README.md)
- Related project: [Elevator System](../elevator-system/PROBLEM.md)
- Related project: [Amazon Locker](../amazon-locker/PROBLEM.md)
- Related project: [Connect Four](../connect-four/PROBLEM.md)
