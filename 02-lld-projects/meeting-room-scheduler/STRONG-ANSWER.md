# Strong Answer: Meeting Room Scheduler

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Meeting Room Scheduler, I'll start by clarifying the core requirements, both functional and non-functional. We want to ensure the system handles concurrent access efficiently and gracefully rejects invalid actions while preserving state invariants."

### Explicit Clarifications
- **Scope:** The core functionality includes booking a meeting with optional amenities, searching for available rooms using strategies, fetching user/room history, and finding common free time slots among users.
- **Concurrency:** The system must handle concurrent room booking attempts gracefully, avoiding double-bookings.
- **Time Representation:** Meetings use explicit start and end intervals. Adjacent half-open intervals `[a,b)` and `[b,c)` do not conflict, allowing back-to-back bookings. Barrier-start overlapping bookings admit at most one reservation.
- **Pacing:** I'm pacing this discussion to 45 minutes, covering the domain models, design patterns, concurrency controls, and failure handling within the allotted time.

## 2. Entity Modeling and APIs (10 mins)
**Say:** "Let's define the primary entities and APIs based on our clarified requirements."

The domain models encapsulate the core business rules:
- `Interval`: Represents the duration. Validates `startTime < endTime`.
- `User`: Has a unique ID, name, and email.
- `MeetingRoom`: Has an ID, capacity, list of amenities, and an internal synchronized collection of booked meetings.
- `Meeting`: The transaction record binding a room, an interval, and attendees.
- `MeetingRoomScheduler`: The primary orchestrator handling routing, lock management, and room allocation.

### Core API Contract
- `MeetingRoomScheduler.book_meeting(title, capacity, interval, amenities, attendees)`: Allocates a room based on the chosen strategy, reserves it, updates user records, and notifies listeners.
- `MeetingRoomScheduler.cancel_meeting(meeting_id)`: Cancels the meeting from the room and user histories, notifying listeners.
- `MeetingRoomScheduler.find_common_free_slots(users, search_start, search_end)`: Aggregates busy intervals across the given users and identifies gaps.
- `MeetingRoomScheduler.get_last_20_meetings_for_user(user_id)` / `get_last_20_meetings_for_room(room_id)`: Fetches historical data efficiently.

## 3. Design Alternatives & Data Structures (10 mins)
**Say:** "Choosing the right allocation strategy and tracking booked slots is critical for performance and correctness."

- **Allocation Strategies:** We define a `RoomAllocationStrategy` interface to keep selection flexible. For instance, a `BestFitAllocationStrategy` finds the room with the smallest capacity that perfectly fits or exceeds the requested capacity, saving larger rooms for larger groups. If we needed a different approach, such as `RandomAllocation` to balance wear-and-tear, it can be trivially swapped in.
- **Complexity and Interval Overlaps:** Our `Interval` class defines `overlaps` explicitly: `this.startTime < other.getEndTime() && other.getStartTime() < this.endTime`. This `O(1)` check ensures that barrier-start overlaps, such as `[10, 11)` and `[11, 12)`, are strictly non-conflicting. An array traversal checks collisions in `O(N)` where `N` is the number of meetings currently booked in a specific room. In optimized versions, an Interval Tree can improve overlap detection to `O(log N)`.

## 4. Concurrency Defense & Thread-Safety Details (12 mins)
**Say:** "Because multiple threads will attempt to book rooms simultaneously, we must guarantee strict thread safety without causing global system bottlenecks."

To prevent double-booking, the implementation avoids a single massive global lock. Instead:
- **Room-Level Locks:** Each `MeetingRoom` holds its own explicit resource lock (e.g., `threading.Lock()` in Python, or `ReentrantLock` in Java). When booking a meeting, the room is locked, the overlap check scans the existing `bookedMeetings` (or Interval Tree), and if safe, the meeting is added. This serializes concurrent booking attempts for the *same* room while allowing concurrent bookings for *different* rooms.
- **State Locks in Scheduler:** The `MeetingRoomScheduler` maintains fine-grained locks for specific collections: `_rooms_lock` for the room list, `_listeners_lock` for notification listeners, and `_user_meetings_lock` for updating user meeting histories. This prevents concurrent modification exceptions and lost updates.

## 5. Failure Handling, Reference Contracts, and Invariants (8 mins)
**Say:** "Let's discuss concrete failure traces and edge cases. What happens if a booking is requested with invalid parameters, or fails midway?"

### Edge Case Reference Contracts
- **Normal Use-Case:** A valid request finds a room matching capacity/amenities, locks the room, confirms no overlaps, inserts the meeting, updates user histories, and notifies listeners.
- **Empty/Invalid Input:** Creating an `Interval(12, 10)` instantly throws an `IllegalArgumentException` (Java) or `ValueError` (Python), rejecting the operation entirely before any locks are acquired or state mutated. Missing amenities fallback or empty users are gracefully handled (e.g., empty attendees list simply results in no user history updates).
- **Duplicate Operations:** Cancelling a meeting that doesn't exist gracefully returns `false` or does nothing. Overlapping bookings for the same room will admit at most one reservation; subsequent requests are rejected by the overlap check and return `null`/empty.
- **Capacity/Equipment Rejection:** If a booking requests a capacity or amenities that no room satisfies, the `AllocationStrategy` returns `null`/`None`. The scheduler gracefully returns without mutating state.
- **Failure Rollbacks:** If `Room A` is selected by the strategy but simultaneously booked by another thread before the current thread reserves it, the room's `bookMeeting()` check returns `false`. The scheduler respects this rejection and gracefully breaks or retries, returning without modifying user histories or notifying listeners. Thus, the system preserves all reservation invariants and avoids partial writes.
- **Cancellation Replay & Lifecycle Operations:** While cancellation is a natural extension, any mutation (like freeing a slot or cancelling) requires acquiring the exact same room-level lock used for booking. This ensures that a concurrent cancellation and booking on the same room are strictly ordered, never corrupting the internal booking list. Cancellation replay (cancelling an already cancelled meeting) preserves invariants and causes no harm.

## 6. Version-Specific Feature Deltas
- **v1-basic:** Basic meeting room scheduling with simple array-based overlap checking, room allocation strategies, and observer notifications for bookings.
- **v2-extended:** Adds support for cancellation, rescheduling, and finding common free slots among users.
- **v3-optimized:** Replaces the array-based meeting storage in rooms with an Interval Tree for `O(log N)` overlap detection and supports recurring meetings. Focused tests target the specific version features (e.g., interval tree overlap testing is explicit in v3).
