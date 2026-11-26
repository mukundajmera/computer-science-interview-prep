# Interview Solution: Hotel Management System

## Verbal Pacing (45-minute guide)

### 1. Requirements & Scope (0 - 5 mins)
**Say:** "I will focus on the operational aspects of the hotel, not the pre-arrival booking system. The core functionalities include handling Housekeeping statuses, the Check-in and Check-out workflows, Room Key issuance, and Folio Ledger operations. I will make sure the system handles concurrent updates to the folio and prevents double-booking a physical room during simultaneous check-ins."

### 2. Entity Modeling (5 - 15 mins)
**Say:** "I'll model the primary entities: `Room`, `Stay`, `Folio`, `Charge`, and `RoomKey`.
- **Room**: Physical room containing ID, Type, Occupancy status, and a strict HousekeepingStatus (`DIRTY`, `CLEAN`, `INSPECTED`).
- **Stay**: Links the Guest, `Room`, `Folio`, and active `RoomKey`s.
- **Folio**: Financial ledger aggregating `Charge` line items and maintaining a balance.
- **RoomKey**: Represents a physical/digital token."

### 3. Design Patterns (15 - 25 mins)
**Say:** "I will use the **State Pattern** for the room's Housekeeping status, enforcing transitions from `DIRTY` to `CLEAN` to `INSPECTED`. The room cannot be checked into unless it is `INSPECTED`. I will also use an **Observer Pattern** to simulate notifying the housekeeping department when a room is marked `DIRTY` upon checkout."

### 4. Concurrency Defense & Thread Safety (25 - 35 mins)
**Say:** "Concurrency is a critical challenge. 
First, for **Room Assignment**: Two agents might try to assign the same `INSPECTED` room. I will implement a check-and-set using fine-grained locks or a concurrent `Queue`/`Set` of available rooms to ensure atomic allocation without locking the entire hotel structure.
Second, for the **Folio Ledger**: Multiple microservices (e.g., room service, minibar, spa) might post a `Charge` simultaneously. The `Folio` will encapsulate its state using a `ReentrantLock` (Java) or `threading.Lock` (Python), ensuring that adding charges and processing payments do not lead to lost updates or invalid balances."

### 5. Failure Handling & Production Trade-offs (35 - 45 mins)
**Say:** "For failure handling, consider what happens if encoding a physical `RoomKey` fails. The `checkIn` operation must be transactional; if key issuance fails, we must rollback the room occupancy status and stay creation, returning the room to the available pool.
For production trade-offs, scaling this to thousands of rooms means an in-memory lock will become a bottleneck. We trade off strict real-time consistency for availability by partitioning the data by property or wing, and using a distributed cache (like Redis) with distributed locks for room allocation. For the Folio, an event-driven architecture using an event bus (like Kafka) to process charges asynchronously provides better fault tolerance."
