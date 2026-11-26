# Design Approach for Hotel Reservation System

## Step 1: Identify Core Entities

From the problem statement, we identify these main entities:

| Entity | Description |
|--------|-------------|
| **Hotel** | The hotel property with rooms and services |
| **Room** | Individual room with type, number, amenities |
| **RoomType** | Category of room (Single, Double, Suite, etc.) |
| **Guest** | Customer making or having reservations |
| **Reservation** | Booking record linking guest, room, and dates |
| **Payment** | Payment transaction record |
| **RoomInventory** | Daily availability tracker per room |

## Step 2: Define Relationships

```
Hotel "1" *-- "*" Room : contains
Room "1" -- "1" RoomType : has_type
Guest "1" -- "*" Reservation : makes
Reservation "*" -- "1" Room : for_room
Reservation "1" -- "*" Payment : has_payments
RoomInventory "*" -- "1" Room : tracks_availability
```

### Composition vs Association:
- **Composition**: Hotel contains Rooms (physical ownership)
- **Association**: Reservation references Room and Guest (logical relationship)

## Step 3: Choose Design Patterns

### 3.1 Factory Pattern (Room Types)
Create different room types with appropriate pricing and amenities:
- `RoomFactory.createRoom(RoomType.SUITE)`
- Encapsulates room creation logic

### 3.2 Strategy Pattern (Pricing)
Different pricing algorithms for flexibility:
- `StandardPricingStrategy`: Fixed room rate
- `SeasonalPricingStrategy`: Adjust by season
- `WeekendPricingStrategy`: Different weekend rates
- `DynamicPricingStrategy`: Based on occupancy

### 3.3 Observer Pattern (Notifications)
Notify stakeholders of booking events:
- Guest receives confirmation email
- Housekeeping notified of check-in
- Management receives booking reports

### 3.4 State Pattern (Reservation Status)
Reservation transitions through states:
- PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT
- PENDING → CANCELLED
- CONFIRMED → CANCELLED

### 3.5 Singleton Pattern (Hotel System)
Central access point for hotel operations.

## Step 4: Design Classes

### 4.1 Hotel (Aggregate Root)
**Responsibilities**: Manage rooms, process reservations
**Attributes**:
- `hotelId`: String
- `name`: String
- `rooms`: List<Room>
- `reservations`: List<Reservation>

**Methods**:
- `searchAvailableRooms(checkIn, checkOut, type)`: Find rooms
- `makeReservation(guest, room, dates)`: Create booking
- `cancelReservation(reservationId)`: Cancel booking
- `checkIn(reservationId)`: Process check-in
- `checkOut(reservationId)`: Process check-out

### 4.2 Room
**Responsibilities**: Store room information
**Attributes**:
- `roomNumber`: String
- `roomType`: RoomType
- `floor`: int
- `basePrice`: double
- `amenities`: List<Amenity>
- `status`: RoomStatus

**Methods**:
- `isAvailable(date)`: Check availability
- `getPrice(date, strategy)`: Get calculated price

### 4.3 Reservation
**Responsibilities**: Store booking details
**Attributes**:
- `reservationId`: String
- `guest`: Guest
- `room`: Room
- `checkInDate`: LocalDate
- `checkOutDate`: LocalDate
- `status`: ReservationStatus
- `totalAmount`: double
- `payments`: List<Payment>

**Methods**:
- `confirm()`: Confirm reservation
- `cancel()`: Cancel reservation
- `calculateTotal(pricingStrategy)`: Calculate cost
- `getNumberOfNights()`: Get stay duration

### 4.4 RoomInventory
**Responsibilities**: Track daily room availability
**Attributes**:
- `room`: Room
- `date`: LocalDate
- `isAvailable`: boolean
- `reservation`: Reservation (if booked)

**Methods**:
- `book(reservation)`: Mark as booked
- `release()`: Mark as available

## Step 5: Handle Edge Cases

### 5.1 Double Booking Prevention
```java
synchronized (room) {
    if (!isAvailable(room, checkIn, checkOut)) {
        throw new RoomNotAvailableException();
    }
    blockRoom(room, checkIn, checkOut);
}
```

### 5.2 Date Validation
```java
if (checkOut.isBefore(checkIn) || checkOut.isEqual(checkIn)) {
    throw new InvalidDateRangeException();
}
if (checkIn.isBefore(LocalDate.now())) {
    throw new PastDateException();
}
```

### 5.3 Cancellation Policy
```java
long hoursUntilCheckIn = Duration.between(now, checkInDateTime).toHours();
if (hoursUntilCheckIn < 24) {
    refundAmount = totalAmount * 0.5;
} else {
    refundAmount = totalAmount;
}
```

### 5.4 Capacity Validation
```java
if (numberOfGuests > room.getMaxOccupancy()) {
    throw new CapacityExceededException();
}
```

## Step 6: Optimization Opportunities

### 6.1 Availability Cache
Cache room availability for frequently queried dates:
```java
Map<LocalDate, Set<Room>> availabilityCache;
```

### 6.2 Database Indexing
Index on (room_id, date) for fast availability queries.

### 6.3 Connection Pooling
Use connection pool for database access.

### 6.4 Thread Safety (v3)
```java
private final ReentrantReadWriteLock inventoryLock = new ReentrantReadWriteLock();

public List<Room> searchAvailable(LocalDate checkIn, LocalDate checkOut) {
    inventoryLock.readLock().lock();
    try {
        // search logic
    } finally {
        inventoryLock.readLock().unlock();
    }
}
```

### 6.5 Batch Operations
Process multiple reservations in batch for efficiency.

## Version Progression

### v1-basic
- Basic room and reservation management
- Simple availability check
- Single pricing strategy
- ~300-400 lines

### v2-extended
- Multiple room types with factory
- Pricing strategies
- Guest profiles
- Payment processing
- Observer notifications
- ~500-700 lines

### v3-optimized
- Thread-safe operations
- Concurrent booking prevention
- Optimized availability search
- Comprehensive error handling
- ~700-1000 lines
