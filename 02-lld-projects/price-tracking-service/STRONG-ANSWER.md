# Strong Answer: Price Tracking Service

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Price Tracking Service, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

## 2. Entity Modeling (10 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."
The main entities are `Product`, `PriceHistory`, `User`, `AlertRule`, and `Notification`. The `AlertRule` links a user's threshold to a specific product.

## 3. Data Structure Rationale (10 mins)
**Say:** "Choosing the right data structures is critical for meeting our latency and throughput requirements."
A Time Series data structure (or a Deque per product) stores historical prices. A Segment Tree enables lightning-fast querying of minimum and maximum prices over specific time intervals.

## 4. Design Pattern Justifications (5 mins)
**Say:** "To keep the system modular and maintainable, I've applied specific design patterns."
The **Observer Pattern** is heavily used to instantly notify users when a product's price drops below their custom `AlertRule` threshold. A **Singleton** coordinates the background scraping and ingestion engine.

## 5. Concurrency Defense & Thread-Safety Details (10 mins)
**Say:** "Given that this system will be accessed by multiple threads concurrently, ensuring thread safety without creating bottlenecks is a priority."
Price updates and user reads happen concurrently at high velocity. We use a `ConcurrentHashMap` for live prices. For the historical log, a `CopyOnWriteArrayList` is effective since price updates are infrequent compared to read queries, providing lock-free read access.

## 6. Failure Handling (3 mins)
**Say:** "Systems fail, so we need to anticipate and handle failures gracefully at the lowest level."
If scraping a price fails, the system retains the last known price and flags it visually as stale. If the downstream notification service experiences downtime, alerts are safely queued in a durable Dead Letter Queue (DLQ) for later delivery.

## 7. Production Trade-offs (2 mins)
**Say:** "In a real production environment, this in-memory or single-node design would require certain trade-offs and adaptations."
Storing fine-grained price history for millions of items requires massive memory. We trade off precision for space by aggressively downsampling older data (e.g., rolling up minute-by-minute data into daily averages after one week) to control the memory footprint.

## 8. Domain Contracts & Edge Cases (5 mins)
**Say:** "To guarantee correctness, the domain contracts explicitly define that exact price-unit histories maintain configured retention and trigger one alert per threshold crossing, not every poll."
Furthermore, edge cases like repeated merchant events, out-of-order timestamps, missing product, failed polling, and unsubscribe are tested with injected transports/clock to ensure deterministic simulation of edge conditions without flakiness.
