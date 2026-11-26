# Strong Answer: Elevator System

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Clarification (5 mins)
**Say:** "To design an Elevator System, I'll start by clarifying the core functional and non-functional requirements. We need to ensure the system is extensible, handles concurrent requests safely without data loss, and avoids starvation while minimizing wait times."

**Explicit Clarifications:**
- **Dispatching Algorithm:** We will use the SCAN (Elevator algorithm) approach, where the elevator moves continuously in one direction as long as there are requests, rather than First-Come-First-Serve (FCFS).
- **Concurrency:** The system must handle concurrent request intake and coordinate state progression deterministically. Request submission concurrent with a step must never lose an accepted request or expose a partially updated floor/direction/door state.
- **Failures and Maintenance:** We must support bounded request-drain shutdown and emergency/maintenance states.
- **Capacity/Scale:** We assume multiple elevators in a building, requiring a dispatcher to choose the optimal elevator.

## 2. Entity Modeling and APIs (10 mins)
**Say:** "The primary entities encapsulate our dispatching rules and state machine transitions, separating the request intake from the physical elevator movement."

### Core Entities:
- `ElevatorSystem`: The main orchestrator/facade containing the elevators, pending request queue, and the global dispatching logic.
- `Elevator`: Encapsulates the car state (`currentFloor`, `direction`, `ElevatorState`, `DoorState`) and its set of destinations.
- `Request`: An immutable object representing a hall or cabin call (floor and direction).
- `Dispatcher` / `DispatchStrategy`: (For optimized versions) Strategies to encapsulate selection policy.

### Primary APIs:
- `void requestElevator(int floor, Direction direction)`: Validates the request, selects the best elevator, and assigns it. If no elevator is suitable, it queues the request.
- `void selectDestination(int elevatorId, int floor)`: Internal request from inside the cabin.
- `void step()`: Deterministic simulation tick that progresses the state of all elevators safely.

## 3. Design Alternatives and Trade-offs (10 mins)
**Say:** "Choosing the right data structures is critical for safe concurrency and optimal routing."

- **Data Structure for Destinations:** A simple `ArrayList` or `HashSet` is insufficient. We use a `ConcurrentSkipListSet<Integer>` in Java. 
  - *Why?* It inherently keeps destinations sorted for efficient floor traversal `O(log N)` for the SCAN algorithm, prevents duplicate destinations, and provides thread-safe concurrent modifications.
- **Dispatching Algorithm:** 
  - *FCFS:* Leads to high wait times and unnecessary reversal.
  - *Nearest Car:* Absolute distance ignores direction, causing inefficient routing.
  - *SCAN/LOOK:* Maintains current direction until all requests in that direction are fulfilled. LOOK optimizes by reversing at the last request instead of the boundary floor.

## 4. Correctness, Complexity, and Concurrency (15 mins)
**Say:** "Let's discuss how we guarantee deterministic behavior, especially regarding edge cases and concurrency."

### Correctness:
- **Duplicate Destinations:** Automatically handled by the Set-based destination tracking.
- **Boundary Floors & Out-of-range:** Validated at the intake API boundary (`isValidFloor`).
- **Direction Reversal:** The elevator explicitly updates its direction when `destinations.higher()` or `lower()` returns null, smoothly reversing to handle remaining requests.

### Concurrency and Safety (Concrete Failure Discussion):
**The Problem:** If `step()` reads an elevator's state while it is concurrently accepting a new request, it might observe a partially updated floor/direction/door state or skip a request.
**The Solution:** 
1. **Intake Queueing:** We use a `ConcurrentLinkedQueue` for pending requests when all elevators are busy.
2. **State Protection:** Request submission concurrent with a step must be synchronized. By using a deterministic simulation `step()` and atomic state transitions (e.g., using locks on the Elevator object during assignment and movement), we ensure that a request is never lost and intermediate states (like a door opening while moving) are never exposed. 
3. **Bounded Request-Drain Shutdown:** When transitioning to Maintenance, the elevator stops accepting new requests, drains its `ConcurrentSkipListSet` of current destinations, and then transitions to out-of-service.

## 5. Extensions and Wrap-up (5 mins)
**Say:** "In a production environment, we could extend this with Zone Dispatching for high-rises or Peak-Hour strategies."
