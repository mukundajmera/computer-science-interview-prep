# Design Approach for Elevator System

A step-by-step thought process for designing the elevator system.

---

## Step 1: Identify Core Entities

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Elevator | ✅ Yes | Moving car |
| Floor | ✅ Yes | Building level |
| Button | ✅ Yes | Input mechanism |
| Request | ✅ Yes | Pickup/destination |
| Door | ✅ Yes | Entry/exit point |
| Display | ❌ No | Part of elevator |
| Dispatcher | ✅ Yes | Assignment logic |
| Building | ✅ Yes | Container |

**Final Entities**: ElevatorSystem, Elevator, Floor, Request, Button, Door, Dispatcher

---

## Step 2: Define Relationships

Use the relationships to keep assignment decisions out of the moving car object.

```
ElevatorSystem (1) ──manages──> (n) Elevator
ElevatorSystem (1) ──has──> (n) Floor  
Elevator (1) ──processes──> (n) Request
Floor (1) ──has──> (2) Button (up/down)
ElevatorSystem (1) ──uses──> (1) Dispatcher
```

---

## Step 3: Choose Design Patterns

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Singleton** | ⚠️ Demo-only | A sample may expose one `ElevatorSystem` per building, but production/interview design should prefer an injected facade/controller for testability and multi-building simulation |
| **State** | ✅ Yes | Elevator states (IDLE, MOVING_UP, MOVING_DOWN) |
| **Strategy** | ✅ Yes | Different scheduling algorithms |
| **Observer** | ✅ v2 | Floor display updates |
| **Command** | 🔄 Optional | Request as command objects |

### Pattern Application:

1. **State Pattern** - Elevator
   - IDLE → can accept any request
   - MOVING_UP → prioritizes up requests
   - MOVING_DOWN → prioritizes down requests

2. **Strategy Pattern** - Dispatcher
   - FCFS (First Come First Serve)
   - SCAN (Elevator algorithm)
   - LOOK (Optimized SCAN)

3. **Observer Pattern** - Floor displays
   - Notify displays when elevator position changes

---

## Step 4: Design Classes

### ElevatorSystem (Facade / Controller)
- **Attributes**: 
  - `elevators: List<Elevator>`
  - `floors: List<Floor>`
  - `dispatcher: Dispatcher`
- **Methods**:
  - `requestElevator(floor, direction): void`
  - `selectDestination(elevatorId, floor): void`
  - `step(): void` - Move simulation

Interview stance: avoid leading with Singleton as the design pattern. If the sample code has a single system instance, call it a composition root or demo convenience. Keep `Dispatcher` injectable so tests can swap FCFS/SCAN/LOOK strategies and so a future building-management simulator can host many independent elevator systems.

### Elevator
- **Attributes**:
  - `id: int`
  - `currentFloor: int`
  - `state: ElevatorState`
  - `destinationQueue: Set<Integer>`
  - `door: Door`
- **Methods**:
  - `move(): void`
  - `addDestination(floor): void`
  - `openDoor(): void`
  - `closeDoor(): void`

### Request
- **Attributes**:
  - `sourceFloor: int`
  - `destinationFloor: int`
  - `direction: Direction`
  - `timestamp: long`
- **Methods**:
  - `getDirection(): Direction`

### Dispatcher (Strategy Interface)
- **Methods**:
  - `selectElevator(request, elevators): Elevator`
- **Implementations**:
  - `FCFSDispatcher` - Nearest available
  - `SCANDispatcher` - Based on direction
  - `LOOKDispatcher` - Optimized SCAN

---

## Step 5: Handle Edge Cases

### Input Validation:
- Invalid floor number
- Request when already at floor
- Request outside building range

### Business Logic:
- All elevators busy
- Elevator at capacity
- Maintenance mode
- Emergency stop

### Concurrency (v3):
- Simultaneous floor requests
- Multiple destination selections
- Elevator state changes

---

## Step 6: Optimization Opportunities

### Scheduling Algorithms:
| Algorithm | Pros | Cons |
|-----------|------|------|
| FCFS | Simple | Long wait times |
| SCAN | Fair | May go to empty floors |
| LOOK | Efficient | More complex |

### Data Structures:
- `TreeSet` for sorted destination queue
- `PriorityQueue` for pending requests

---

## Step 7: Elevator States

State transitions should make illegal door and movement combinations impossible.

```
         ┌─────────────┐
         │    IDLE     │
         └──────┬──────┘
                │ Request received
         ┌──────┴──────┐
         ▼             ▼
   ┌───────────┐ ┌───────────┐
   │ MOVING_UP │ │MOVING_DOWN│
   └─────┬─────┘ └─────┬─────┘
         │             │
         │  All done   │
         └──────┬──────┘
                ▼
         ┌─────────────┐
         │    IDLE     │
         └─────────────┘
```
