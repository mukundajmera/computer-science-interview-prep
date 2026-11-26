# Approach

## 1. Requirement Analysis & Core Entities

The system needs to manage physical assets (Rooms, Keys), operational workflows (Housekeeping, Check-in/out), and financial records (Folio, Charges).

### Entities

- **Room**: Represents the physical room. Attributes include ID, Room Type, Housekeeping Status, and Occupancy Status.
- **RoomKey**: Represents an access card. Linked to a Room and has an Active/Inactive status.
- **Folio**: The financial ledger for a stay. Contains a list of `Charge` items and a balance.
- **Charge**: An individual line item on a folio (e.g., Minibar, Room Service).
- **Stay / GuestSession**: Links a Guest, a Room, a Folio, and active Room Keys.

## 2. System Architecture & Workflows

1. **Housekeeping Workflow**: 
   - A state machine governs room cleanliness: `DIRTY` -> `CLEAN` -> `INSPECTED`.
   - When a guest checks out, the room automatically transitions to `DIRTY`.

2. **Check-in Workflow**:
   - Verify reservation (if applicable) and guest details.
   - Find an available room that is `INSPECTED`.
   - Create a `Stay` session.
   - Initialize a `Folio`.
   - Issue `RoomKey`(s) and mark room as `OCCUPIED`.

3. **Billing Workflow**:
   - Any service (e.g., restaurant) can post a `Charge` to the room's active `Folio`.
   - The `Folio` must handle concurrent charge postings safely (e.g., using locks or thread-safe collections).

4. **Check-out Workflow**:
   - Verify the `Folio` balance is zero. If not, prompt for payment.
   - Deactivate all active `RoomKey`s associated with the stay.
   - Close the `Stay`.
   - Change the room occupancy to `VACANT` and cleanliness to `DIRTY`.

## 3. Concurrency & Thread Safety

- **Folio Ledger**: Multiple services (restaurant, spa, minibar) might post charges concurrently to the same room. A `ReentrantLock` or synchronized block on the `Folio` is necessary to prevent lost updates.
- **Room Booking/Assignment**: Two front-desk agents might try to check guests into the same available room simultaneously. The room assignment process requires a global lock or optimistic concurrency control on the room's state.

## 4. Design Patterns

- **State Pattern**: For managing Room Housekeeping Status (`DIRTY`, `CLEAN`, `INSPECTED`).
- **Strategy Pattern**: For applying different types of discounts or tax rates to charges (if extended later).
- **Observer Pattern**: When a room is marked `DIRTY`, notify the housekeeping department.

## 5. Acceptance Criteria Enforcement
1. **Housekeeping:** State transition constraints (`DIRTY` -> `CLEAN` -> `INSPECTED`) enforced strictly via state machine logic.
2. **Double Booking:** Atomic lock acquisition required on room assignment during check-in; overlapping stays are verified using half-open date logic `[checkInDate, checkOutDate)`.
3. **Financials:** All monetary calculations in `Folio` must use integer minor units (e.g., cents) to prevent floating-point precision loss. Refunds/replays must preserve balance integrities securely.
4. **Versioning:** APIs are strictly scoped into v1 (basic), v2 (thread-safe extended), and v3 (concurrent optimized) modules.
