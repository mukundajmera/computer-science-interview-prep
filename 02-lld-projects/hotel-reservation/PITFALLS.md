# Hotel Reservation System — Common Interview Pitfalls

Common failure patterns and what to do instead.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. Missing Concurrency Control for Room Inventory
- **Pitfall**: Querying for an available room and creating a booking without any locking mechanism.
- **Why it hurts**: Leads to double-booking the exact same room for overlapping dates during high traffic.
- **Better**: Use proper database transactions with row-level locks, or optimistic concurrency control on inventory records.

## 2. Inefficient Search Mechanism
- **Pitfall**: Iterating through all rooms in the application memory to check date overlaps for availability.
- **Why it hurts**: Highly inefficient; will crash or timeout as the number of rooms and bookings grows.
- **Better**: Design the database schema to handle date range queries efficiently (e.g., using PostGIS/range types or pre-calculated availability tables).

## 3. Confusing Room Types with Physical Rooms
- **Pitfall**: Modeling a booking against a general "Deluxe Room" string rather than a specific physical room ID, OR mapping directly to a room ID too early.
- **Why it hurts**: Leads to inventory mismanagement or prevents optimal room assignment algorithms.
- **Better**: Clearly distinguish between `RoomType` (for searching/booking) and physical `Room` (for check-in allocation).

## 4. Hardcoding Pricing Logic
- **Pitfall**: Embedding fixed daily rates directly in the reservation class.
- **Why it hurts**: Cannot support dynamic pricing, weekend surges, seasonal variations, or discount codes.
- **Better**: Abstract pricing logic into a dedicated Strategy pattern or Pricing Engine Service.

## 5. Poor Handling of Time Zones
- **Pitfall**: Storing check-in/check-out dates using local server time without timezone metadata.
- **Why it hurts**: Causes massive confusion for international bookings and hotel operating hours.
- **Better**: Always store dates in UTC and convert to the specific hotel's local time at the application boundary.

## 6. Coupling Booking with Payment
- **Pitfall**: Making the reservation process fail completely if the immediate payment gateway call fails.
- **Why it hurts**: Poor user experience; many systems allow booking with a grace period for payment or "pay at hotel".
- **Better**: Decouple booking creation (state: Pending Payment) from payment processing using asynchronous updates.

## 7. Inflexible Cancellation Policies
- **Pitfall**: Hardcoding a simple "cancel equals full refund" logic.
- **Why it hurts**: Cannot model real-world complexities like non-refundable rates or partial refunds based on timing.
- **Better**: Use a Rules Engine or Strategy pattern to evaluate cancellation penalties dynamically based on the booking contract.

## 8. Lack of Audit Logging
- **Pitfall**: Overwriting reservation statuses (e.g., from Booked to Cancelled) without keeping history.
- **Why it hurts**: Impossible to audit discrepancies, resolve customer disputes, or track operational metrics.
- **Better**: Implement an append-only event log or audit trail for all mutating operations on a reservation.
