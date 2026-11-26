# Rideshare Matching Engine - Follow-Up Questions

## Cross-links
* [Problem Statement](PROBLEM.md)
* [Design Document](DESIGN.md)

## Follow-up questions

1. **How would you scale this matching engine across multiple servers?**
   * Expected Answer: The in-memory data structures must be migrated to a distributed database (e.g., Redis for active states, PostGIS/ElasticSearch for spatial queries). A pub/sub system like Kafka would act as the transaction ledger for state transitions.

2. **How do you handle driver location updates efficiently at scale?**
   * Expected Answer: Location updates are extremely noisy. Instead of processing every ping, implement client-side batching or rate limiting. On the backend, use a memory-optimized spatial index (QuadTree, Geohash, S2) such as Redis geospatial indices instead of simple lists.

3. **What happens if a driver disconnects while in the `ACCEPTED` state?**
   * Expected Answer: Implement a heartbeat or TTL mechanism. If a driver misses X heartbeats, a background worker transitions their state to `IDLE` or `OFFLINE`, and the assigned `Trip` is rolled back and re-queued in the matching engine for another driver.

## Variants and extensions

* **Shared Rides (Carpooling)**: Extend the system to allow a single `Driver` to have multiple `Trip`s concurrently, where the route is dynamically re-optimized using a VRP (Vehicle Routing Problem) algorithm to pick up/drop off multiple riders without violating constraints like maximum seats or delay bounds.
* **Scheduled Rides**: Add a temporal component where trips are placed in a deferred queue and only enter the matching pool a set time before their start requirement.

## Interviewer probes to prepare

* "Show me exactly where you ensure that two riders requesting a ride at the same millisecond don't get assigned the same driver."
* "Your distance calculation is $O(N)$ against all idle drivers. Can you explain the time complexity if we have 100,000 drivers online?"
