# Elevator System

## Problem Statement

Design an elevator control system for a multi-floor building that accepts hall/cabin requests, dispatches elevators, and runs safely under concurrent demand.

---

## Functional Requirements

1. Support multiple elevators and configurable floor count.
2. Accept hall calls (`UP` / `DOWN`) from floors.
3. Accept cabin destination requests from inside an elevator.
4. Dispatch requests to an appropriate elevator.
5. Move elevators one floor at a time with door open/close behavior at stops.
6. Maintain elevator state (`IDLE`, moving, door open, maintenance/emergency when enabled).
7. Expose elevator position, direction, and active requests for display/monitoring.
8. Allow elevators to be marked out-of-service and excluded from dispatch.

---

## Non-Functional Requirements

1. Deterministic request handling under concurrent button presses.
2. Fairness: avoid starvation for far-away floors.
3. Extensibility for dispatch strategies (SCAN/LOOK/priority).
4. Testability with clear public APIs and resettable singleton/system state.
5. Predictable performance for high-rise scenarios.

---

## Requirements and Constraints

- `N` floors and `M` elevators are runtime-configurable.
- Direction-aware dispatch is mandatory for baseline behavior.
- One elevator cannot serve two conflicting actions simultaneously (e.g., move while doors are open).
- Capacity/overload policy should be modeled even if simplified in `v1`.
- Requests should be representable as immutable command-like objects.
- Assume all floors are reachable unless maintenance rules state otherwise.

---

## API Signals Interviewers Expect

- `requestElevator(floor, direction)` for hall calls.
- `selectDestination(elevatorId, floor)` for cabin calls.
- `step()` or equivalent simulation tick for deterministic progression.
- Read APIs for elevator status and assigned/pending requests.

---

## Clarifying Questions to Ask Early

1. Is the objective average wait time, fairness, or throughput?
2. Should dispatch be global or zoned by floors?
3. Are express or VIP elevators in scope?
4. What are maintenance and emergency behaviors?
5. What concurrency level should we design for (single building controller vs distributed controllers)?
6. What observability is expected (display board only vs telemetry hooks)?

---

## 60-90 Second Answer

Say: "I would model the system as a facade `ElevatorSystem`, a set of `Elevator` objects that own movement and door state, immutable `Request` objects, and a pluggable `Dispatcher` strategy. The key split is that dispatch chooses which car gets a hall call, while each elevator owns its stop set and legal state transitions. I would expose `requestElevator`, `selectDestination`, and deterministic `step()` APIs so the design is testable without sleeps. The baseline can use a direction-aware SCAN or LOOK strategy, then extend to maintenance, emergency recall, VIP priority, and zone dispatch. The main risks are starvation, conflicting door/move states, and concurrent request intake, so I would add state guards, queue boundaries, and tests around deterministic ticks."

---

## Core Entities

| Entity | Responsibility |
|--------|----------------|
| `ElevatorSystem` | Coordinates elevators, request intake, and dispatch |
| `Elevator` | Owns movement state, stop list, door lifecycle |
| `Request` | Encapsulates hall/cabin request metadata |
| `Dispatcher` | Selects elevator based on strategy |
| `DispatchStrategy` | Algorithm plug-in (`SCAN`, `LOOK`, variants) |
| `Door` / `Display` | Optional collaborators for safety + observability |

---

## Variants and Extensions

1. Zone-based dispatch for 100+ floor buildings.
2. Peak-hour strategy switching (lobby-first morning mode).
3. Priority floors/VIP queues with starvation guards.
4. Emergency/fire recall mode with system-wide override.
5. Live display/monitoring via observer events.

---

## Version Roadmap

| Version | Scope |
|---------|-------|
| `v1-basic` | Core entities, single strategy, deterministic movement |
| `v2-extended` | Strategy plug-ins, richer edge-case handling, maintenance |
| `v3-optimized` | Better scheduling heuristics and monitoring hooks; concurrency boundaries are documented, but current sample operations are not fully thread-safe |

---

## Cross-Links

- LLD practice flow: [HOW-TO-APPROACH](../HOW-TO-APPROACH.md)
- Repo LLD index: [02-lld-projects README](../README.md)
- Pattern refresh: [01-design-patterns](../../01-design-patterns/README.md)
- Theory refresh: [00-theory](../../00-theory/README.md)
- Related project: [Parking Lot](../parking-lot/PROBLEM.md)
- Related project: [Amazon Locker](../amazon-locker/PROBLEM.md)
- Related project: [Connect Four](../connect-four/PROBLEM.md)
