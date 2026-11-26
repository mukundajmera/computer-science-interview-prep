# Code Walkthrough: Elevator System

## Overview

This walkthrough ties the conceptual model in [DESIGN](./DESIGN.md) to the Java/Python implementations and explains how interviewers typically evaluate the flow.

---

## Requirements and Constraints Trace

| Requirement | Where it appears in code |
|-------------|--------------------------|
| Hall + cabin requests | System-level request intake APIs |
| Direction-aware dispatch | `Dispatcher` + strategy implementation |
| Safe movement | `Elevator` state transition checks |
| Deterministic progression | `step()`-style simulation cycle |
| Extensibility | Strategy interface + versioned `v1 -> v3` folders |

---

## End-to-End Flow

### 1. Hall call

1. Floor panel triggers `requestElevator(floor, direction)`.
2. System validates floor bounds and request dedup policy.
3. Dispatcher evaluates elevators using active strategy.
4. Selected elevator receives destination insertion.
5. If no elevator qualifies immediately, request enters pending queue.

### 2. Cabin destination

1. Passenger inside elevator triggers `selectDestination(elevatorId, floor)`.
2. System resolves elevator by id.
3. Elevator updates ordered destination set.

### 3. Simulation tick

1. System assigns queued hall requests where possible.
2. Each elevator executes one movement step.
3. Elevator opens/closes doors at stop floors and updates state.
4. Display/observer hooks can publish floor + direction updates.

---

## Version Progression

| Version | Interview signal |
|---------|------------------|
| `v1-basic` | Correct object model and movement lifecycle |
| `v2-extended` | Better separation for strategy/state and richer edge handling |
| `v3-optimized` | Better scheduling and operational hooks; production thread safety would require serialized request intake and locked tick progression |

---

## Pattern Usage Anchors

1. `Strategy`: dispatch behavior changes without modifying `Elevator`.
2. `State`: invalid transitions are blocked by explicit elevator states.
3. `Observer` (optional extension): decoupled status display/monitoring.
4. `Command-like request objects`: immutable intake payloads.

---

## Common Interview Talking Points

1. Why direction matters more than absolute distance in dispatch.
2. How starvation is controlled (SCAN/LOOK/aging).
3. Production hardening path: global dispatcher lock vs per-elevator lock vs single-threaded event loop.
4. Failure modes: out-of-service elevator, overloaded car, emergency stop.
5. Testing strategy: deterministic tick-based tests without `sleep`.

---

## Variants and Extension Hooks

1. Add `PriorityDispatchStrategy` for VIP floors.
2. Add `TrafficMonitor` that switches strategy at peak windows.
3. Add `Zone` abstraction for high-rise scaling.
4. Add telemetry event publisher for monitoring systems.

---

## Testability Checklist

1. Keep dispatcher logic side-effect free where possible for unit tests.
2. Verify invariants after each tick: floor bounds, direction validity, and door-state safety.
3. Add deterministic regression tests for tie-breaking when two elevators have equal scores.

---

## Cross-Links

- Problem framing: [PROBLEM](./PROBLEM.md)
- Design details: [DESIGN](./DESIGN.md)
- Scoring expectations: [RUBRIC](./RUBRIC.md)
- Mistakes to avoid: [PITFALLS](./PITFALLS.md)
- Follow-up variants: [FOLLOW-UPS](./FOLLOW-UPS.md)
- Related LLD project: [Parking Lot](../parking-lot/PROBLEM.md)

## Compilation and Execution

To compile and run the project for any version (e.g., v1-basic), use the following commands from the root directory of the project:

### Compile
```bash
find java/v1-basic -name '*.java' | xargs javac -encoding UTF-8 -d out
```

### Run
```bash
java -cp out ElevatorDemo
```
