# Ride Sharing System — Common Interview Pitfalls

The top 6 mistakes candidates make in a Ride Sharing System low-level design interview, why each is a problem, and what the interviewer actually expects.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. No Trip State Machine

### ❌ The Mistake

Treating a trip as a single event — calling `completeRide()` directly after `requestRide()` — instead of modeling the full lifecycle. Trip status is tracked with boolean flags like `isStarted`, `isCompleted`, and `isCancelled`, leading to invalid combinations (`isStarted = true` and `isCancelled = true` simultaneously). There is no enforcement of valid transitions, so the system allows completing a trip that was never matched to a driver, or cancelling a trip that is already in progress without proper handling.

### 🎯 What the Interviewer Expects

- Define an explicit `TripStatus` enum or State pattern: `REQUESTED`, `MATCHED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`.
- Each state knows its valid transitions — `REQUESTED` can transition to `MATCHED` or `CANCELLED`, but never directly to `COMPLETED` or `IN_PROGRESS`.
- State transitions are centralized in a single method on the `Trip` class, not scattered across multiple services.
- The State pattern encapsulates per-state behavior: `RequestedState.assignDriver()` transitions to MATCHED; `MatchedState.startTrip()` transitions to IN_PROGRESS; invalid calls throw an exception.

### 💡 Tip

Sketch the state transition diagram before writing any code. Five states and their directed edges take 30 seconds to draw and immediately demonstrate design maturity. If you catch yourself writing `if (isStarted && !isCancelled && driver != null)`, stop and refactor into states.

---

## 2. Race Condition on Driver Assignment

### ❌ The Mistake

Two riders request rides at the same time and the matching algorithm selects the same nearby driver for both. Without synchronization, both ride requests are assigned to that driver — the driver receives two trips and one rider is left without a pickup. The candidate treats driver matching as a single-threaded operation when the problem is inherently concurrent.

### 🎯 What the Interviewer Expects

- Identify the concurrency boundary: the moment a driver is selected and marked as unavailable must be atomic.
- Use a locking mechanism on the driver: `synchronized` block, `ReentrantLock`, or compare-and-swap (CAS) on the driver's availability flag.
- The matcher's assign-driver operation must be atomic — reading driver availability and assigning them to a trip should not be interleaved with another matching request.
- Discuss granularity: a global lock on the entire driver pool is simple but limits throughput; per-driver locks allow concurrent assignments to different drivers without contention.

### 💡 Tip

Even if the interviewer doesn't mention concurrency, proactively say: "Driver assignment needs to be atomic because two ride requests could select the same driver concurrently." This single sentence earns significant credit and shows you think beyond the happy path.

---

## 3. Naive Nearest-Driver Matching

### ❌ The Mistake

Finding the nearest driver by iterating through every driver in the system and computing the distance to the rider's pickup location. With 10,000 active drivers, every ride request triggers a full scan with Haversine calculations — O(n) per request. The candidate does not consider spatial indexing, grid-based partitioning, or any optimization for location-based queries.

### 🎯 What the Interviewer Expects

- Acknowledge that a linear scan is acceptable for a v1 prototype but does not scale.
- Propose a spatial optimization: grid-based partitioning (divide the city into cells, only search the rider's cell and adjacent cells), quadtree, or geohash-based indexing.
- The matching algorithm should consider more than just distance — factor in driver rating, vehicle type preference, and estimated time of arrival (which accounts for road network, not just straight-line distance).
- Implement behind a `MatchingStrategy` interface so the naive implementation can be swapped for an optimized one without modifying the rest of the system.

### 💡 Tip

When you implement the first version, say: "I'm doing a linear scan for simplicity, but in production I'd use a grid-based spatial index — partition the city into cells and only search the rider's cell plus neighbors." This takes ten seconds and demonstrates awareness of real-world scale without over-engineering the interview solution.

---

## 4. Hard-Coded Fare Formula Without Strategy

### ❌ The Mistake

Embedding the fare calculation directly in the `Trip` class with inline arithmetic: `fare = 50 + distance * 10 + time * 2`. Magic numbers with no explanation, no configuration, and no way to support different pricing models. When the interviewer asks "how would you add surge pricing?", the candidate must rewrite the fare logic inside the Trip class, violating the Open/Closed Principle.

### 🎯 What the Interviewer Expects

- Extract fare calculation into a separate `FareCalculator` with a `PricingStrategy` interface.
- The base strategy computes fare from components: base fare + (distance × per-km rate) + (time × per-minute rate), with rates varying by `VehicleType`.
- A `SurgePricingStrategy` wraps the base strategy with a multiplier derived from demand/supply ratio in the rider's zone.
- Strategies are composable — surge, promotional discounts, and vehicle-type adjustments can be layered without modifying the core formula.
- Fare breakdowns (base, distance charge, time charge, surge multiplier, total) are returned as a structured `FareBreakdown` object, not a raw number.

### 💡 Tip

When you first calculate the fare, immediately say: "I'm putting this behind a strategy interface so we can swap in surge pricing or promotional rates." Then implement the standard formula as the default. This demonstrates the Open/Closed Principle in action — which is exactly what the interviewer is evaluating.

---

## 5. Missing Driver Rejection / Timeout Flow

### ❌ The Mistake

Assuming the matched driver always accepts the ride. The system transitions directly from REQUESTED to IN_PROGRESS the moment a driver is selected, with no confirmation step. In reality, drivers may reject requests (too far, unfavorable route) or simply not respond within the timeout window. The candidate's design has no mechanism to handle rejection, timeout, or re-matching — leaving the rider stuck in a matched state indefinitely.

### 🎯 What the Interviewer Expects

- Model an explicit driver confirmation step: after matching, the trip enters MATCHED state and the driver has a configurable timeout (e.g., 30 seconds) to accept or reject.
- On acceptance, the trip transitions to IN_PROGRESS. On rejection or timeout, the driver is excluded from the candidate pool and the matcher re-runs to find the next-best driver.
- Track a rejection count per request — after N rejections (e.g., 3), notify the rider that no driver is available and transition to CANCELLED.
- The re-matching loop must release the rejected driver back to the available pool (for other riders) and avoid selecting the same driver again for this request.

### 💡 Tip

Mention the driver acceptance flow when you first describe the matching process. Say: "After matching, the driver has 30 seconds to accept. On timeout, I re-match with the next-best driver." This shows you understand real-world ride-sharing flows and distinguishes you from candidates who model a toy system.

---

## 6. No Separation Between Rider and Driver Interfaces

### ❌ The Mistake

Creating a single `User` class with a `role` field (`"rider"` or `"driver"`) and cramming all behavior into it. The `User` class ends up with methods like `requestRide()`, `acceptRide()`, `updateLocation()`, `setAvailability()`, and `rateTrip()` — half of which are irrelevant depending on the role. Conditional logic checks the role before every operation: `if (role.equals("driver"))`. Adding a new role (e.g., fleet manager) requires modifying the monolithic `User` class.

### 🎯 What the Interviewer Expects

- Define separate `Rider` and `Driver` classes, each with role-specific behavior and state.
- `Rider` has: ride history, payment method, `requestRide()`, `rateDriver()`, and `cancelRide()`.
- `Driver` has: current location, availability status, vehicle type, rating, `acceptRide()`, `rejectRide()`, `startTrip()`, and `completeTrip()`.
- Shared properties (name, phone, email) can live in a common `User` base class or be composed via a `UserProfile` value object — but the role-specific interfaces must be distinct.
- This separation makes it easy to add constraints (e.g., driver must have a verified license) without polluting the rider's interface.

### 💡 Tip

When you start defining entities, draw `Rider` and `Driver` as separate boxes immediately. If the interviewer sees a single `User` class with a role string, they will push back — and refactoring mid-interview is costly. Start with clean separation and you avoid the entire conversation.

---

## Summary Table

| # | Pitfall | What's Missing | Scoring Impact |
|---|---------|---------------|----------------|
| 1 | No trip state machine | State pattern, valid transitions, centralized state logic | Class Design: -3 to -4 points |
| 2 | Race condition on driver assignment | Atomic matching, per-driver locking, CAS operations | Extensibility: -2 to -3 points |
| 3 | Naive nearest-driver matching | Spatial indexing, grid-based partitioning, scalable lookup | Extensibility: -2 to -3 points |
| 4 | Hard-coded fare formula | PricingStrategy interface, composable pricing, fare breakdown | Design Patterns: -2 to -3 points |
| 5 | Missing driver rejection/timeout | Confirmation step, re-matching loop, rejection count limit | Extensibility: -2 to -3 points |
| 6 | No rider/driver separation | Distinct role classes, role-specific interfaces, clean OOP | Class Design: -2 to -3 points |

---

*See [RUBRIC](./RUBRIC.md) for full scoring criteria and [FOLLOW-UPS](./FOLLOW-UPS.md) for extension questions that probe these areas deeper.*
