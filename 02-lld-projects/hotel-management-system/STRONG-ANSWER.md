# Strong Answer Guide: Hotel Management System

## Overview
This guide provides the necessary structure and talking points to deliver a comprehensive 45-minute verbal design interview for the Hotel Management System. It strictly covers concurrency defense, data structure rationale, failure handling, and production trade-offs without generic placeholders.

## 1. Requirement Scoping & Pacing (0 - 5 mins)
Begin by distinguishing this system from a standard reservation engine.
**Say:** "I will focus on the operational backbone of the hotel. This means we are managing real-time, on-site state. Our primary workflows are Housekeeping state transitions (`DIRTY` -> `CLEAN` -> `INSPECTED`), the Check-in/Check-out lifecycle, Room Key issuance, and Folio Ledger operations. I will not focus on future availability searches, but rather on the immediate execution of a guest stay."

Identify the critical bottlenecks immediately.
**Say:** "The most critical components requiring concurrency defense are the Folio Ledger—where multiple asynchronous services (restaurant, spa, minibar) might post charges simultaneously—and the room allocation phase during check-in to prevent double-booking a physical room."

## 2. Entity Modeling & Data Structures (5 - 15 mins)
Outline the entities with precision.
**Say:** "The core entities include `Room`, `Stay`, `Folio`, `Charge`, and `RoomKey`. 
- **Room**: Contains an ID, Type, Occupancy status (boolean), and Housekeeping status (Enum). I will model the Housekeeping status as a strict state machine to prevent invalid transitions.
- **Stay**: Acts as the aggregate root for an active guest session. It holds a reference to the `Room`, the guest details, a `Folio`, and a list of active `RoomKey`s.
- **Folio**: The financial ledger. It contains a list of `Charge` objects and a running balance.
- **RoomKey**: Represents the physical or digital access token, containing an ID, the associated Room ID, and an active boolean flag.

For data structures, I'll use `ConcurrentHashMap` to maintain the active `Rooms` and `Stays` in memory for rapid lookup. The `Folio` will wrap its internal state with a `ReentrantLock` (Java) or `threading.Lock` (Python) to prevent race conditions during concurrent charge postings. For rapid room assignment during check-in, I will maintain an `availableRooms` set grouped by `RoomType`."

## 3. Concurrency Defense & State Synchronization (15 - 25 mins)
This section is critical for an LLD interview.
**Say:** "Let's deep dive into concurrency defense based on the codebase implementation. 
First, **Room Allocation**: During a busy check-in period, multiple receptionists might query for an `INSPECTED` room of a specific type. If we simply scan all rooms, a race condition exists. To defend against this, we use an `availableRooms` lookup structure. We fetch an available room ID, then acquire a fine-grained `ReentrantLock` on that specific room object. We verify it's still `INSPECTED` and unoccupied before proceeding.

Second, **Folio Billing**: A guest might check out at the front desk while simultaneously, a delayed batch-processing job from the minibar attempts to post a charge. To prevent a race condition where a guest pays 0 but a charge is added milliseconds later, the `checkOut` method must first remove the stay from the `activeStays` concurrent map. Only after removal does it lock the Folio and verify the balance is 0. If the balance is > 0, the stay is placed back into the map and an exception is thrown. This guarantees no new charges can be posted via `activeStays.get()` while we are checking out."

## 4. Failure Handling & Edge Cases (25 - 35 mins)
Address systemic failures and operational anomalies.
**Say:** "In a physical system, failure handling is paramount. What happens if a room key fails to encode after the system has marked the room as occupied?
We must use distributed transactions or a Saga pattern if external systems (like the key encoder hardware) are involved. If the key encoder fails, we must execute a compensating transaction to roll back the `Stay` creation, mark the room as unoccupied, and return the room to the `availableRooms` pool.

Furthermore, consider the edge case of a lost key. When a new key is issued, the system must not only create a new `RoomKey` record but must push an invalidation event for the old key ID to the hardware lock system to prevent unauthorized access."

## 5. Production Trade-offs & Scaling Limits (35 - 45 mins)
Conclude with architectural trade-offs, calculating realistic scenario assumptions.
**Say:** "While an in-memory implementation is suitable for a single, small hotel, scaling this to a massive resort with thousands of rooms requires trade-offs. 
**Scaling Limits Assumptions**: Assume a massive mega-resort with 5,000 rooms. At peak check-out time (11:00 AM), we might process 2,500 checkouts in an hour, which is roughly 0.7 checkouts per second. Lock contention on a monolithic map is not the primary bottleneck at this low throughput; however, database lock contention could occur if all front desks update the same tables simultaneously.
**Trade-off:** We can partition the data by physical building or wing to reduce blast radius.
**Indexing Trade-offs:** For housekeeping, staff need to query rooms by status. We maintain the `availableRooms` index specifically for `INSPECTED` rooms. Maintaining similar indexes for `DIRTY` rooms would increase write overhead (lock churn) every time a status changes. The trade-off is accepting slower read queries for housekeeping dashboards in exchange for fast, concurrent check-ins.
Finally, for the Folio ledger, relying entirely on real-time synchronous billing for external systems (like a third-party restaurant) is fragile. We trade strict real-time consistency for availability by using an event-driven architecture, where charges are pushed to an event bus (like Kafka) and consumed by the Folio service asynchronously."
