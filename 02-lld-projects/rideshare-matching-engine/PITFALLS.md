# Rideshare Matching Engine - Common Pitfalls

## Cross-links
* [Problem Statement](PROBLEM.md)
* [Design Document](DESIGN.md)

### Global Lock Contention
- **Signal**: Performance degrades significantly as concurrent ride requests increase. The entire matching engine is locked during driver search.
- **Root Cause**: Over-using `synchronized` on global methods or locking the parent `MatchingEngine` class while searching and assigning.
- **Mitigation**: Use fine-grained locking. Lock the global collection only to snapshot available drivers, then lock individual `Driver` objects during assignment evaluation.
- **Validation**: Load tests using multithreading will show high wait times vs quick rejections/matches under fine-grained locking.

### Division by Zero in Surge Pricing
- **Signal**: Application crashes or returns `NaN`/Infinity when calculating price with 0 available drivers.
- **Root Cause**: Failing to account for `availableDrivers == 0` when generating a ratio (`activeRequests / availableDrivers`).
- **Mitigation**: Add an explicit check and hardcoded return (e.g., multiplier of `2.0` if requests > 0, else `1.0`) when drivers = 0.
- **Validation**: Ensure unit tests cover cases where demand spikes while supply is completely zeroed out.

### Deadlocks During State Update
- **Signal**: Threads hang indefinitely during driver allocation.
- **Root Cause**: Two threads attempt to update a Trip and a Driver object simultaneously but acquire their locks in opposite orders.
- **Mitigation**: Maintain strict lock ordering, or decouple state updates so they never hold multiple nested locks across distinct resources.
- **Validation**: Use `RLock` in Python or `ReentrantLock` in Java, and strictly test concurrent assignments to flush out circular wait conditions.
