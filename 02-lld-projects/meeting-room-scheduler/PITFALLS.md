# Meeting Room Scheduler - Common Pitfalls

## 1. Global Lock Bottlenecks
- **Signal**: Synchronizing the entire `bookMeeting` method on the `Scheduler` object.
- **Root Cause**: Developer attempts to prevent double-booking the easy way.
- **Mitigation**: Use fine-grained locking per `MeetingRoom` instance to allow concurrent bookings for different rooms.

## 2. Incorrect Boundary Check for Back-to-Back Meetings
- **Signal**: Rejecting back-to-back meetings (e.g., A ends at 10:00, B starts at 10:00).
- **Root Cause**: Using `<=` or `>=` incorrectly in interval overlap checks.
- **Mitigation**: Overlap formula should strictly be `start1 < end2 && start2 < end1`.

## 3. Attendee Calendar Desync
- **Signal**: If a booking fails midway, some users have it on their calendar while others don't.
- **Root Cause**: Lack of transactional boundaries when adding meetings to user lists.
- **Mitigation**: Use atomic operations or rollback logic if a partial failure occurs.

## 4. Non-Thread-Safe Room Reservation (Check-then-Act)
- **Signal**: Checking if a room is available, then in a separate un-synchronized block adding the meeting.
- **Root Cause**: Race condition between the check and the act.
- **Mitigation**: The check and insertion must happen atomically within a synchronized block or `ReentrantLock`.
