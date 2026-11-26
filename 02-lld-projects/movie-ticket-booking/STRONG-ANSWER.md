# Strong Answer: Movie Ticket Booking — LLD

**Pacing Target:** 45 minutes

## 1. Introduction & Explicit Clarifications (5 mins)
**Say:** "Before I design the Movie Ticket Booking system, I'll clarify the core constraints. The main challenge is concurrency—how do we ensure two users don't book the same seat simultaneously? We must guarantee all-or-none seat acquisition. Are we supporting dynamic pricing? Yes. Can a user hold a seat and pay later? Yes, typically a 10-minute hold with a TTL expiry."

## 2. Entities & APIs (10 mins)
**Say:** "Let's define the primary entities and the core API contract."
- **Entities:** `Theater`, `Screen`, `Movie`, `Show`, `Seat`, `ShowSeat`, and `Booking`.
- **API Contract:**
  - `lockSeats(showId, seatIds, userId, clock) -> bookingId | error`
  - `confirmBooking(bookingId, paymentToken) -> success | error`
  - `releaseSeats(bookingId) -> void`
  - `getAvailableSeats(showId) -> List<ShowSeat>`

## 3. Data Structure Rationale & Design Alternatives (10 mins)
**Say:** "For seat availability queries, a standard list or array works, but for highly concurrent lock acquisition, we need constant-time lookup and thread safety."
- **Design Alternative 1: Pessimistic Locking (RDBMS)**. A traditional approach uses `SELECT FOR UPDATE` in a relational database. This prevents dirty reads but creates contention locking the row.
- **Design Alternative 2: In-Memory Concurrent Maps (Chosen for LLD)**. We map a `ShowID` to a `ConcurrentHashMap` of `ShowSeat` objects. Each `ShowSeat` maintains its lock status, owner, and lock timestamp.

## 4. Concurrency Defense & Correctness/Complexity (10 mins)
**Say:** "Handling overlapping multi-seat holds is the crux of the problem. We must yield at most one owner per seat and guarantee all-or-none acquisition."
- **All-or-None Acquisition:** When a user requests multiple seats, we must acquire all locks or fail entirely.
- **Deadlock Prevention:** Overlapping holds can cause deadlocks if User A locks Seat 1 then waits for Seat 2, while User B locks Seat 2 and waits for Seat 1. We prevent this by sorting seat IDs lexicographically before attempting to acquire locks sequentially. Bounded joins or timeouts on the lock attempt act as a fail-safe.
- **Complexity:** Locking seats takes O(K log K) to sort the requested seats, and O(K) to acquire locks (where K is the number of seats requested).

## 5. Failure Handling & Concrete Concurrency Discussion (10 mins)
**Say:** "Failures such as dropped checkouts and stale callbacks must not corrupt the seat state or sell a seat twice."
- **TTL Expiry & Injected Time:** A time-to-live (TTL) on seat holds ensures that if a payment fails or a session is dropped, seats become available. For testability and correctness, we inject a monotonic `Clock` rather than relying on `System.currentTimeMillis()`. This allows us to deterministically test TTL expiry and hold refresh.
- **Stale Confirmations:** If a payment callback is delayed and arrives after the TTL expired (and the seat was potentially released and acquired by another user), the system validates the `Booking` state and the current owner of the `ShowSeat`. If the owner has changed or the booking is marked expired, the late payment is rejected or refunded.
- **Duplicate Seat IDs:** The API rejects requests containing duplicate seat IDs in the payload to prevent self-deadlock or double counting.
