# Design for Movie Ticket Booking System

Complete class design with diagrams and key decisions.

---

## Mermaid Class Diagram

```mermaid
classDiagram
    class Theater {
        -String id
        -String name
        -String address
        -List~Screen~ screens
        +addScreen(Screen) void
        +getScreen(String) Screen
        +getAllShows() List~Show~
    }

    class Screen {
        -String id
        -String name
        -List~Seat~ seats
        -int capacity
        +getSeat(String) Seat
        +getAllSeats() List~Seat~
    }

    class Seat {
        -String id
        -String row
        -int number
        -SeatType seatType
        +getId() String
        +getType() SeatType
    }

    class Movie {
        -String id
        -String title
        -String description
        -int durationMinutes
        -String genre
        -String rating
    }

    class Show {
        -String id
        -Movie movie
        -Screen screen
        -LocalDateTime startTime
        -Map~String, ShowSeat~ showSeats
        +getAvailableSeats() List~ShowSeat~
        +lockSeats(List~String~, String) boolean
        +bookSeats(List~String~) boolean
    }

    class ShowSeat {
        -Seat seat
        -SeatStatus status
        -double price
        -String lockedBy
        -long lockedAt
        +lock(String) boolean
        +unlock() void
        +book() void
        +isLockExpired() boolean
    }

    class Booking {
        -String id
        -Show show
        -List~ShowSeat~ seats
        -Customer customer
        -BookingStatus status
        -double totalAmount
        -Payment payment
        +confirm() void
        +cancel() void
        +getTicket() Ticket
    }

    class Payment {
        -String id
        -double amount
        -PaymentMethod method
        -PaymentStatus status
        +process() boolean
        +refund() boolean
    }

    class SeatType {
        <<enumeration>>
        REGULAR
        PREMIUM
        VIP
    }

    class SeatStatus {
        <<enumeration>>
        AVAILABLE
        LOCKED
        BOOKED
    }

    class BookingStatus {
        <<enumeration>>
        PENDING
        CONFIRMED
        CANCELLED
    }

    Theater "1" *-- "n" Screen : contains
    Screen "1" *-- "n" Seat : has
    Show --> Movie
    Show --> Screen
    Show "1" *-- "n" ShowSeat : manages
    ShowSeat --> Seat
    Booking --> Show
    Booking "1" --> "n" ShowSeat : reserves
    Booking --> Payment
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    THEATER ||--o{ SCREEN : has
    SCREEN ||--o{ SEAT : contains
    SCREEN ||--o{ SHOW : hosts
    MOVIE ||--o{ SHOW : plays_in
    SHOW ||--o{ SHOW_SEAT : has
    SEAT ||--o{ SHOW_SEAT : represents
    CUSTOMER ||--o{ BOOKING : makes
    BOOKING ||--o{ BOOKING_SEAT : reserves
    SHOW_SEAT ||--o{ BOOKING_SEAT : booked_as
    BOOKING ||--|| PAYMENT : has

    THEATER {
        string theater_id PK
        string name
        string address
        string city
    }

    SCREEN {
        string screen_id PK
        string theater_id FK
        string name
        int capacity
    }

    SEAT {
        string seat_id PK
        string screen_id FK
        string row
        int number
        string seat_type
    }

    MOVIE {
        string movie_id PK
        string title
        int duration_minutes
        string genre
        string rating
        date release_date
    }

    SHOW {
        string show_id PK
        string movie_id FK
        string screen_id FK
        datetime start_time
        datetime end_time
    }

    SHOW_SEAT {
        string show_seat_id PK
        string show_id FK
        string seat_id FK
        decimal price
        string status
        string locked_by
        timestamp locked_at
    }

    CUSTOMER {
        string customer_id PK
        string name
        string email
        string phone
    }

    BOOKING {
        string booking_id PK
        string show_id FK
        string customer_id FK
        string status
        decimal total_amount
        timestamp created_at
    }

    BOOKING_SEAT {
        string booking_seat_id PK
        string booking_id FK
        string show_seat_id FK
    }

    PAYMENT {
        string payment_id PK
        string booking_id FK
        decimal amount
        string method
        string status
        timestamp paid_at
    }
```

**Schema Notes:**
- `SHOW_SEAT` tracks seat availability per show with locking mechanism
- `locked_at` enables automatic lock expiry (10 min timeout)
- `BOOKING_SEAT` junction table for many-to-many booking relationship
- Concurrency handled via optimistic locking on `SHOW_SEAT`

---

## Class Diagram

```
┌─────────────────────┐     ┌─────────────────────┐
│       Movie         │     │      Theater        │
├─────────────────────┤     ├─────────────────────┤
│ - id: String        │     │ - id: String        │
│ - title: String     │     │ - name: String      │
│ - duration: int     │     │ - address: String   │
│ - genre: Genre      │     │ - screens: List     │
└─────────────────────┘     └──────────┬──────────┘
                                       │ contains
                                       ▼
┌─────────────────────┐     ┌─────────────────────┐
│        Show         │────>│       Screen        │
├─────────────────────┤     ├─────────────────────┤
│ - id: String        │     │ - id: String        │
│ - movie: Movie      │     │ - name: String      │
│ - screen: Screen    │     │ - seats: List<Seat> │
│ - startTime: Date   │     │ - capacity: int     │
│ - showSeats: Map    │     └─────────────────────┘
└─────────────────────┘              │ has
         │ has                       ▼
         ▼               ┌─────────────────────┐
┌─────────────────────┐  │        Seat         │
│      ShowSeat       │  ├─────────────────────┤
├─────────────────────┤  │ - id: String        │
│ - seat: Seat        │  │ - row: String       │
│ - status: SeatStatus│  │ - number: int       │
│ - price: double     │  │ - type: SeatType    │
│ - lockedBy: String  │  └─────────────────────┘
│ - lockedAt: long    │
└─────────────────────┘
         │
         │ booked in
         ▼
┌─────────────────────┐     ┌─────────────────────┐
│      Booking        │────>│      Payment        │
├─────────────────────┤     ├─────────────────────┤
│ - id: String        │     │ - id: String        │
│ - show: Show        │     │ - amount: double    │
│ - seats: List       │     │ - method: PayMethod │
│ - status: Status    │     │ - status: PayStatus │
│ - totalAmount: dbl  │     └─────────────────────┘
└─────────────────────┘

┌─────────────────────────────────────┐
│         SeatStatus <<enum>>          │
├─────────────────────────────────────┤
│ AVAILABLE, LOCKED, BOOKED           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│          SeatType <<enum>>           │
├─────────────────────────────────────┤
│ REGULAR, PREMIUM, VIP               │
└─────────────────────────────────────┘
```

---

## Core Classes

### Movie
- **Attributes**: `id`, `title`, `description`, `duration`, `genre`, `rating`

### Theater
- **Attributes**: `id`, `name`, `address`, `screens`
- **Methods**: `addScreen()`, `getScreen()`, `getAllShows()`

### Screen
- **Attributes**: `id`, `name`, `seats`, `capacity`
- **Methods**: `getSeat()`, `getAllSeats()`

### Seat
- **Attributes**: `id`, `row`, `number`, `seatType`
- **Patterns Used**: Factory for different types

### Show
- **Attributes**: `id`, `movie`, `screen`, `startTime`, `showSeats`
- **Methods**: `getAvailableSeats()`, `lockSeats()`, `bookSeats()`

### ShowSeat
- **Attributes**: `seat`, `status`, `price`, `lockedBy`, `lockedAt`
- **Methods**: `lock()`, `unlock()`, `book()`, `isLockExpired()`

### Booking
- **Attributes**: `id`, `show`, `seats`, `user`, `status`, `totalAmount`, `payment`
- **Methods**: `confirm()`, `cancel()`, `getTicket()`

---

## Key Design Decisions

### Decision 1: ShowSeat vs Seat
**Rationale**: 
- Seat represents physical seat (row, number, type)
- ShowSeat represents seat status for specific show
- Allows same physical seat in different shows

### Decision 2: Optimistic Locking for Seats
**Rationale**:
- Better performance than pessimistic locking
- Works well for read-heavy workloads
- Handles race conditions gracefully

### Decision 3: Seat Lock with Timeout
**Rationale**:
- Prevents indefinite seat holds
- Allows retry if payment fails
- Configurable timeout (10 min default)

---

## Thread Safety (v3)

### Critical Sections:
1. **Seat locking** - CAS operation
2. **Seat booking** - Atomic status update
3. **Lock expiry** - Scheduled cleanup

### Synchronization:
```java
// ConcurrentHashMap for show seats
private final ConcurrentHashMap<String, ShowSeat> showSeats;

// Atomic seat status update
public boolean lockSeat(String seatId, String userId) {
    return showSeats.computeIfPresent(seatId, (k, seat) -> {
        if (seat.isAvailable() || seat.isLockExpired()) {
            seat.lock(userId);
            return seat;
        }
        return seat;
    }) != null;
}
```

---

## Complexity Analysis

| Operation | Complexity |
|-----------|------------|
| Find available seats | O(n) where n = seats in show |
| Lock seat | O(1) with HashMap |
| Book seats | O(k) where k = selected seats |
| Check lock expiry | O(1) |
