# Meeting Room Scheduler - Problem Statement

## Problem Description
Design and implement a Meeting Room Scheduler. The system should manage a set of meeting rooms with different capacities and amenities, allowing users to book rooms for specific time intervals, handle concurrent booking requests safely to prevent double-booking, and send notifications to attendees.

## Functional Requirements
1. **Manage Rooms**: Add rooms with specific capacity and a list of amenities.
2. **Book Meeting**: Users can book a meeting specifying capacity, time interval [start, end), and required amenities.
3. **Collision Avoidance**: Ensure that rooms are not double-booked (i.e., no overlapping meetings in the same room).
4. **Notifications**: Dispatch notifications to attendees upon successful booking, cancellation, or updates.
5. **Find Common Free Slot**: Given a list of users, find common free slots where all users are available.
6. **Query History**: Ability to query the last 20 meetings for a given user or room.

## Non-Functional Requirements
1. Thread safety and concurrent access handling.
2. Extensibility for different room allocation strategies.
3. High performance for finding available rooms and slots.

## Constraints
1. Time intervals are defined by start and end timestamps (exclusive end).
2. All users and rooms fit in memory (single-machine LLD simulation).

## Clarifying Questions
- Q: Are intervals [start, end) inclusive of start and exclusive of end? A: Yes.
- Q: How to resolve overlapping meetings? A: Reject the booking or suggest another room.
- Q: What happens if a room goes down or under maintenance? A: Out of scope for now, but good to consider in follow-ups.

## Core Entities
- **User**: Represents a person interacting with the system.
- **MeetingRoom**: Represents a physical room.
- **Meeting**: Represents a booked event.
- **Interval**: Represents a time block [start, end).
