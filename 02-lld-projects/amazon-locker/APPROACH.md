# Approach for Amazon Locker System

## Overview and Core Strategy
The Amazon Locker system orchestrates the allocation, reservation, and management of physical storage compartments for packages. It matches incoming packages of varying sizes to physical compartments, manages access credentials via tokens, and transitions compartments between different operational states based on usage and maintenance requirements.

The implementation is structured around a central `Locker` orchestrator coordinating stateful `Compartment` objects. Instead of a database, the system uses in-memory collections and time-based state transitions (e.g., token expiration, reservation timeouts) controlled via a deterministic clock interface to ensure exact parity and testability across both Java and Python.

## Public APIs & Version Deltas

### v1-basic: Exact Size Allocation
Focuses on the core flow of depositing and retrieving a package using exact-size matching.
*   **`depositPackage(size: PackageSize) -> str`**: Finds an available compartment matching the requested size exactly, marks it `OCCUPIED`, generates a unique token (e.g., `T-1`), and maps the token to the compartment. Returns `None`/`null` if at capacity.
*   **`pickup(tokenCode: str) -> bool`**: Validates the token against the active mapping and expiry time. If valid, it releases the compartment to `AVAILABLE` and destroys the token.
*   **`clearExpiredDeposits() -> int`**: Sweeps active tokens, invalidating any that have passed their TTL. Associated compartments are marked `AVAILABLE` and the count of cleared deposits is returned.

### v2-extended: Strategy Pattern and Maintenance
Introduces allocation strategies and manual maintenance overrides.
*   **`setAllocationPolicy(policy: AllocationPolicy)`**: Dynamically injects an allocation strategy (e.g., `ExactSizePolicy` or `FallbackSizePolicy`). The fallback policy attempts to upgrade small packages to larger compartments if exact matches are exhausted.
*   **`markCompartmentOutOfService(compartmentId: str) -> bool`**: Transitions a compartment's status to `OUT_OF_SERVICE`. Allocation policies actively skip out-of-service compartments. Returns `False` if the compartment is currently `OCCUPIED` or does not exist.

### v3-optimized: Two-Phase Reservation
Introduces a two-phase commit pattern to reserve compartments before finalizing deposits, mimicking scenarios where a courier requests a slot before physically arriving.
*   **`reserveCompartment(size: PackageSize) -> str`**: Allocates a compartment and places it in a `RESERVED` state. Returns a reservation ID (e.g., `R-1`). If unused within the `reservation_ttl`, the reservation implicitly expires.
*   **`confirmDeposit(reservationId: str) -> str`**: Upgrades a pending reservation to an active deposit. Generates the final access token and transitions the compartment to `OCCUPIED`. Fails if the reservation has timed out or was cancelled.
*   **`cancelReservation(reservationId: str) -> bool`**: Aborts a pending reservation, immediately returning the compartment to `AVAILABLE`.
*   **`expireReservations() -> int`**: Sweeps active reservations, transitioning those past their TTL to `EXPIRED` and releasing their compartments.

## Explicit Reference Contracts

The implementation guarantees the following behaviors uniformly across both Java and Python:

*   **Normal Use-Case**: A successful deposit generates a unique token that immediately grants access to the `pickup` function, releasing the compartment for subsequent use. In v3, a successful reservation guarantees a slot for `confirmDeposit` within the TTL window.
*   **Empty/Invalid Input**: Attempting to pickup with a non-existent or structurally invalid token (e.g., empty string, `null`) returns `False` without modifying system state. Similarly, confirming an invalid reservation ID fails safely.
*   **Duplicate Operation**: `pickup` acts as a one-time operation. A successful pickup invalidates the token, meaning any immediate duplicate call with the same token will deterministically return `False`.
*   **Capacity Boundary**: If the locker is full (or lacking compartments of the required size under the active policy), `depositPackage` (or `reserveCompartment`) will deterministically return `null` (Java) or `None` (Python). The system does not queue or block; it fails fast.
*   **Failure Rollback (Timeouts)**: If a deposit is forgotten (token expires) or a reservation is abandoned (reservation expires), calling the sweep functions (`clearExpiredDeposits`, `expireReservations`) successfully rolls back the allocation. The compartment is marked `AVAILABLE` and can be immediately assigned to a new request, guaranteeing no permanent resource leaks.
