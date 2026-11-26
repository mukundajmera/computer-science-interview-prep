# Rubric

## 1. Domain Modeling (L4 - L5)
- **L5 (Senior)**: Distinctly models Housekeeping, Check-in/out, Folio Ledger, and Room Keys. Understands that a `Stay` is an aggregate root that manages the lifecycle of a guest session.
- **L4 (Beginner)**: Basic functionality works, but might merge Folio and Stay or fail to distinguish between a Reservation (future) and a Stay (current).

## 2. Check-in/Check-out Workflow (L4 - L6)
- **L6 (Staff)**: Explains the exact failure trace if a room key fails to encode after the room is marked occupied (e.g., requires compensating transactions).
- **L5 (Senior)**: Strictly enforces that rooms must be `INSPECTED` to check-in. Check-out marks rooms `DIRTY` and deactivates all linked `RoomKey`s.
- **L4 (Beginner)**: Checks in guests and checks out, but misses edge cases like key deactivation or room status progression.

## 3. Financial/Ledger Integrity (L4 - L5)
- **L5 (Senior)**: Uses thread-safe operations for `Folio` charges. Validates that `Folio` balance must be 0 to check out and handles concurrent billing during checkout.
- **L4 (Beginner)**: Maintains a ledger but lacks concurrency control for simultaneous charges. Might just use an integer addition without tracking `Charge` items.

## 4. Concurrency & Thread Safety (L4 - L7)
- **L7 (Staff)**: Explains scaling limits (e.g., monolithic lock contention at 11:00 AM) and proposes partitioning by wing/building. Uses indexed structures (like `availableRooms`) to optimize `checkIn`.
- **L6 (Staff)**: Demonstrates failure trace where a `postCharge` arrives during a `checkOut`, and correctly orders map removal and locks to prevent phantom charges.
- **L5 (Senior)**: Uses appropriate fine-grained locking (`ReentrantLock` per room/folio) instead of global manager locks.
- **L4 (Beginner)**: Minimal thread safety, possibly relying on global `synchronized` methods, causing bottlenecks.
