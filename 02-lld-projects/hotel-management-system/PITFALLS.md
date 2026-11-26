# Pitfalls

1. **Confusing Reservation with Management**:
   - *Pitfall*: Designing a system focused on future bookings, date overlaps, and availability search.
   - *Counterexample*: Building complex date-range overlap SQL queries instead of focusing on the real-time `DIRTY` -> `CLEAN` -> `INSPECTED` state machine.
   - *Fix*: Focus on the on-site operational aspect: present moment check-ins and real-time billing.

2. **Race Conditions in Billing**:
   - *Pitfall*: Using standard collections (`ArrayList`, `list`) for the Folio's charges without locks, leading to lost charges if the spa and restaurant bill the room simultaneously.
   - *Counterexample*: `balance += amount` without a lock. If thread A reads 0, thread B reads 0, both add 50, balance becomes 50 instead of 100.
   - *Fix*: Protect the Folio with a `ReentrantLock` (Java) or `threading.Lock` (Python), or use atomic concurrent data structures.

3. **Check-out without Settle**:
   - *Pitfall*: Allowing a guest to check out and the room to become vacant while an outstanding balance remains.
   - *Fix*: The `checkOut` method must validate that the `Folio` balance is zero before proceeding.

4. **Concurrent Billing during Checkout**:
   - *Pitfall*: Validating the balance is 0, but a concurrent charge is added right before the room is marked empty.
   - *Fix*: Remove the room from the `activeStays` mapping *before* checking the balance. If the balance is > 0, rollback the removal and throw an exception.
