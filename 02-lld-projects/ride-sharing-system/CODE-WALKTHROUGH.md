# Code Walkthrough: Ride Sharing (Uber/Lyft)

## Overview

Matching riders with drivers and trip management.

---

## Core Flow

```
Request Ride → Match Driver → Driver Accepts → Pickup → Trip → Drop → Payment
```

---

## Key Classes

```java
class RideService {
    void requestRide(Rider rider, Location pickup, Location drop);
    Driver matchDriver(Location pickup);
    void startTrip(Ride ride);
    void completeTrip(Ride ride);
    double calculateFare(Ride ride);
}

class Ride {
    Rider rider;
    Driver driver;
    Location pickup;
    Location dropoff;
    RideStatus status;
    double fare;
}

class Driver {
    Location currentLocation;
    DriverStatus status;  // AVAILABLE, ON_TRIP, OFFLINE
    double rating;
}
```

---

## Interview Questions

### 1. "How to match drivers?"

```java
Driver matchDriver(Location pickup, RideType type) {
    return drivers.stream()
        .filter(d -> d.isAvailable())
        .filter(d -> d.supportsType(type))
        .min(Comparator.comparing(d -> d.distanceTo(pickup)))
        .orElse(null);
}
```

### 2. "How to calculate dynamic pricing (surge)?"

```java
double getSurgeMultiplier(Location area) {
    int demand = getPendingRequests(area);
    int supply = getAvailableDrivers(area);
    
    double ratio = (double) demand / supply;
    if (ratio > 2.0) return 2.0;  // 2x surge
    if (ratio > 1.5) return 1.5;  // 1.5x surge
    return 1.0;
}
```

### 3. "How to handle driver cancellation?"

```java
void handleDriverCancel(Ride ride) {
    penalizeDriver(ride.driver);
    ride.driver = null;
    ride.status = MATCHING;
    matchDriver(ride);
}
```

### 4. "How to implement rating system?"

```java
class Rating {
    void rateDriver(Ride ride, int stars, String comment) {
        ride.driver.updateRating(stars);
        if (stars <= 2) flagForReview(ride.driver);
    }
}
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Strategy** | Fare calculation, matching |
| **Observer** | Driver/rider notifications |
| **State** | Ride status |
| **Singleton** | RideService |
