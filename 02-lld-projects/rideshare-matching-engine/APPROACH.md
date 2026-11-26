# Rideshare Matching Engine - Approach

## Core Entities
1. **Driver**: Represents a driver. Contains thread-safe driver state (`DriverState`) and current `Location`.
2. **Rider**: Represents the rider requesting a trip.
3. **Trip**: Represents a ride request, including origin, destination, assigned driver, price, and state.
4. **Location**: Represents latitude and longitude.
5. **PricingEngine**: Responsible for maintaining supply and demand metrics, and evaluating surge multipliers and trip price estimates.
6. **MatchingEngine**: Acts as the main orchestrator, holding all active drivers and trips. Dispatches trips by finding nearest drivers and attempting atomic state transitions.

## Concurrency Strategy
1. **Thread-Safe State Transitions**: Utilizing `ReentrantLock` in Java and `threading.RLock()` in Python to handle state changes within Driver, Trip, PricingEngine, and MatchingEngine.
2. **Atomic Allocation**: When a trip request is processed, the system fetches a list of nearest drivers. It iterates over this list, attempting to atomically transition the driver's state from `IDLE` to `ACCEPTED`. If successful, the driver is attached to the trip. If not, it falls through to the next nearest driver.
3. **Supply/Demand Synchronization**: Updates to `availableDrivers` and `activeRequests` must be thread-safe as multiple concurrent requests and driver state changes alter these variables simultaneously.

## Spatial Search Strategy
Since we only have to build an in-memory application without external DB constraints, we can calculate distances sequentially. If the system was larger, a quad-tree or GeoHash index would be used. For this project, filtering drivers by IDLE state and sorting by Euclidean distance is sufficient.
