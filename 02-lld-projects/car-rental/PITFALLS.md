# Car Rental System — Common Interview Pitfalls

Common failure patterns and what to do instead.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. Missing Concurrency Control for Inventory
- **Pitfall**: Querying for available cars and booking them without locking.
- **Why it hurts**: Leads to double-booking the same physical car for the same dates.
- **Better**: Use row-level locking (SELECT FOR UPDATE) or optimistic concurrency control (versioning) when booking.

## 2. Inefficient Search Mechanism
- **Pitfall**: Iterating through all cars in memory to check date overlaps.
- **Why it hurts**: Scales poorly (O(N) search time) as inventory grows.
- **Better**: Design the database schema to efficiently query availability (e.g., indexed date ranges or available vehicle views).

## 3. Ignoring Vehicle Lifecycle States
- **Pitfall**: Assuming a car is only "Available" or "Booked".
- **Why it hurts**: Fails to model reality (maintenance, cleaning, transit between branches).
- **Better**: Implement a robust state machine for the Vehicle entity (Available, Reserved, Rented, InMaintenance, Lost).

## 4. Hardcoding Pricing Logic
- **Pitfall**: Embedding fixed daily rates directly in the booking calculation.
- **Why it hurts**: Cannot support dynamic pricing, seasonal surges, or discount codes.
- **Better**: Abstract pricing logic into a dedicated Strategy pattern or Pricing Engine.

## 5. Poor Handling of Time Zones
- **Pitfall**: Storing reservation dates using local server time without timezone data.
- **Why it hurts**: Causes massive confusion for cross-country rentals and branch operating hours.
- **Better**: Always store dates/times in UTC and convert to local branch time at the UI boundary.

## 6. Coupling Booking with Payment
- **Pitfall**: Making the reservation process fail completely if immediate payment fails.
- **Why it hurts**: Poor user experience; many systems allow booking with delayed payment.
- **Better**: Decouple booking creation from payment processing using asynchronous events.

## 7. Inflexible Return Policies
- **Pitfall**: Hardcoding logic that assumes cars are returned to the same branch.
- **Why it hurts**: Prevents implementing one-way rentals.
- **Better**: Design the schema to support distinct pick-up and drop-off branch locations.

## 8. Overlooking Audit and History
- **Pitfall**: Overwriting vehicle status without keeping a history of rentals and maintenance.
- **Why it hurts**: Cannot track vehicle wear-and-tear or audit past rentals for fines.
- **Better**: Maintain an immutable `RentalRecord` or log for every vehicle transaction.
