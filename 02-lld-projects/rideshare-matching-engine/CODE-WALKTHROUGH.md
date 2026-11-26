# Rideshare Matching Engine - Code Walkthrough

This walkthrough outlines how the Java and Python implementations map to the system's design requirements.

## File Structure Map
* **Models**: `Driver`, `Rider`, `Trip`, `Location`, `DriverState`, `TripState`.
  * In Python: `rideshare/models.py`.
  * In Java: `src/*.java`.
* **Engines**: `PricingEngine`, `MatchingEngine`.
  * In Python: `v1-basic/engine.py`, `v2-extended/rideshare_matching_engine.py`, `v3-optimized/rideshare_matching_engine.py`.
  * In Java: `v1-basic/MatchingEngine.java`, `v2-extended/RideshareMatchingEngine.java`, `v3-optimized/RideshareMatchingEngine.java`.
* **Tests**: Focused tests target specific versions rather than silently importing v1, verifying FSM, spatial ranking, dynamic pricing, and concurrent atomic assignment.
  * In Python: `tests/test_rideshare.py`, `tests/test_v2_rideshare.py`, `tests/test_v3_rideshare.py`.
  * In Java: `tests/RideshareMatchingEngineTest.java`, `tests/V2RideshareMatchingEngineTest.java`, `tests/V3RideshareMatchingEngineTest.java`.

## Reference Contracts in Code
Tests and engines implement explicit contracts:
- **Normal Use-Case:** `requestRide()` successfully returns an assigned `Trip`.
- **Empty/Invalid Input:** Requests with no available drivers handle capacity boundaries by returning gracefully (e.g., null or unassigned).
- **Duplicate Operation:** Locks in `transitionState()` ensure concurrent threads safely compete for the same driver.
- **Capacity Boundary:** The `PricingEngine` scales safely when supply is exhausted.
- **Failure Rollback:** If trip creation or assignment throws an error, the driver state is rolled back to `IDLE` to prevent permanent resource leaks.

## Lifecycle Management
The `Driver` model encapsulates an internal `transitionState` method. This method internally holds a lock. It verifies if the passed state transition is valid against a hardcoded set of valid transition paths (e.g., `IDLE` -> `ACCEPTED` -> `ARRIVED` -> `IN_TRIP` -> `COMPLETED` -> `IDLE`). If valid, the state is updated and the method returns `true`.

## Concurrent Driver Allocation
The `MatchingEngine.requestRide()` method is the core path. When concurrent requests occur:
1. `findNearestDrivers()` safely retrieves a snapshot of `IDLE` drivers.
2. The engine iterates over this list, attempting `driver.transitionState(DriverState.ACCEPTED)`.
3. Because `transitionState` is synchronized (via `RLock` or `ReentrantLock`), only the first thread invoking it on an `IDLE` driver will succeed.
4. If a thread fails to transition a driver, it continues to the next nearest driver. This ensures exactly one driver is assigned per trip, and no driver handles two trips simultaneously.

## Surge Pricing Calculation
The `PricingEngine` increments `availableDrivers` and `activeRequests`. A lock protects these variables. `calculateSurgeMultiplier()` calculates `activeRequests / availableDrivers`. If the ratio > 2.0, a multiplier of `2.0` is used. If ratio > 1.0, `1.5` is used.

