# Code Walkthrough: Movie Ticket Booking

## Overview

Booking system with seat selection - common e-commerce pattern.

---

## File Structure

```
java/v1-basic/
├── Movie.java       # Movie entity
├── Theater.java     # Theater with screens
├── Show.java        # Show timing
├── Seat.java        # Seat with status
├── Booking.java     # Booking record
└── BookingDemo.java
```

---

## Core Concepts

### Seat Selection

```java
class Show {
    Movie movie;
    Theater theater;
    LocalDateTime startTime;
    Map<String, Seat> seats;  // seatId -> Seat
    
    synchronized boolean bookSeats(List<String> seatIds, User user) {
        // Check all seats available
        for (String id : seatIds) {
            if (!seats.get(id).isAvailable()) return false;
        }
        // Book all seats atomically
        for (String id : seatIds) {
            seats.get(id).book(user);
        }
        return true;
    }
}
```

---

## Interview Questions

### 1. "How to handle concurrent booking?"

**Problem:** Two users selecting same seat simultaneously

**Solutions:**
- Pessimistic locking: Lock seats during selection
- Optimistic locking: Check version on commit
- Temporary hold: Reserve for X minutes

```java
// Optimistic locking
class Seat {
    long version;
    
    boolean bookWithVersion(User user, long expectedVersion) {
        if (this.version != expectedVersion) return false;
        this.version++;
        this.user = user;
        return true;
    }
}
```

### 2. "How to implement seat hold?"

```java
class SeatHold {
    String seatId;
    User user;
    Instant expiresAt;
    
    boolean isExpired() {
        return Instant.now().isAfter(expiresAt);
    }
}

// Background job to release expired holds
scheduler.scheduleAtFixedRate(() -> {
    releaseExpiredHolds();
}, 1, 1, TimeUnit.MINUTES);
```

### 3. "How to handle payment failure?"

Saga pattern:
1. Reserve seats
2. Process payment
3. If payment fails → release seats
4. If success → confirm booking

### 4. "How to implement dynamic pricing?"

Strategy pattern:
```java
interface PricingStrategy {
    double getPrice(Show show, Seat seat);
}

class PeakHourPricing implements PricingStrategy { ... }
class WeekendPricing implements PricingStrategy { ... }
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Factory** | Create shows |
| **Strategy** | Pricing strategies |
| **Observer** | Notify on booking confirmation |
| **Singleton** | BookingManager |
