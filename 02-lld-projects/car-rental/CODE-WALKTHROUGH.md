# Code Walkthrough: Car Rental

## Overview

Fleet management with booking and availability tracking.

---

## Core Entities

| Entity | Key Attributes |
|--------|---------------|
| Vehicle | model, type, status, location |
| Reservation | vehicle, customer, dates, pickup/return |
| Customer | license, contact, history |
| Location | address, inventory |

---

## Booking Flow

```
1. Search (dates, location, type)
2. Check availability
3. Reserve vehicle
4. Customer pickup (verify license)
5. Return vehicle
6. Calculate charges
```

---

## Interview Questions

### 1. "How to handle different vehicle types?"

```java
abstract class Vehicle {
    abstract double getDailyRate();
}

class Sedan extends Vehicle { }
class SUV extends Vehicle { }
class Luxury extends Vehicle { }
```

### 2. "How to track vehicle location?"

```java
class Vehicle {
    Location currentLocation;
    VehicleStatus status; // AVAILABLE, RENTED, MAINTENANCE
}
```

### 3. "How to calculate charges?"

```java
double calculateCharges(Reservation r) {
    long days = ChronoUnit.DAYS.between(r.start, r.end);
    double base = days * vehicle.getDailyRate();
    double insurance = r.hasInsurance ? days * INSURANCE_RATE : 0;
    double lateFee = r.isLate() ? calculateLateFee(r) : 0;
    return base + insurance + lateFee;
}
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Factory** | Create vehicles by type |
| **Strategy** | Pricing strategies |
| **Observer** | Vehicle status updates |

## Compilation and Execution

To compile and run the project for any version (e.g., v1-basic), use the following commands from the root directory of the project:

### Compile
```bash
find java/v1-basic -name '*.java' | xargs javac -encoding UTF-8 -d out
```

### Run
```bash
java -cp out CarRentalDemo
```
