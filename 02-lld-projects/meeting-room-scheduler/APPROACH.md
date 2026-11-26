# Meeting Room Scheduler - Approach

## Entity Identification
- `MeetingRoom`: Contains ID, capacity, amenities, and a collection of booked `Meeting`s.
- `Meeting`: Contains ID, subject, interval, list of attendees, and a reference to the `MeetingRoom`.
- `Interval`: Holds `startTime` and `endTime`.
- `User`: Contains ID, name, email.

## Interval Overlap Mathematics
To detect if two intervals `[start1, end1)` and `[start2, end2)` overlap, we check:
```
start1 < end2 && start2 < end1
```
If true, the intervals overlap.

## Room Allocation Strategies
We use the Strategy pattern to allow flexible allocation:
- **FirstAvailableAllocationStrategy**: Picks the first room that satisfies the constraints.
- **BestFitAllocationStrategy**: Picks the room with the smallest capacity that is still `>=` the requested capacity, minimizing wasted seats.

## Sweep-line Algorithm for Common Free Slots
To find common free slots across multiple users:
1. Collect all meetings for all given users.
2. Extract the intervals for these meetings.
3. Merge overlapping intervals.
4. The gaps between the merged intervals represent the common free slots.
