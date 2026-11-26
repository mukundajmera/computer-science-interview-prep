# Strong Answer: Parking Lot

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Clarification (5 mins)
**Say:** "To design a multi-floor Parking Lot system, I'll start by clarifying the core functional and non-functional requirements. We need to ensure the system is extensible, highly concurrent, and deterministic under load."

**Explicit Clarifications:**
- **Vehicle Types:** We support multiple vehicle categories (e.g., Motorcycle, Car, Truck) and spot sizes (Compact, Regular, Large). A vehicle can only park in a spot that fits it (e.g., a Motorcycle can park in a Compact spot, but a Truck cannot).
- **Concurrency:** The system must handle concurrent entry and exit traffic from multiple gates. Spot allocation must avoid double-booking.
- **Pricing:** The fee calculation needs to be policy-driven (e.g., hourly vs. flat rate) and uncoupled from core domain objects like `Ticket`.

## 2. Entity Modeling and APIs (10 mins)
**Say:** "The primary entities in this system encapsulate our business rules, separating allocation, ticket lifecycle, and pricing concerns."

### Core Entities:
- `ParkingLot`: The main orchestrator/facade containing floors, active tickets, and pricing policies.
- `Floor`: Manages spot pools and local availability.
- `ParkingSpot`: Encapsulates occupancy state and spot compatibility.
- `Vehicle`: Represents the identity (license plate) and type of the vehicle.
- `Ticket`: The immutable entry/exit record tying a `Vehicle` to a `ParkingSpot` with timestamps.
- `PricingStrategy`: An interface to calculate fees, allowing flexible implementations without changing core classes.

### Primary APIs:
- `Ticket parkVehicle(Vehicle vehicle)`: Validates the vehicle, finds a compatible spot, atomically claims it, and generates a ticket.
- `PaymentResult unparkVehicle(String ticketId)`: Resolves the ticket, computes the fee via the pricing strategy, releases the spot, marks the ticket closed, and returns a payment summary.
- `int getAvailableSpots(VehicleType type)`: Returns current availability for display boards.

## 3. Design Alternatives and Trade-offs (10 mins)
**Say:** "Choosing the right data structures and concurrency mechanisms is critical for meeting our near-O(1) latency requirement for assignments and lookups."

- **Spot Allocation:**
  - *Alternative 1 (Linear Search):* Iterate all spots O(N) to find a free one. Too slow for a large lot.
  - *Alternative 2 (Free Lists / Queues per type):* O(1) assignment. We map `SpotType -> Queue<ParkingSpot>`. This is the preferred approach for fast assignments.
- **Lookups:**
  - We use `HashMap`s keyed by `ticketId` (to active ticket) and `licensePlate` (to active parked vehicle). This guarantees O(1) average lookup when unparking or finding a vehicle, avoiding scanning floors.
- **Pricing Extensibility:**
  - By using the **Strategy Pattern**, we can swap an `HourlyPricing` for `DynamicPricing` seamlessly.
- **System Facade:**
  - The `ParkingLot` acts as a facade, keeping internal complexity away from caller interfaces.

## 4. Correctness, Complexity, and Concurrency (10 mins)
**Say:** "A single-threaded design fails in production when multiple cars enter simultaneously. We must guarantee deterministic, thread-safe allocation."

**Concurrency Mechanisms:**
- To prevent double-booking, we must protect the spot pools. In a heavily loaded system, a global lock on `parkVehicle` is a bottleneck.
- **Optimized approach:** We can use concurrent collections (like `ConcurrentHashMap` for tickets) and per-floor or per-queue synchronization. When multiple vehicles try to park simultaneously, we use atomic operations (e.g., locking the spot queue, dequeuing, and changing spot state) to ensure exactly one vehicle gets the spot.

**Acceptance Guarantee (Barrier-Start Contenders):**
Consider a scenario where one free compatible spot remains, and eight cars attempt to enter simultaneously across different gates (barrier-start contenders). Our lock-protected allocation ensures exactly one active ticket and one vehicle assignment succeeds. The other seven fail gracefully (e.g., returning `null` or a "lot full" message).

## 5. Failure Handling and Edge Cases (10 mins)
**Say:** "We must ensure robust invariants during edge case scenarios."

**Reference Contracts for Edge Cases:**
- **Normal Use-Case:** A vehicle enters, requests a spot, receives a ticket mapping to an exact spot, occupies the spot, and later unparks by presenting the ticket, freeing the spot and paying the calculated fee.
- **Empty/Invalid Input:** Requests with `null` or missing vehicles are explicitly rejected. Invalid or already processed tickets during unpark are rejected gracefully (e.g., returning `-1` or `null`) without side effects.
- **Duplicate Operations:**
  - *Duplicate Park:* If a vehicle is already active in the lot (tracked by license plate), subsequent park requests are explicitly rejected (returning `null`) before claiming a new spot. If a spot is accidentally claimed concurrently, the transaction is rolled back, releasing the spot.
  - *Duplicate Unpark (Idempotency):* Repeated unpark attempts (e.g., double scanning) safely reject the duplicate request because the ticket is removed from active tracking on the first successful run, preventing double-release of the spot or negative capacity.
- **Capacity Bounds:** The system gracefully returns `null` or a clear failure when the lot is full or no spot is compatible with the `VehicleType`, preserving invariants without exceptions.
- **Failure Rollbacks:** If an operation fails mid-flight (e.g., in `v3-optimized` when a duplicate plate is detected during concurrent park), any provisionally claimed spot is explicitly unparked/released to prevent capacity leaks.

**Concrete Failure/Concurrency Discussion:**
- **Idempotency on Unpark:** Repeated unpark requests (e.g., scanning the ticket twice) must be idempotent. If the ticket is already marked closed, the system should reject the second attempt without crashing or releasing an already-freed/re-occupied spot. This preserves ticket, spot, and capacity invariants.
- **Invalid Inputs:** Duplicate license plates (a vehicle already parked trying to enter again), a full lot, or an invalid spot type request must be rejected safely. The system checks active maps before attempting allocation, ensuring invariants are preserved.
- **Failure Trace with Assumptions:** If a thread successfully claims a spot but crashes before creating a ticket (e.g., OutOfMemoryError), the spot might be leaked. A robust system might employ a sweeper/reservation TTL to reclaim spots claimed without a finalized ticket after a short threshold (e.g., 2 minutes). In our in-memory implementation, atomic blocks encompassing claim+ticket creation minimize this risk.

## 6. Wrap-Up and Version Evolution
**Say:** "This architecture directly supports extensions. To add reservations, we introduce a `ReservationManager` that holds spots temporarily without rewriting the core `parkVehicle` logic. For EV charging, we add a new `SpotType` and integrate an EV pricing strategy layer."

**Version-Specific Feature Deltas:**
- `v1-basic`: Core singleton `ParkingLot`, `VehicleType` spot compatibility, immutable `Ticket`, and `PricingStrategy` foundation.
- `v2-extended`: Introduces `PaymentMethod` processing, `Payment` records, and VIP spot reservations (`reserve_spot`).
- `v3-optimized`: Implements thread-safe concurrent allocation using explicit locking (`threading.Lock` in Python, `ConcurrentHashMap`/`CopyOnWriteArrayList` in Java), handling concurrent barrier-start contention to ensure exactly one ticket and assignment per free spot.

