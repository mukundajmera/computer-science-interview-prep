# Code Walkthrough

## v1-basic
The v1 implementation focuses on the core domain models and basic workflows without complex thread-safety mechanisms.
- Defines basic `Room`, `Stay`, `Folio`, `Charge`, and `RoomKey` classes.
- The `HotelManager` class handles synchronous, single-threaded check-ins, check-outs, and charge postings.
- Simple enums for `HousekeepingStatus` (`CLEAN`, `DIRTY`, `INSPECTED`) and `RoomType`.

## v2-extended
The v2 implementation introduces concurrency controls and robust thread handling.
- **Folio Concurrency**: Adds a `ReentrantLock` (Java) or `threading.Lock` (Python) to the `Folio` and `Room` classes to ensure thread-safe operations.
- **Room Allocation**: Uses `ConcurrentHashMap` for rooms and active stays. Protects `checkIn` with fine-grained room locks, though it still iteratively searches through all rooms.
- **Check-out Workflow**: Ensures a room's active stay cannot be concurrently billed by acquiring folio and room locks sequentially.

## v3-optimized
The v3 implementation optimizes performance by reducing lock contention and lookup times.
- **Available Room Indexing**: Uses a concurrent `availableRooms` set grouped by `RoomType`. This eliminates the need to scan all rooms during `checkIn`.
- **Lock ordering during Check-Out**: In Java v3, the active stay is removed from `activeStays` map *before* validating the folio balance, placing it back if balance is non-zero, to prevent race conditions where a concurrent `postCharge` occurs during `checkOut`.
- **Thread-safe Key Lists**: Replaces standard array lists with `CopyOnWriteArrayList` in Java to prevent `ConcurrentModificationException` when keys are issued concurrently with read operations.
