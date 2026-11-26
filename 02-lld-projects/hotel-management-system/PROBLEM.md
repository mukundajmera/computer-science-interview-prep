# Hotel Management System

## Problem Statement

Design a Hotel Management System that acts as the operational backbone of a hotel. Distinct from a Reservation System (which handles online bookings before arrival), the Management System handles on-site operations. Core functions include managing housekeeping statuses, guest check-in/check-out processes, issuing and tracking room keys, managing the folio ledger (billing), and tracking service item charges (e.g., room service, spa, minibar).

## Requirements

1. **Housekeeping Management**: 
   - Rooms have statuses such as `CLEAN`, `DIRTY`, and `INSPECTED`.
   - Housekeeping staff should be able to update room statuses.
   - Rooms can only be checked into if they are `INSPECTED` (or at least `CLEAN` depending on policy, but we will assume `INSPECTED` for best practice).

2. **Check-in / Check-out**:
   - Guests check-in upon arrival, changing the room status to `OCCUPIED`.
   - Upon check-out, the folio is settled, and the room status changes to `DIRTY`.

3. **Room Keys**:
   - Issue physical/digital room keys upon check-in.
   - Keys must be uniquely identifiable and linked to a specific room and active stay.
   - Deactivate keys upon check-out or loss.

4. **Folio Ledger Billing**:
   - Maintain a master folio for each stay.
   - The folio must aggregate all base room charges and incidental service charges.
   - Support for partial or full payments.

5. **Service Item Charges**:
   - Ability to post charges to a room's folio for amenities like room service, laundry, spa, minibar, etc.
   - Each charge must be itemized with timestamp, description, and amount.

## Core Operations

1. `checkIn(reservationId, guestDetails)` -> Assigns room, issues key, starts folio.
2. `checkOut(roomId)` -> Settles folio, invalidates key, marks room `DIRTY`.
3. `updateHousekeepingStatus(roomId, newStatus)` -> Changes room state.
4. `issueRoomKey(roomId, keyId)` -> Activates a new key.
5. `postCharge(roomId, chargeDetails)` -> Adds item to the folio.
6. `settleFolio(roomId, amount)` -> Applies payment to the folio.

## Constraints & Assumptions

- All charges are tied to an active folio (meaning the room must be currently occupied).
- Housekeeping must mark a room as `INSPECTED` before it can be assigned to a new guest.
- Concurrency: Multiple staff might try to update housekeeping status or post charges simultaneously. Thread safety is critical, particularly for folio updates.

## Acceptance Criteria
1. Dirty/out-of-service rooms cannot be allocated until the agreed housekeeping transition; overlapping stays use half-open dates and atomic room ownership.
2. Folio charges/payment/refund replay preserve integer-minor-unit balances; concurrent check-in, checkout and maintenance reservation cannot double-assign a room.
3. Version-specific APIs and deterministic fixture inputs/expected outputs are fixed before implementation; no production/security promise is inferred.
