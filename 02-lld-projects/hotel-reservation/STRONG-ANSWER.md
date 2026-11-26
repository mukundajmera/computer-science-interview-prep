# Strong Interview Answer: Hotel Reservation System

## ⏱️ 45-Minute Pacing Target

1. **Requirements & Scope (5 mins):** Align on date ranges, room types, capacities, payment options, and the single-hotel scope constraints.
2. **Entity Modeling & Inventory (10 mins):** Define `Hotel`, `Room`, `Reservation`, and especially the `RoomInventory` date-based tracking mechanism for precise availability queries.
3. **Core Logic & Booking Correctness (15 mins):** Prevent double bookings and manage state transitions (`PENDING`, `CONFIRMED`, `CHECKED_IN`, `CHECKED_OUT`, `CANCELLED`), enforcing explicit reference contracts for boundary cases.
4. **State and Pricing Design (5 mins):** Integrate `PricingStrategy` (e.g., Seasonal or Weekend) and cancellation policy edge cases.
5. **APIs, Complexity & Trade-offs (10 mins):** Define public APIs, discuss complexity (O(R x D) search), and discuss `v3` thread-safety (ReadWriteLocks/RLocks) and scaling design alternatives.

## 🗣️ Interview Script

### 1. Requirements Clarification
**Say:** "I will focus on the single-hotel reservation lifecycle. The system must track per-room-night availability and explicitly validate date ranges and capacity. I will ensure we handle cancellation policies logically, refunding either partially or fully depending on the 24-hour cutoff."

### 2. Entity Modeling & APIs
**Say:** "I'll model `Hotel`, `Room`, `Guest`, and `Reservation`. Rather than iterating over complex date overlap logic dynamically for every room, I would logically design a `RoomInventory` concept that tracks day-by-day availability, making queries significantly faster. Our code validates availability before confirming the booking by iterating through reservations and checking for overlap (`!checkOut.isBefore(res.getCheckInDate()) && !checkIn.isAfter(res.getCheckOutDate())`).

The core public APIs are:
*   `searchAvailableRooms(checkIn, checkOut, type)`: Returns a list of available rooms.
*   `makeReservation(guest, room, checkIn, checkOut)`: Creates a reservation, validating inputs (e.g. empty inputs or capacity boundary).
*   `checkIn(reservationId)` and `checkOut(reservationId)`: Handles guest arrival/departure.
*   `cancelReservation(reservationId)`: Processes cancellation and refunds."

### 3. Core Booking Correctness & Boundary Constraints
**Say:** "To book a room, we first check if it is available across the entire date range. If valid, we create a `Reservation` in a `PENDING` state and calculate the total amount. A payment confirmation transitions it to `CONFIRMED`. On arrival, it transitions to `CHECKED_IN`, updating the physical `RoomStatus` to `OCCUPIED`. When they leave, it becomes `CHECKED_OUT`, and the room moves to `CLEANING`. If they cancel, it moves to `CANCELLED` and triggers the refund policy.

We explicitly enforce reference contracts:
*   **Empty/Invalid Input:** Date range must be valid (checkout > checkin).
*   **Duplicate Operation:** Trying to double book the same room is prevented.
*   **Capacity Boundary:** Trying to exceed room capacity will be rejected.
*   **Failure Rollback:** If a transaction fails mid-booking, the room is released back to inventory."

### 4. Pricing Strategies & Complexity
**Say:** "I'll use the **Strategy Pattern** for pricing. We define a `PricingStrategy` interface with implementations like `StandardPricing`, `SeasonalPricing`, or `WeekendPricing`. This separates the pricing logic from the room and reservation, allowing dynamic rates without modifying core entities.

For **Complexity Analysis**:
*   **Time Complexity**: `searchAvailableRooms` is O(R × D) where R=rooms, D=days in range. `makeReservation` is O(D) to block days.
*   **Space Complexity**: `RoomInventory` is O(R × 365) to store daily availability for a year."

### 5. Design Alternatives, Failure & Concurrency Discussion
**Say:** "In a concurrent environment (like our `v3-optimized` design), preventing double booking is the primary challenge. 
If two users try to book the last available room for the same dates simultaneously, a race condition occurs.
I will mitigate this by using a `ReentrantReadWriteLock` (Java) or `threading.RLock` (Python) during the booking phase. We lock the inventory, perform a double-check on availability, and create the reservation atomically.
If the check fails during the locked phase, we explicitly reject the request (e.g., throw `RoomNotAvailableException`).

**Design Alternative:** We could use optimistic locking (versioning the room state) rather than pessimistic locking (RLocks). Optimistic locking is often better for read-heavy workloads where conflicts are rare, but for a hotel with scarce high-value inventory, pessimistic locking prevents the frustrating UX of 'booking failed at the last step.' For production scale across multiple hotels, we would move this locking to the database level using ACID transactions or distributed locks."
