# Code Walkthrough: Hotel Reservation

## Overview

Booking system with room allocation and pricing.

---

## Core Entities

| Entity | Attributes |
|--------|------------|
| Hotel | name, rooms, address |
| Room | type, price, amenities, status |
| Reservation | guest, room, dates, status |
| Guest | name, contact, preferences |

---

## Key Operations

### Room Search

```java
List<Room> searchRooms(LocalDate checkIn, LocalDate checkOut, RoomType type) {
    return rooms.stream()
        .filter(r -> r.getType() == type)
        .filter(r -> isAvailable(r, checkIn, checkOut))
        .collect(toList());
}
```

### Booking Flow

```
1. Search available rooms
2. Select room
3. Create reservation (PENDING)
4. Process payment
5. Confirm reservation
```

---

## Interview Questions

### 1. "How to handle overbooking?"

Hotels overbook by ~5%:
```java
int overbookingLimit = (int)(totalRooms * 0.05);
if (confirmedBookings <= totalRooms + overbookingLimit) {
    allowBooking();
}
```

### 2. "How to implement dynamic pricing?"

```java
interface PricingStrategy {
    double getPrice(Room room, LocalDate date);
}

class SeasonalPricing implements PricingStrategy {
    // Higher prices during peak season
}
```

### 3. "How to handle cancellation?"

```java
enum CancellationPolicy {
    FREE_24H,      // Free if >24h before
    PARTIAL_REFUND, // 50% refund
    NO_REFUND
}
```

## Compilation and Execution

To compile and run the project for any version (e.g., v1-basic), use the following commands from the root directory of the project:

### Compile
```bash
find java/v1-basic -name '*.java' | xargs javac -encoding UTF-8 -d out
```

### Run
```bash
java -cp out HotelDemo
```
