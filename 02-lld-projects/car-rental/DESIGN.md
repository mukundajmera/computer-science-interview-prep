# Design for Car Rental System

## Mermaid Class Diagram

```mermaid
classDiagram
    class RentalService {
        <<Singleton>>
        -Map~String, Vehicle~ vehicles
        -Map~String, Customer~ customers
        -Map~String, Reservation~ reservations
        -PricingStrategy pricingStrategy
        +searchAvailable(VehicleType, LocalDate, LocalDate) List~Vehicle~
        +makeReservation(String, String, LocalDate, LocalDate) Reservation
        +pickupVehicle(String) RentalAgreement
        +returnVehicle(String, DamageReport) Payment
        +cancelReservation(String) boolean
    }

    class Vehicle {
        -String vehicleId
        -String licensePlate
        -String make
        -String model
        -VehicleType type
        -VehicleStatus status
        -double pricePerDay
        -String location
        -int mileage
        -List~DamageReport~ damageHistory
        +isAvailable(LocalDate, LocalDate) boolean
        +updateStatus(VehicleStatus) void
        +addDamageReport(DamageReport) void
    }

    class Customer {
        -String customerId
        -String name
        -String email
        -String phone
        -String drivingLicense
        -List~Reservation~ reservations
        +addReservation(Reservation) void
        +getActiveReservation() Reservation
        +cancelReservation(String) boolean
    }

    class Reservation {
        -String reservationId
        -Customer customer
        -Vehicle vehicle
        -LocalDate startDate
        -LocalDate endDate
        -ReservationStatus status
        -InsuranceType insurance
        -double totalCost
        -Payment payment
        +confirm() void
        +cancel() void
        +startRental() RentalAgreement
        +completeRental() void
        +calculateCost() double
    }

    class RentalAgreement {
        -String agreementId
        -Reservation reservation
        -LocalDateTime pickupTime
        -LocalDateTime returnTime
        -int startMileage
        -int endMileage
        -String pickupLocation
        -String returnLocation
    }

    class Payment {
        -String paymentId
        -Reservation reservation
        -double amount
        -PaymentMethod method
        -PaymentStatus status
        -LocalDateTime transactionDate
        +process() boolean
        +refund() boolean
    }

    class DamageReport {
        -String reportId
        -Vehicle vehicle
        -String description
        -DamageSeverity severity
        -double estimatedCost
        -LocalDate reportDate
        +calculateRepairCost() double
    }

    class PricingStrategy {
        <<interface>>
        +calculatePrice(Vehicle, int) double
    }

    class HourlyPricing {
        +calculatePrice(Vehicle, int) double
    }

    class DailyPricing {
        +calculatePrice(Vehicle, int) double
    }

    class WeeklyPricing {
        +calculatePrice(Vehicle, int) double
    }

    class VehicleType {
        <<enumeration>>
        CAR
        SUV
        TRUCK
        VAN
        LUXURY
    }

    class VehicleStatus {
        <<enumeration>>
        AVAILABLE
        RESERVED
        RENTED
        MAINTENANCE
        OUT_OF_SERVICE
    }

    class ReservationStatus {
        <<enumeration>>
        PENDING
        CONFIRMED
        ACTIVE
        COMPLETED
        CANCELLED
    }

    class DamageSeverity {
        <<enumeration>>
        MINOR
        MODERATE
        SEVERE
    }

    RentalService --> PricingStrategy : uses
    RentalService "1" --> "n" Vehicle : manages
    RentalService "1" --> "n" Customer : manages
    RentalService "1" --> "n" Reservation : tracks
    PricingStrategy <|.. HourlyPricing
    PricingStrategy <|.. DailyPricing
    PricingStrategy <|.. WeeklyPricing
    Customer "1" --> "n" Reservation : makes
    Reservation --> Vehicle
    Reservation --> Customer
    Reservation --> Payment
    Reservation --> RentalAgreement
    Vehicle "1" --> "n" DamageReport : has
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    BRANCH ||--o{ VEHICLE : has
    VEHICLE ||--o{ RESERVATION : reserved_for
    CUSTOMER ||--o{ RESERVATION : makes
    RESERVATION ||--|| RENTAL_AGREEMENT : becomes
    RESERVATION ||--|| PAYMENT : has
    VEHICLE ||--o{ DAMAGE_REPORT : has
    RENTAL_AGREEMENT ||--o| DAMAGE_REPORT : may_have

    BRANCH {
        string branch_id PK
        string name
        string address
        string city
        string phone
    }

    VEHICLE {
        string vehicle_id PK
        string branch_id FK
        string license_plate UK
        string make
        string model
        int year
        string type
        string status
        decimal price_per_day
        int mileage
    }

    CUSTOMER {
        string customer_id PK
        string name
        string email UK
        string phone
        string driving_license UK
        string address
        timestamp created_at
    }

    RESERVATION {
        string reservation_id PK
        string customer_id FK
        string vehicle_id FK
        date start_date
        date end_date
        string status
        string insurance_type
        decimal total_cost
        timestamp created_at
    }

    RENTAL_AGREEMENT {
        string agreement_id PK
        string reservation_id FK
        datetime pickup_time
        datetime return_time
        int start_mileage
        int end_mileage
        string pickup_location
        string return_location
        text terms_accepted
    }

    PAYMENT {
        string payment_id PK
        string reservation_id FK
        decimal amount
        string method
        string status
        timestamp transaction_date
    }

    DAMAGE_REPORT {
        string report_id PK
        string vehicle_id FK
        string agreement_id FK
        text description
        string severity
        decimal repair_cost
        date report_date
    }
```

**Schema Notes:**
- `BRANCH` supports multi-location rental operations
- `RESERVATION` tracks booking before actual rental
- `RENTAL_AGREEMENT` captures pickup/return details
- `DAMAGE_REPORT` can be linked to specific rental or general vehicle history

---

## Class Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Customer     │     │   Reservation   │     │     Vehicle     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ - customerId    │     │ - reservationId │     │ - vehicleId     │
│ - name          │1   *│ - startDate     │*   1│ - licensePlate  │
│ - email         │────▶│ - endDate       │────▶│ - make          │
│ - drivingLicense│     │ - status        │     │ - model         │
│ - reservations  │     │ - insurance     │     │ - type          │
└─────────────────┘     │ - totalCost     │     │ - status        │
                        └────────┬────────┘     │ - location      │
                                 │              └────────┬────────┘
                                 │                       │
                        ┌────────▼────────┐     ┌────────▼────────┐
                        │    Payment      │     │  DamageReport   │
                        ├─────────────────┤     ├─────────────────┤
                        │ - paymentId     │     │ - reportId      │
                        │ - amount        │     │ - description   │
                        │ - status        │     │ - severity      │
                        │ - method        │     │ - repairCost    │
                        └─────────────────┘     └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      PricingStrategy                             │
├─────────────────────────────────────────────────────────────────┤
│ + calculatePrice(vehicle, duration): double                      │
└─────────────────────────────────────────────────────────────────┘
                              △
          ┌───────────────────┼───────────────────┐
          │                   │                   │
┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
│  HourlyPricing    │ │ DailyPricing  │ │  WeeklyPricing    │
├───────────────────┤ ├───────────────┤ ├───────────────────┤
│ + calculatePrice()│ │+ calculatePrice│ │ + calculatePrice()│
└───────────────────┘ └───────────────┘ └───────────────────┘
```

## Core Classes

### Vehicle
- **Attributes**: vehicleId, licensePlate, make, model, type, status, pricePerDay, location, mileage
- **Methods**: isAvailable(startDate, endDate), updateStatus(), addDamageReport()
- **Patterns Used**: Factory pattern for creation

### VehicleType (Enum)
- CAR, SUV, TRUCK, VAN, LUXURY

### VehicleStatus (Enum)
- AVAILABLE, RESERVED, RENTED, MAINTENANCE, OUT_OF_SERVICE

### Customer
- **Attributes**: customerId, name, email, phone, drivingLicense, reservations
- **Methods**: addReservation(), getActiveReservation(), cancelReservation()

### Reservation
- **Attributes**: reservationId, customer, vehicle, startDate, endDate, status, insurance, totalCost, payment
- **Methods**: confirm(), cancel(), startRental(), completeRental(), calculateCost()
- **Patterns Used**: State pattern for status management

### ReservationStatus (Enum)
- PENDING, CONFIRMED, ACTIVE, COMPLETED, CANCELLED

### PricingStrategy (Interface)
- **Methods**: calculatePrice(vehicle, durationHours)
- **Implementations**: HourlyPricing, DailyPricing, WeeklyPricing

### DamageReport
- **Attributes**: reportId, vehicle, description, severity, estimatedCost, reportDate
- **Methods**: calculateRepairCost()

### DamageSeverity (Enum)
- MINOR, MODERATE, SEVERE

### Payment
- **Attributes**: paymentId, reservation, amount, status, method, transactionDate
- **Methods**: process(), refund()

### PaymentStatus (Enum)
- PENDING, COMPLETED, REFUNDED, FAILED

### RentalService (Singleton)
- **Attributes**: vehicles, customers, reservations
- **Methods**: searchAvailable(), makeReservation(), pickupVehicle(), returnVehicle()
- **Patterns Used**: Singleton, Facade

## Key Design Decisions

1. **Factory for Vehicles**: Allows easy creation of different vehicle types with appropriate base pricing
2. **Strategy for Pricing**: Enables flexible pricing (hourly for short, weekly for long rentals)
3. **State for Reservations**: Clean state transitions with validation
4. **Singleton for Service**: Single point of access, ensures consistency

## Trade-offs

| Decision | Pros | Cons |
|----------|------|------|
| In-memory storage | Fast, simple | Not persistent |
| Date-based availability | Accurate | Complex overlap checks |
| Lock per vehicle | Fine-grained | Memory overhead |

## Complexity Analysis

- **Search available**: O(V) where V = vehicles
- **Make reservation**: O(1) with HashMap
- **Return vehicle**: O(1)
- **Space**: O(V + R + C) for vehicles, reservations, customers
