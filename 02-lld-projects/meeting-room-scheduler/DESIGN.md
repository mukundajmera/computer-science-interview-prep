# Meeting Room Scheduler - Design

## System Architecture
The system consists of a `MeetingRoomScheduler` that orchestrates bookings, users, and rooms. It delegates room selection to an injected `RoomAllocationStrategy`. `Meeting`s trigger events that notify `NotificationListener`s.

## Class Diagram

```mermaid
classDiagram
    class User {
        +String id
        +String name
        +String email
    }
    class MeetingRoom {
        +String id
        +int capacity
        +List~String~ amenities
        +List~Meeting~ getBookedMeetings()
        +boolean bookMeeting(Meeting meeting)
    }
    class Meeting {
        +String id
        +String title
        +Interval interval
        +List~User~ attendees
        +MeetingRoom room
    }
    class Interval {
        +long startTime
        +long endTime
        +boolean overlaps(Interval other)
    }
    class RoomAllocationStrategy {
        <<interface>>
        +MeetingRoom allocateRoom(List~MeetingRoom~ rooms, int capacity, Interval interval, List~String~ amenities)
    }
    class BestFitAllocationStrategy {
        +MeetingRoom allocateRoom(...)
    }
    class NotificationListener {
        <<interface>>
        +void onMeetingBooked(Meeting meeting)
        +void onMeetingCancelled(Meeting meeting)
    }
    class MeetingRoomScheduler {
        -List~MeetingRoom~ rooms
        -RoomAllocationStrategy allocationStrategy
        -List~NotificationListener~ notificationListeners
        +Meeting bookMeeting(...)
        +void cancelMeeting(...)
        +List~Interval~ findCommonFreeSlots(...)
    }
    
    MeetingRoomScheduler --> RoomAllocationStrategy
    MeetingRoomScheduler o-- MeetingRoom
    MeetingRoomScheduler o-- NotificationListener
    MeetingRoom o-- Meeting
    Meeting --> Interval
    Meeting o-- User
```

## Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant Scheduler as MeetingRoomScheduler
    participant Strategy as BestFitAllocationStrategy
    participant Room as MeetingRoom
    participant Notifier as NotificationListener
    
    User->>Scheduler: bookMeeting(capacity, interval, amenities, attendees)
    Scheduler->>Strategy: allocateRoom(rooms, capacity, interval, amenities)
    Strategy-->>Scheduler: selectedRoom
    Scheduler->>Room: bookMeeting(meeting)
    Room-->>Scheduler: success
    Scheduler->>Notifier: onMeetingBooked(meeting)
    Scheduler-->>User: meeting Details
```
