# Design for Hotel Reservation System

## Mermaid Class Diagram

```mermaid
classDiagram
    class Hotel {
        -String hotelId
        -String name
        -String address
        -Map~String, Room~ rooms
        -Map~String, Reservation~ reservations
        -Map~String, Guest~ guests
        -PricingStrategy pricingStrategy
        +searchAvailableRooms(LocalDate, LocalDate, RoomType) List~Room~
        +makeReservation(Guest, Room, LocalDate, LocalDate) Reservation
        +cancelReservation(String) boolean
        +checkIn(String) boolean
        +checkOut(String) Payment
        +getReservation(String) Reservation
        +addRoom(Room) void
    }

    class Room {
        -String roomNumber
        -RoomType roomType
        -int floor
        -double basePrice
        -int maxOccupancy
        -Set~String~ amenities
        -RoomStatus status
        +getPrice(LocalDate) double
        +isAvailable() boolean
        +setStatus(RoomStatus) void
    }

    class Reservation {
        -String reservationId
        -Guest guest
        -Room room
        -LocalDate checkInDate
        -LocalDate checkOutDate
        -ReservationStatus status
        -double totalAmount
        -LocalDateTime createdAt
        +confirm() void
        +cancel() void
        +checkIn() void
        +checkOut() void
        +getNumberOfNights() int
    }

    class Guest {
        -String guestId
        -String name
        -String email
        -String phone
        -String address
        -List~Reservation~ reservationHistory
        +addReservation(Reservation) void
        +getActiveReservations() List~Reservation~
    }

    class RoomInventory {
        -Room room
        -LocalDate date
        -boolean isAvailable
        -Reservation reservation
        +book(Reservation) void
        +release() void
    }

    class PricingStrategy {
        <<interface>>
        +calculatePrice(Room, LocalDate) double
        +calculateTotal(Room, LocalDate, LocalDate) double
    }

    class StandardPricingStrategy {
        +calculatePrice(Room, LocalDate) double
        +calculateTotal(Room, LocalDate, LocalDate) double
    }

    class SeasonalPricingStrategy {
        -Map~String, Double~ seasonalMultipliers
        +calculatePrice(Room, LocalDate) double
    }

    class WeekendPricingStrategy {
        -double weekendMultiplier
        +calculatePrice(Room, LocalDate) double
    }

    class BookingObserver {
        <<interface>>
        +onReservationCreated(Reservation) void
        +onReservationCancelled(Reservation) void
        +onCheckIn(Reservation) void
        +onCheckOut(Reservation) void
    }

    class EmailNotifier {
        +onReservationCreated(Reservation) void
        +onCheckIn(Reservation) void
    }

    class HousekeepingNotifier {
        +onCheckOut(Reservation) void
    }

    class RoomType {
        <<enumeration>>
        SINGLE
        DOUBLE
        DELUXE
        SUITE
    }

    class RoomStatus {
        <<enumeration>>
        AVAILABLE
        OCCUPIED
        MAINTENANCE
        CLEANING
    }

    class ReservationStatus {
        <<enumeration>>
        PENDING
        CONFIRMED
        CHECKED_IN
        CHECKED_OUT
        CANCELLED
    }

    Hotel "1" *-- "n" Room : contains
    Hotel "1" --> "n" Reservation : tracks
    Hotel "1" --> "n" Guest : manages
    Hotel --> PricingStrategy : uses
    Hotel --> BookingObserver : notifies
    Reservation --> Guest
    Reservation --> Room
    Room "1" --> "n" RoomInventory : has_availability
    PricingStrategy <|.. StandardPricingStrategy
    PricingStrategy <|.. SeasonalPricingStrategy
    PricingStrategy <|.. WeekendPricingStrategy
    BookingObserver <|.. EmailNotifier
    BookingObserver <|.. HousekeepingNotifier
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    HOTEL ||--o{ ROOM : has
    ROOM ||--o{ ROOM_INVENTORY : has_daily
    GUEST ||--o{ RESERVATION : makes
    ROOM ||--o{ RESERVATION : booked_for
    RESERVATION ||--o| PAYMENT : generates
    RESERVATION ||--o{ ROOM_INVENTORY : blocks

    HOTEL {
        string hotel_id PK
        string name
        string address
        string city
        string country
        int star_rating
    }

    ROOM {
        string room_id PK
        string hotel_id FK
        string room_number
        string room_type
        int floor
        decimal base_price
        int max_occupancy
        string status
    }

    GUEST {
        string guest_id PK
        string name
        string email UK
        string phone
        string address
        string id_proof_type
        string id_proof_number
    }

    RESERVATION {
        string reservation_id PK
        string guest_id FK
        string room_id FK
        date check_in_date
        date check_out_date
        string status
        decimal total_amount
        timestamp created_at
        timestamp updated_at
    }

    ROOM_INVENTORY {
        string inventory_id PK
        string room_id FK
        date date
        boolean is_available
        string reservation_id FK
        decimal price_for_day
    }

    PAYMENT {
        string payment_id PK
        string reservation_id FK
        decimal amount
        string payment_method
        string status
        timestamp paid_at
    }
```

**Schema Notes:**
- `ROOM_INVENTORY` provides day-by-day availability tracking
- `RESERVATION` links guest to room for date range
- `PAYMENT` tracks payment details with multiple method support
- Room pricing can vary by day via `ROOM_INVENTORY.price_for_day`

---

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HOTEL RESERVATION SYSTEM                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   <<enum>>      │     │   <<enum>>      │     │   <<enum>>      │
│   RoomType      │     │ ReservationStatus│     │   RoomStatus    │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ SINGLE          │     │ PENDING          │     │ AVAILABLE       │
│ DOUBLE          │     │ CONFIRMED        │     │ OCCUPIED        │
│ DELUXE          │     │ CHECKED_IN       │     │ MAINTENANCE     │
│ SUITE           │     │ CHECKED_OUT      │     │ CLEANING        │
└─────────────────┘     │ CANCELLED        │     └─────────────────┘
                        └─────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                               Hotel                                    │
├───────────────────────────────────────────────────────────────────────┤
│ - hotelId: String                                                      │
│ - name: String                                                         │
│ - address: String                                                      │
│ - rooms: Map<String, Room>                                             │
│ - reservations: Map<String, Reservation>                               │
│ - guests: Map<String, Guest>                                           │
│ - pricingStrategy: PricingStrategy                                     │
├───────────────────────────────────────────────────────────────────────┤
│ + searchAvailableRooms(checkIn, checkOut, type): List<Room>            │
│ + makeReservation(guest, room, checkIn, checkOut): Reservation         │
│ + cancelReservation(reservationId): boolean                            │
│ + checkIn(reservationId): boolean                                      │
│ + checkOut(reservationId): Payment                                     │
│ + getReservation(reservationId): Reservation                           │
│ + addRoom(room): void                                                  │
└───────────────────────────────────────────────────────────────────────┘
          │                                           │
          │ contains                                  │ tracks
          ▼                                           ▼
┌─────────────────────────┐              ┌─────────────────────────┐
│         Room            │              │      Reservation        │
├─────────────────────────┤              ├─────────────────────────┤
│ - roomNumber: String    │              │ - reservationId: String │
│ - roomType: RoomType    │              │ - guest: Guest          │
│ - floor: int            │              │ - room: Room            │
│ - basePrice: double     │              │ - checkInDate: LocalDate│
│ - maxOccupancy: int     │              │ - checkOutDate: LocalDate│
│ - amenities: Set<String>│              │ - status: ReservationStatus│
│ - status: RoomStatus    │              │ - totalAmount: double   │
├─────────────────────────┤              │ - createdAt: LocalDateTime│
│ + getPrice(date): double│              ├─────────────────────────┤
│ + isAvailable(): boolean│              │ + confirm(): void       │
│ + setStatus(status)     │              │ + cancel(): void        │
└─────────────────────────┘              │ + checkIn(): void       │
                                         │ + checkOut(): void      │
                                         │ + getNumberOfNights(): int│
                                         └─────────────────────────┘
                                                    │
                                                    │ for
                                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                               Guest                                    │
├───────────────────────────────────────────────────────────────────────┤
│ - guestId: String                                                      │
│ - name: String                                                         │
│ - email: String                                                        │
│ - phone: String                                                        │
│ - address: String                                                      │
│ - reservationHistory: List<Reservation>                                │
├───────────────────────────────────────────────────────────────────────┤
│ + addReservation(reservation): void                                    │
│ + getActiveReservations(): List<Reservation>                           │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                     RoomInventory (Daily Availability)                 │
├───────────────────────────────────────────────────────────────────────┤
│ - room: Room                                                           │
│ - date: LocalDate                                                      │
│ - isAvailable: boolean                                                 │
│ - reservation: Reservation                                             │
├───────────────────────────────────────────────────────────────────────┤
│ + book(reservation): void                                              │
│ + release(): void                                                      │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                  <<interface>> PricingStrategy                         │
├───────────────────────────────────────────────────────────────────────┤
│ + calculatePrice(room: Room, date: LocalDate): double                  │
│ + calculateTotal(room: Room, checkIn: LocalDate, checkOut: LocalDate)  │
└───────────────────────────────────────────────────────────────────────┘
          △
          │ implements
          │
    ┌─────┴─────────────────┬─────────────────────┐
    │                       │                     │
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ StandardPricing   │ │ SeasonalPricing   │ │ WeekendPricing    │
│ Strategy          │ │ Strategy          │ │ Strategy          │
├───────────────────┤ ├───────────────────┤ ├───────────────────┤
│ Uses base price   │ │ Adjusts by season │ │ Higher weekend    │
│ without changes   │ │ (peak/off-peak)   │ │ rates             │
└───────────────────┘ └───────────────────┘ └───────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                  <<interface>> BookingObserver                         │
├───────────────────────────────────────────────────────────────────────┤
│ + onReservationCreated(reservation: Reservation): void                 │
│ + onReservationCancelled(reservation: Reservation): void               │
│ + onCheckIn(reservation: Reservation): void                            │
│ + onCheckOut(reservation: Reservation): void                           │
└───────────────────────────────────────────────────────────────────────┘
          △
          │ implements
          │
    ┌─────┴───────────────┬───────────────────┐
    │                     │                   │
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ EmailNotifier    │ │ HousekeepingNotif│ │ RevenueTracker   │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

## Core Classes

### Hotel
- **Attributes**: hotelId, name, rooms, reservations, guests, pricingStrategy
- **Methods**: searchAvailableRooms(), makeReservation(), cancelReservation(), checkIn(), checkOut()
- **Patterns Used**: Singleton (optional), Observer (for notifications)

### Room
- **Attributes**: roomNumber, roomType, floor, basePrice, maxOccupancy, amenities, status
- **Methods**: getPrice(), isAvailable(), setStatus()
- **Patterns Used**: Factory (for creation based on type)

### Reservation
- **Attributes**: reservationId, guest, room, checkInDate, checkOutDate, status, totalAmount
- **Methods**: confirm(), cancel(), checkIn(), checkOut(), getNumberOfNights()
- **Patterns Used**: State (for status transitions)

### PricingStrategy (Interface)
- **Implementations**: StandardPricingStrategy, SeasonalPricingStrategy, WeekendPricingStrategy
- **Methods**: calculatePrice(), calculateTotal()
- **Patterns Used**: Strategy

### BookingObserver (Interface)
- **Implementations**: EmailNotifier, HousekeepingNotifier, RevenueTracker
- **Methods**: onReservationCreated(), onCheckIn(), onCheckOut()
- **Patterns Used**: Observer

## Key Design Decisions

### 1. Room Inventory Approach
**Decision**: Use date-based inventory tracking instead of calendar-per-room
**Rationale**: 
- Faster availability queries
- Easy to handle partial bookings
- Better for concurrent access
**Trade-off**: More storage, but better query performance

### 2. Reservation Status Machine
**Decision**: Use explicit state transitions with validation
**Rationale**:
- Prevents invalid state transitions
- Clear business logic
- Audit trail friendly
**Trade-off**: More code, but safer

### 3. Strategy Pattern for Pricing
**Decision**: Pluggable pricing algorithms
**Rationale**:
- Easy to add new pricing rules
- Supports seasonal adjustments
- Can combine strategies
**Trade-off**: Slight complexity increase

### 4. Observer for Notifications
**Decision**: Decouple notification from booking logic
**Rationale**:
- Easy to add new notification channels
- Non-blocking notifications
- Single responsibility
**Trade-off**: Indirect flow, harder to debug

## Sequence Diagrams

### Make Reservation Flow
```
Guest       Hotel         Room        Inventory     Reservation
  │           │            │              │              │
  │ search    │            │              │              │
  │──────────>│ getAvailable              │              │
  │           │───────────────────────────>              │
  │           │            │   available  │              │
  │           │<───────────────────────────              │
  │  rooms    │            │              │              │
  │<──────────│            │              │              │
  │           │            │              │              │
  │ select    │            │              │              │
  │ room 201  │            │              │              │
  │──────────>│ makeReservation           │              │
  │           │───────────────────────────> block        │
  │           │            │              │              │
  │           │            │              │  create      │
  │           │───────────────────────────────────────────>
  │           │            │              │              │
  │  confirm  │            │              │              │
  │<──────────│            │              │              │
```

### Check-in Flow
```
Guest       Hotel       Reservation     Room
  │           │              │            │
  │ check-in  │              │            │
  │──────────>│ getReservation            │
  │           │──────────────>            │
  │           │   reservation │            │
  │           │<──────────────            │
  │           │ validate      │            │
  │           │──────────────>            │
  │           │   CONFIRMED  │            │
  │           │<──────────────            │
  │           │ checkIn()    │            │
  │           │──────────────>            │
  │           │              │ setStatus  │
  │           │              │──────────> │
  │           │              │  OCCUPIED  │
  │           │              │<───────────│
  │  key card │              │            │
  │<──────────│              │            │
```

## Complexity Analysis

### Time Complexity
| Operation | Complexity | Notes |
|-----------|------------|-------|
| Search Available Rooms | O(R × D) | R=rooms, D=days in range |
| Make Reservation | O(D) | D=days to block |
| Cancel Reservation | O(D) | D=days to release |
| Check-in | O(1) | Status update |
| Check-out | O(1) | Status update |
| Calculate Price | O(D) | D=nights |

### Space Complexity
| Component | Complexity | Notes |
|-----------|------------|-------|
| Room Inventory | O(R × 365) | Per room per day for year |
| Reservations | O(N) | N=total reservations |
| Guest History | O(G × Avg) | G=guests × average bookings |

## Concurrency Considerations (v3)

### Thread Safety
1. **Room Inventory**: ReadWriteLock for availability queries vs booking
2. **Reservation**: Synchronized status transitions
3. **Hotel**: ConcurrentHashMap for room and reservation storage

### Race Condition Prevention
```java
// Use optimistic locking for booking
public Reservation makeReservation(Guest guest, Room room, 
                                   LocalDate checkIn, LocalDate checkOut) {
    inventoryLock.writeLock().lock();
    try {
        // Double-check availability
        if (!isRoomAvailable(room, checkIn, checkOut)) {
            throw new RoomNotAvailableException();
        }
        // Block room and create reservation
        return createReservation(guest, room, checkIn, checkOut);
    } finally {
        inventoryLock.writeLock().unlock();
    }
}
```

### Preventing Overbooking
1. Lock room inventory during booking
2. Validate availability before confirmation
3. Use database transactions in production

## Error Handling

### Exception Hierarchy
```
HotelException (base)
├── RoomException
│   ├── RoomNotAvailableException
│   ├── RoomNotFoundException
│   └── InvalidRoomException
├── ReservationException
│   ├── ReservationNotFoundException
│   ├── InvalidDateRangeException
│   ├── InvalidCancellationException
│   └── InvalidStatusTransitionException
├── GuestException
│   ├── GuestNotFoundException
│   └── InvalidGuestDataException
└── PaymentException
    ├── PaymentFailedException
    └── RefundFailedException
```
