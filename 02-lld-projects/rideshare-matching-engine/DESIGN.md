# Rideshare Matching Engine - Design Document

## Cross-links
* [Problem Statement](PROBLEM.md)
* [Approach](APPROACH.md)
* [Code Walkthrough](CODE-WALKTHROUGH.md)
* [Interview Scoring Rubric](RUBRIC.md)
* [Common Pitfalls](PITFALLS.md)
* [Follow-Up Questions](FOLLOW-UPS.md)

## Architecture Overview
The system relies on an in-memory orchestration model where the `MatchingEngine` serves as the entry point. Drivers continuously update their states, which dynamically influences the `PricingEngine`'s calculation of supply.

### Component Details
1. **Models/Entities**: Simple data objects encapsulating their internal state locks to prevent dirty reads or race conditions.
2. **Pricing Engine**: Handles the supply-demand tracking mathematically. A ratio of requests over drivers calculates a step-based surge multiplier (`1.0`, `1.5`, `2.0`).
3. **Matching Engine**: On `requestRide()`, queries the `PricingEngine` for fare estimation, generates a trip, queries idle drivers, and assigns the trip based on atomic state allocation.

### Data Structures
- **Concurrent Hash Maps**: Used to hold mappings of driver IDs to Driver objects and trip IDs to Trip objects. In Java, `ConcurrentHashMap` is used; in Python, dictionaries protected by `RLock`.
- **List Sorting**: A simple sorting of IDLE drivers based on a Euclidean distance calculation provides the nearest drivers.

## Reference Contracts
- **Normal Use-Case:** A rider requests a ride, the engine finds the nearest IDLE driver using a spatial index (or brute-force in v1), calculates a price based on supply/demand, and atomically assigns the driver to the trip.
- **Empty/Invalid Input:** Requesting a ride with no available drivers correctly updates demand and gracefully returns without assignment, keeping the trip in a cancelled or unassigned state.
- **Duplicate Operation:** Multiple concurrent requests for the same area will compete for drivers; locks ensure a driver is assigned to exactly one trip.
- **Capacity Boundary:** The system scales to limits by failing safely when drivers run out, utilizing dynamic surge pricing boundaries.
- **Failure Rollback:** If a driver is marked ASSIGNED but the trip assignment fails for any reason, the driver's state is rolled back to IDLE to prevent ghost drivers.

## Version-Specific Feature Deltas & Public APIs
- **v1-basic:** Simple brute force spatial search and coarse-grained driver lists. Public APIs include `registerDriver(driver)`, `requestRide(rider, destination)`, and `updateDriverState(driverId, newState)`.
- **v2-extended:** Introduces `PricingEngine` for surge multiplier based on supply/demand using global counters. Public API expands to include `PricingEngine.updateSupplyDemand` and `PricingEngine.estimatePrice`.
- **v3-optimized:** Implements `SpatialIndex` with Geohashing and fine-grained `ReentrantLock`/`RLock` for atomic state transitions, reducing spatial search to O(1) grid buckets.
