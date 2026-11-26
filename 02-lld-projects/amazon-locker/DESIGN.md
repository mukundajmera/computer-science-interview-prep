# Amazon Locker Design

## Core entities

| Entity | Responsibility |
|---|---|
| `Locker` | Deposit/pickup orchestration, token map, cleanup operations |
| `Compartment` | Physical slot state and compatibility checks |
| `AccessToken` | Code, expiry, compartment mapping |
| `AllocationPolicy` (v2+) | Exact-size or fallback-size selection |
| `Reservation` (v3+) | Reserve-confirm lifecycle |

## Key APIs

### `Locker`
- `depositPackage(size) -> tokenCode | error`
- `pickupPackage(tokenCode) -> bool`
- `clearExpiredDeposits() -> int`
- `reserveCompartment(size) -> reservationId` (v3)
- `confirmDeposit(reservationId) -> tokenCode` (v3)
- `cancelReservation(reservationId) -> bool` (v3)

### `Compartment`
- `isAvailable()`
- `markOccupied()`
- `markAvailable()`
- `markOutOfService()` / `markInService()` (v2+)

## Invariants
1. At most one active token per occupied compartment.
2. Pickup with valid token invalidates the token.
3. Expired tokens cannot be used for pickup.
4. Out-of-service compartments are never allocatable.

## Complexity
- Allocation scan: O(n compartments)
- Pickup by token: O(1) map lookup + O(1) state updates
- Expiry cleanup: O(active tokens)
