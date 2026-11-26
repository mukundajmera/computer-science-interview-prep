# Ride Sharing System — Follow-Up Questions

Common follow-up variants an interviewer may ask after the core Ride Sharing System design, along with brief approach outlines for each.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md)

---

## 1. "How would you implement surge pricing?"

### Why They Ask

Tests whether your fare calculation is extensible and whether you understand demand-supply economics. Surge pricing touches the pricing strategy, the geographic zone model, and the request flow — revealing how well your design separates concerns. Candidates who hard-coded the fare formula will struggle here.

### Approach

- **Zone-based demand tracking:** Divide the service area into geographic zones (grid cells or geohash regions). Track the number of active ride requests (demand) and available drivers (supply) per zone in real time.
- **Multiplier calculation:** Compute a surge multiplier per zone: `multiplier = demand / supply`. Apply thresholds — e.g., multiplier kicks in only when the ratio exceeds 1.5, and cap it at 3.0× to prevent extreme pricing.
- **Strategy pattern integration:** Create a `SurgePricingStrategy` that wraps the base `PricingStrategy`. It fetches the current multiplier for the rider's pickup zone and applies it to the base fare: `surgeFare = baseFare × multiplier`. The `FareCalculator` composes strategies, so surge pricing is layered on without modifying the base formula.
- **Rider notification:** Before confirming the request, show the rider the surge multiplier and estimated fare. The rider must explicitly accept the surge price, adding a confirmation step in the request flow.

**Key trade-off:** Aggressive surge pricing maximizes driver supply response (drivers move toward high-surge zones) but risks rider churn. A gentler multiplier curve retains riders but may not attract enough drivers. Production systems tune the curve per market and time of day.

---

## 2. "How would you handle ride cancellation with penalties?"

### Why They Ask

Tests whether your trip state machine supports reverse transitions and whether you can model business rules (cancellation windows, penalty fees) cleanly. Also probes whether cancellation logic is isolated from the core trip flow or tangled into it.

### Approach

- **State transition:** Add CANCELLED as a reachable state from REQUESTED and MATCHED. From IN_PROGRESS, cancellation is not allowed (the rider must complete the trip or the driver ends it). The `Trip.cancel()` method validates the current state before transitioning.
- **Cancellation window:** Define a grace period (e.g., 2 minutes after matching). Cancellations within the window are free; cancellations after the window incur a penalty fee. The window duration is configurable per vehicle type or city.
- **Penalty fee calculator:** Create a `CancellationPenaltyCalculator` that computes the fee based on time elapsed since matching, vehicle type, and whether the driver has already started moving toward the pickup. Return a `CancellationResult` object with the fee amount and reason.
- **Driver release:** On cancellation, release the assigned driver back to the available pool immediately. Update the driver's status to AVAILABLE so they can be matched to the next request without delay.
- **Rider history tracking:** Record cancellation frequency per rider. Riders with excessive cancellations (e.g., more than 3 in a week) receive warnings or temporary suspension from requesting rides.

**Key trade-off:** Strict penalties discourage frivolous cancellations but frustrate riders who cancel for legitimate reasons (e.g., driver taking too long). A tiered approach — free within grace period, small fee after, larger fee if driver is en route — balances both sides.

---

## 3. "How would you support ride-sharing / carpooling?"

### Why They Ask

Tests whether your Trip model can accommodate multiple riders and whether your matching algorithm can evaluate route compatibility. Carpooling introduces a fundamentally different matching problem — not just nearest driver, but best route overlap — and reveals how flexible your class design really is.

### Approach

- **Shared trip entity:** Extend the `Trip` model to support multiple riders. A `SharedTrip` holds a list of `RideSegment` objects, each representing one rider's pickup-to-dropoff leg. The trip's overall route is the optimized combination of all segments.
- **Route overlap matching:** When a new rider requests a shared ride, evaluate existing in-progress shared trips for route compatibility. Compute the detour ratio: `detour = (newRouteDistance - originalRouteDistance) / originalRouteDistance`. Accept the match only if the detour is below a threshold (e.g., 25%).
- **Split fare calculation:** Each rider pays a fraction of the total fare proportional to their segment distance relative to the total trip distance. Create a `SplitFareCalculator` that computes per-rider fare breakdowns. All riders benefit from a discount compared to a solo trip.
- **Capacity management:** Track available seats in the vehicle. A CAR may have 3 shareable seats; an AUTO may have 1. The matcher only considers trips with remaining capacity.
- **Pickup/dropoff ordering:** Optimize the stop sequence to minimize total trip time. The driver's navigation updates dynamically as riders are added or dropped off.

**Key trade-off:** Aggressive matching (high detour threshold) increases ride-sharing utilization but degrades individual rider experience with longer trips. Conservative matching preserves trip quality but reduces sharing opportunities. Production systems let riders set their own detour tolerance.

---

## 4. "How would you make driver matching thread-safe?"

### Why They Ask

Tests your understanding of concurrency in a high-throughput system. With thousands of ride requests per minute, the matching service is a concurrency hotspot — multiple threads selecting from the same pool of available drivers. This question separates candidates who understand thread-safety from those who only design single-threaded systems.

### Approach

- **Per-driver locking:** Use a fine-grained lock on each `Driver` object (or the driver's availability flag). When the matcher selects a driver, it acquires the lock, checks availability, marks the driver as ASSIGNED, and releases the lock. Two matchers cannot simultaneously assign the same driver.
- **Optimistic concurrency with CAS:** Replace the boolean `isAvailable` with an `AtomicBoolean` or versioned status field. The matcher reads the current status, attempts a compare-and-swap from AVAILABLE to ASSIGNED. If the CAS fails (another thread already assigned the driver), the matcher moves to the next candidate in the ranked list.
- **Batch-and-lock approach:** Collect pending ride requests into a batch, acquire a short-lived global lock on the driver pool, run the matching algorithm for the entire batch (optimal assignment), release the lock, and dispatch all assignments. This reduces lock contention by amortizing the cost across multiple requests.
- **Thread-safe data structures:** Store available drivers in a `ConcurrentHashMap<Zone, ConcurrentSkipListSet<Driver>>` partitioned by geographic zone. Each zone's set is independently lockable, so matching in Zone A doesn't block matching in Zone B.

**Key trade-off:** Per-driver CAS is the most scalable approach (no global contention) but may require multiple retries under heavy load. The batch-and-lock approach guarantees globally optimal matching but introduces latency from batching. Production systems often combine both — CAS for real-time matching with periodic batch re-optimization.

---

## 5. "How would you add real-time ETA calculation?"

### Why They Ask

Tests whether your Location model supports more than simple straight-line distance, and whether you can integrate a dynamic calculation into the trip lifecycle. ETA is a core user-facing feature that touches location tracking, route estimation, and periodic updates — revealing how well your system handles real-time data.

### Approach

- **Route distance estimation:** Replace straight-line (Haversine) distance with road-network distance using a routing engine (or an approximation factor: `roadDistance ≈ haversineDistance × 1.4`). Store the estimated route distance and duration on the `Trip` when it is created.
- **Traffic factor:** Multiply the base ETA by a traffic factor derived from the time of day and zone congestion data. Define a `TrafficFactorProvider` that returns a multiplier (e.g., 1.0 for off-peak, 1.5 for rush hour, 2.0 for heavy congestion).
- **Periodic recalculation:** Once the trip is IN_PROGRESS, recalculate ETA at regular intervals (e.g., every 30 seconds) based on the driver's current location and remaining route distance. Push the updated ETA to the rider via the Observer pattern.
- **Phases:** ETA has two distinct phases: (1) pickup ETA — time for the driver to reach the rider, calculated from match to pickup; (2) trip ETA — time from pickup to destination, calculated from trip start. Both are tracked and displayed separately.
- **Implementation:** Add an `ETACalculator` service that accepts current location, destination, and traffic factor, and returns an `ETAEstimate` with distance remaining, estimated minutes, and confidence level.

**Key trade-off:** Frequent recalculation provides accurate ETAs but increases computational cost and network traffic from location updates. Infrequent recalculation is efficient but shows stale data. A hybrid approach recalculates on significant events (driver completes a turn, enters a new road segment) and interpolates between updates.

---

## 6. "How would you implement a driver incentive system?"

### Why They Ask

Tests whether your design can accommodate business logic that sits outside the core trip flow. Incentives depend on driver behavior over time (completion rate, peak-hour activity, ratings) and reveal whether your Driver model captures enough state to support analytics-driven features.

### Approach

- **Bonus calculator:** Create a `BonusCalculator` that evaluates a driver's activity over a time window (daily, weekly). Bonuses are triggered by rules: complete 10 trips in a day → ₹500 bonus; maintain a 4.5+ rating for a week → ₹1000 bonus; complete 5 trips during peak hours → ₹300 bonus.
- **Peak-hour multipliers:** Define peak-hour windows per city (e.g., 8–10 AM, 6–9 PM). Trips completed during peak hours earn a higher per-trip payout for the driver. The multiplier is separate from surge pricing — surge affects rider fare, incentive multiplier affects driver payout.
- **Completion-rate tracking:** Track the ratio of completed trips to total assigned trips per driver. Drivers below a threshold (e.g., 85% completion rate) are deprioritized in matching. Drivers above a high threshold (e.g., 95%) receive bonus incentives. Store this as a rolling metric on the `Driver` entity.
- **Incentive tiers:** Define tier levels (Bronze, Silver, Gold, Platinum) based on cumulative trip count and rating. Higher tiers unlock benefits: priority matching, lower commission rates, and access to premium ride requests. The `Driver` entity holds the current tier, and the `DriverMatcher` can factor tier into matching priority.
- **Implementation:** Add a `DriverIncentiveService` that runs periodically (end of day/week), evaluates all active drivers against the rule set, computes bonuses, and records them. Rules are defined as `IncentiveRule` objects with a condition and reward, making the system extensible without code changes.

**Key trade-off:** Generous incentives attract and retain drivers but reduce platform margins. Strict incentive criteria maintain profitability but may cause driver churn in competitive markets. Production systems run A/B tests on incentive structures per city and dynamically adjust based on driver supply metrics.

---

## Quick Reference

| # | Follow-Up | Core Challenge | Key Concept |
|---|-----------|---------------|-------------|
| 1 | Surge pricing | Demand/supply-driven dynamic pricing | PricingStrategy composition, zone-based multipliers |
| 2 | Ride cancellation | Reverse state transitions with business rules | Cancellation window, penalty calculator, driver release |
| 3 | Ride-sharing / carpooling | Multi-rider trips with route compatibility | SharedTrip model, detour ratio, split fare |
| 4 | Thread-safe matching | Concurrent access to driver pool | Per-driver CAS, zone-partitioned locks, batch matching |
| 5 | Real-time ETA | Dynamic route and traffic estimation | ETACalculator, traffic factor, periodic recalculation |
| 6 | Driver incentives | Behavior-based rewards outside core trip flow | BonusCalculator, completion-rate tracking, incentive tiers |

---

*See [APPROACH](./APPROACH.md) for how to structure the base design, and [PITFALLS](./PITFALLS.md) for mistakes to avoid when handling these extensions.*
