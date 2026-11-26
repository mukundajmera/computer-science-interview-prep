# Strong Answer: Car Rental System

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Car Rental System, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."
- **Normal use-cases:** Customers can search for available vehicles, make reservations for a specific date range, pick up vehicles, and return them. We track branches and dynamic pricing based on inventory availability and seasonal variations.
- **Empty/invalid input:** Requesting a vehicle that is not available for the requested dates correctly triggers an exception or rejection.
- **Duplicate operations:** A customer cancelling a reservation twice or making overlapping reservations on the same vehicle should be handled smoothly without state corruption.
- **Capacity boundary:** Attempting to book a vehicle when inventory availability reaches 0% must fail safely.
- **Failure rollback:** If a transaction fails mid-update (e.g., failure in saving a reservation record), the vehicle's availability status must gracefully rollback to prevent overbooking or ghost reservations.

## 2. Entity Modeling & APIs (10 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."
We define `Vehicle`, `Customer`, `Reservation`, `RentalService`, `DamageReport`, and `Payment`.
Public APIs in `RentalService`:
- `searchAvailable(VehicleType type, LocalDate startDate, LocalDate endDate) List<Vehicle>`
- `makeReservation(String customerId, String vehicleId, LocalDate startDate, LocalDate endDate) Reservation`
- `pickupVehicle(String reservationId) RentalAgreement`
- `returnVehicle(String reservationId, DamageReport damage) Payment`
- `cancelReservation(String reservationId) boolean`

In version-specific deltas, `v1-basic` covers fundamental reservation flow. `v2-extended` covers custom vehicle equipment add-ons (GPS, Child Seat) and late return penalty strategies. `v3-optimized` handles dynamic seasonal pricing, inventory surge multipliers, and branch transfers.

## 3. Data Structure & Design Alternatives (10 mins)
**Say:** "Choosing the right data structures is critical for meeting our latency and throughput requirements."
We use Maps for quick lookup: `Map<String, Vehicle>`, `Map<String, Customer>`, `Map<String, Reservation>`, and `Map<String, Branch>`.
*Design Alternatives:* A relational database would handle date-range availability checks smoothly with overlapping range queries (e.g., `START <= end_date AND END >= start_date`). For in-memory representations, checking all vehicles sequentially or using an Interval Tree per vehicle are options. Here, we iterate through vehicles and check their internal reservation lists using `Vehicle.isAvailable(LocalDate, LocalDate)`.

## 4. Design Pattern Justifications (5 mins)
**Say:** "To keep the system modular and maintainable, I've applied specific design patterns."
- **Singleton Pattern:** For the `RentalService` entry point.
- **Strategy Pattern:** For pricing algorithms (`HourlyPricing`, `DailyPricing`, `WeeklyPricing`, and `PricingStrategy` interface).
- **State/Status Pattern:** Managing `VehicleStatus` (AVAILABLE, RESERVED, RENTED) and `ReservationStatus`.
- **Factory Pattern:** `Vehicle` creation pattern (Allows easy creation of different vehicle types with appropriate base pricing).

## 5. Concurrency Defense & Thread-Safety Details (10 mins)
**Say:** "Given that this system will be accessed by multiple threads concurrently, ensuring thread safety without creating bottlenecks is a priority."
*Concrete Failure / Concurrency Discussion:* Consider a scenario where two customers try to book the exact same `Vehicle` at the same time. If they both evaluate `Vehicle.isAvailable(startDate, endDate)` simultaneously, both might see it as true, leading to overbooking. 
To prevent this, the `makeReservation` method in Java is explicitly marked as `synchronized` (`public synchronized Reservation makeReservation(...)`), acting as a global lock or monitor, guaranteeing only one reservation is processed at a time. In Python, an equivalent Threading `Lock` is necessary.

## 6. Failure Handling (3 mins)
**Say:** "Systems fail, so we need to anticipate and handle failures gracefully at the lowest level."
If transferring a vehicle fails because the target branch is full, the state must not reflect the vehicle in limbo. 

## 7. Production Trade-offs (2 mins)
**Say:** "In a real production environment, this in-memory design would require certain trade-offs."
Synchronizing the entire `makeReservation` method provides safety but creates a severe concurrency bottleneck at scale. A better production approach is fine-grained locking on the specific `Vehicle` object, or using optimistic concurrency control (e.g., Row Versioning in a Database) to improve throughput while avoiding overbooking.
