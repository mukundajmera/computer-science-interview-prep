# 🏆 Coach Answer: Amazon Locker — LLD

> **Type:** Low-Level Design  
> **Difficulty:** Intermediate  
> **Time Target:** 45 minutes

---

## 1. Requirements Clarification

### Functional
1. Accept package deposit by size (`SMALL`, `MEDIUM`, `LARGE`).
2. Allocate a compatible compartment and issue an access token.
3. Allow pickup by token and release the corresponding compartment.
4. Reject invalid or expired tokens.
5. Support periodic cleanup for expired deposits.

### Non-Functional
- Deterministic IDs and time-driven behavior for tests.
- Standard-library-only implementation.
- Extendable allocation policy and reservation lifecycle.

---

## 2. API Contract & Reference Behavior

Both Java and Python implement the identical reference contracts across versions. Tests deterministically cover the following scenarios:

- **Normal Use-Case:** Depositing a `SMALL` package allocates an available compartment, marks it occupied, and returns a valid token. Picking up with the valid token releases the compartment.
- **Empty/Invalid Input:** Calling `pickup` with `None`/`null` or a non-existent/expired token string immediately returns false without altering locker state.
- **Duplicate Operation:** Picking up a package twice with the same valid token returns `true` on the first call, and `false` on subsequent calls (token is invalidated).
- **Capacity Boundaries:** If all compartments of a requested size (and fallbacks in v2) are occupied, `depositPackage` returns `None`/`null` (cash inventory equivalent).
- **Failure Rollbacks:** If a token is successfully generated but the deposit unexpectedly fails or token is expired, the system safely rolls back (via explicit timeout clear) or ensures state consistency.

---

## 3. Version-Specific Feature Deltas

### v1-basic (Exact Match & Expiry)
Focuses on the core lifecycle of a locker.
- **API:**
  - `Locker.depositPackage(size) -> tokenCode | error`
  - `Locker.pickup(tokenCode) -> bool`
  - `Locker.clearExpiredDeposits() -> int`
- **Behavior:** Deposits strictly map to a compartment of the exact size. Time is deterministically mocked via an injected clock to verify expired token cleanup without waiting.

### v2-extended (Fallback Policy & Maintenance)
Introduces the Strategy Pattern to abstract allocation rules and handles operational downtime.
- **API:**
  - `Compartment.markOutOfService()` and `Compartment.markInService()`
- **Behavior:** Uses an `AllocationPolicy` (e.g., `FallbackAllocationPolicy`) to upgrade packages to larger compartments if the exact size is fully occupied. Out-of-service compartments are strictly bypassed.

### v3-optimized (Reservation Flow)
Decouples intent-to-deposit from physical confirmation, modeling a real delivery driver's workflow.
- **API:**
  - `Locker.reserveCompartment(size) -> reservationId`
  - `Locker.confirmDeposit(reservationId) -> tokenCode`
  - `Locker.cancelReservation(reservationId) -> bool`
- **Behavior:** Introduces a `RESERVED` state. A reservation locks the compartment but does not issue a customer token until explicitly confirmed. Unused reservations eventually expire during cleanup.

---

## 4. Core Architecture

| Entity | Responsibility |
|---|---|
| `Locker` | Deposit/pickup orchestration, token and reservation maps |
| `Compartment` | Physical slot state and serviceability |
| `AccessToken` | Token identity + expiry semantics |
| `AllocationPolicy` (v2+) | Exact-size vs fallback-size allocation |
| `Reservation` (v3+) | Reserve-confirm-cancel lifecycle |
| `Clock` (v3+) | Injectable time source for deterministic tests |

---

## 5. Design Notes & Complexity

- **Explicit State Transitions:** Compartments transition explicitly between `AVAILABLE`, `RESERVED`, and `OCCUPIED`.
- **Clock Injection:** Thread-safe determinism is achieved by injecting a clock interface (or function), eliminating `Thread.sleep` and allowing instant expiry testing.
- **Concurrency Defenses:** (If scaled) Lock-free thread-safe maps and atomic variables prevent double-allocating a single compartment when concurrent delivery drivers request reservations.

### Time & Space Complexity
- **Allocation Scan:** `O(n)` where `n` is the number of compartments.
- **Pickup:** `O(1)` token lookup + `O(1)` state update.
- **Cleanup:** `O(t)` where `t` is the number of active tokens or reservations.
