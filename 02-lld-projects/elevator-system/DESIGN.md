# Design for Elevator System

## Design Goals

1. Separate request intake, dispatch decision, and car movement.
2. Keep dispatch algorithm swappable without rewriting core entities.
3. Enforce valid elevator state transitions.
4. Support deterministic simulation (`step`) and make the concurrency boundary explicit for future hardening.

---

## Requirements and Constraints Mapping

| Requirement | Design Choice |
|-------------|---------------|
| Multi-elevator dispatch | `ElevatorSystem` + `Dispatcher` over `List<Elevator>` |
| Direction-aware assignment | `DispatchStrategy` computes candidate score |
| Safe movement | `ElevatorState` + `DoorState` transitions |
| Concurrency readiness | Current examples are deterministic and single-process; production hardening would lock request intake, assignment, and tick progression |
| Extensibility | Strategy/Observer hooks; request model remains stable |

---

## Core Components

### `ElevatorSystem`
- System facade for request APIs.
- Owns elevator registry, request queue(s), dispatcher, and simulation clock/tick.
- Coordinates assignment and movement steps.

### `Elevator`
- Owns car state: `currentFloor`, `direction`, `state`, destination set.
- Exposes operations like `addDestination`, `moveOneStep`, `openDoor`, `closeDoor`.
- Does not choose which hall request to accept globally.

### `Request`
- Immutable request object (source, optional destination, direction, timestamp/sequence).
- Can represent hall or cabin requests via request type or nullable destination.

### `Dispatcher` + `DispatchStrategy`
- Dispatcher orchestrates assignment using active strategy.
- Strategies encapsulate selection policy (`SCAN`, `LOOK`, priority variants).

---

## Suggested Class Skeleton (Conceptual)

This sketch describes ownership boundaries, not a complete thread-safe implementation.

```text
ElevatorSystem
  - elevators: List<Elevator>
  - dispatcher: Dispatcher
  - pendingRequests: Queue<Request>
  + requestElevator(floor, direction)
  + selectDestination(elevatorId, floor)
  + step()

Dispatcher
  - strategy: DispatchStrategy
  + assign(request, elevators): Elevator?

DispatchStrategy (interface)
  + select(request, elevators): Elevator?

Elevator
  - currentFloor: int
  - direction: Direction
  - state: ElevatorState
  - destinations: SortedSet<int>
  + addDestination(floor)
  + moveOneStep()
```

---

## State Model

- `IDLE` -> `MOVING_UP` / `MOVING_DOWN`
- `MOVING_*` -> `DOOR_OPEN` at stop floors
- `DOOR_OPEN` -> `IDLE` (no work) or back to movement
- `ANY` -> `MAINTENANCE` / `EMERGENCY` when triggered

Invalid transitions (must be blocked):
- Moving while door is open.
- Accepting new assignments while out-of-service.

---

## Data Structure Choices

1. `SortedSet`/ordered stop container for directional serving.
2. Queue for pending hall calls to preserve fairness baseline.
3. Map by elevator id for O(1) target lookup on cabin requests.
4. Optional priority queue in variants (VIP/aged requests).

---

## Complexity Snapshot

- Assign request: `O(E)` where `E = number of elevators`.
- Insert destination: `O(log D)` where `D = destinations per elevator`.
- Tick step across system: `O(E + R_assign)`.

---

## Variants and Extensions

1. Zone-aware dispatcher for high-rise buildings.
2. Time-window strategy switching (peak-hour up/down modes).
3. Priority/aging policy to reduce starvation.
4. Observer stream for floor displays and monitoring dashboards.
5. Distributed controller partitioning by zone (advanced).

---

## Determinism Hooks

1. Keep a deterministic `step()` loop as the default simulation contract.
2. Avoid wall-clock sleeps in tests; advance state through explicit ticks.
3. Keep request ordering stable for same-floor/same-direction bursts.

---

## Cross-Links

- Interview flow: [APPROACH](./APPROACH.md)
- Code mapping: [CODE-WALKTHROUGH](./CODE-WALKTHROUGH.md)
- Evaluation: [RUBRIC](./RUBRIC.md)
- Failure modes: [PITFALLS](./PITFALLS.md)
- Extensions: [FOLLOW-UPS](./FOLLOW-UPS.md)
- Patterns reference: [01-design-patterns](../../01-design-patterns/README.md)
- Theory reference: [00-theory](../../00-theory/README.md)
