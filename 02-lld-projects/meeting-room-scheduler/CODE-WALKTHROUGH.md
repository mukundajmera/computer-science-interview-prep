# Meeting Room Scheduler - Code Walkthrough

## End-to-End Booking Flow
1. A client calls `bookMeeting` on `MeetingRoomScheduler` providing the required `capacity`, `Interval`, `amenities`, and a list of `attendees`.
2. The `Scheduler` iterates through available rooms or delegates to a `RoomAllocationStrategy` to find a suitable room.
3. The `BestFitAllocationStrategy` filters rooms based on capacity, amenities, and availability during the requested interval. It then sorts the valid rooms by capacity (ascending) to find the "best fit" and returns the first one.
4. The `Scheduler` attempts to book the selected room. The room has thread-safe controls to ensure no other threads can double-book it for overlapping intervals.
5. Once successfully booked, the `Scheduler` calls `onMeetingBooked` on all registered `NotificationListener` instances to notify attendees.

## Concurrency Control
- **Per-Room Locks**: Each `MeetingRoom` maintains its list of bookings. To handle concurrent bookings safely, checking for availability and inserting the booking are synchronized or lock-protected within the room instance.
- This prevents the classic "check-then-act" race condition where two threads might see a room as available and both attempt to book it.

## Attendee Notification Hooks
- Uses the Observer pattern.
- Interfaces like `NotificationListener` allow decoupling the scheduling logic from email/SMS notification logic.

## Query APIs
- Finding common free slots requires extracting all meetings for a set of users, merging their intervals, and finding the inverse (gaps).
- Querying the last 20 meetings can be done by maintaining a sorted history per user or room.
