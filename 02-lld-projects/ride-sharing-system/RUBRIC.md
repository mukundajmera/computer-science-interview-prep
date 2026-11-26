# Ride Sharing System — Interview Scoring Rubric

A structured rubric for evaluating Ride Sharing System low-level design interviews across 5 dimensions, each scored from 1 (Poor) to 5 (Strong).

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|-----------|--------|------------|
| 1 | Requirements Gathering | 15% | Vehicle types, matching criteria, fare structure, surge pricing, rating system |
| 2 | Class Design & Entity Modeling | 25% | Trip state machine, separation of Rider/Driver/Trip, Location model, proper use of enums for states and vehicle types |
| 3 | Design Pattern Usage | 20% | Strategy (matching algorithms), State (trip lifecycle), Observer (location tracking, ride status notifications) |
| 4 | Extensibility & Edge Cases | 25% | Concurrent driver assignment, driver rejecting request, no available drivers, surge pricing triggers, GPS coordinate handling, ride cancellation |
| 5 | Code Quality & Communication | 15% | Clean OOP, explaining matching trade-offs, state transitions |

---

## 1. Requirements Gathering

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Jumps into coding without clarifying requirements. Does not ask about vehicle types, matching criteria, or fare structure. Assumes a single vehicle type with a fixed fare and ignores rider/driver roles entirely. |
| **3 — Acceptable** | Asks about vehicle types (Car, Auto, Bike), matching approach (nearest driver), and basic fare components (base fare + per-km rate). Identifies core operations (request ride, match driver, start trip, complete trip) and mentions at least one non-functional concern such as concurrent matching or location tracking frequency. |
| **5 — Strong** | Systematically clarifies: supported vehicle types and their fare tiers, matching criteria (distance, rating, vehicle type preference), fare components (base fare, distance rate, time rate, surge multiplier), surge pricing triggers (demand/supply ratio per zone), rating system (mutual rider-driver ratings), and cancellation policies. Separates functional requirements (ride request, driver matching, trip lifecycle, fare calculation, ratings) from non-functional requirements (thread-safe matching, location update frequency, matching timeout, GPS precision). Explicitly scopes out features like ride-sharing/carpooling, scheduled rides, and multi-stop trips as future extensions. |

---

## 2. Class Design & Entity Modeling

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Puts all logic in a single `RideService` class with primitive fields. No separate classes for Rider, Driver, Trip, Location, or FareCalculator. Trip state is tracked with boolean flags (`isStarted`, `isCompleted`) instead of a proper state machine. Driver and rider logic are intermingled in a single `User` class with a role string. |
| **3 — Acceptable** | Identifies core entities: `RideService`, `Rider`, `Driver`, `Trip`, `Location`, `RideRequest`. Uses an enum for `TripStatus` (REQUESTED, MATCHED, IN_PROGRESS, COMPLETED, CANCELLED) and `VehicleType` (CAR, AUTO, BIKE). Establishes basic relationships (rider requests trips, driver is matched to trips). Requests capture pickup location, drop-off location, and vehicle type preference. Some encapsulation with private fields and getters. |
| **5 — Strong** | Presents a complete class hierarchy: `RideService` as the façade; `Trip` with a full state machine (REQUESTED → MATCHED → IN_PROGRESS → COMPLETED, with CANCELLED reachable from REQUESTED and MATCHED); `Rider` and `Driver` as distinct entities with role-specific behavior (driver has current location, availability status, vehicle type, and rating; rider has payment method and ride history); `RideRequest` as a value object capturing pickup, drop-off, vehicle preference, and timestamp; `DriverMatcher` decoupled from `Trip` with a strategy interface; `FareCalculator` separated from trip logic with pluggable pricing strategies; `Location` as a proper model with latitude, longitude, and distance calculation. Uses composition over inheritance where appropriate (e.g., Driver has a Vehicle, Trip has a FareBreakdown). Demonstrates clear encapsulation, single responsibility, and clean interfaces between entities. |

---

## 3. Design Pattern Usage

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No identifiable design patterns. Matching logic is hard-coded with inline distance calculations and nested `if/else` blocks. Trip state is managed with boolean flags rather than a state machine. Fare calculation is embedded directly in the trip completion method with magic numbers. |
| **3 — Acceptable** | Uses at least two patterns appropriately: Strategy for driver matching algorithm selection and either State for trip lifecycle transitions or Observer for ride status notifications. Can name the patterns used and explain why they apply to the ride-sharing domain. |
| **5 — Strong** | Applies patterns naturally and justifies each: **Strategy** for `MatchingStrategy` (nearest-first, rating-weighted, vehicle-type-filtered algorithms swappable at runtime) and `PricingStrategy` (standard pricing, surge pricing, promotional pricing); **State** for `TripStatus` (each state encapsulates valid transitions — REQUESTED can transition to MATCHED or CANCELLED, MATCHED can transition to IN_PROGRESS or CANCELLED, IN_PROGRESS can only transition to COMPLETED); **Observer** for status notifications (rider and driver subscribe to trip state changes, location tracking pushes updates to active trips). Discusses trade-offs — e.g., why State prevents invalid transitions like completing a trip that hasn't started, why separate strategies for matching and pricing allow independent evolution. |

---

## 4. Extensibility & Edge Cases

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Designs for a single rider and single driver with no consideration for concurrent requests. Does not handle what happens when no drivers are available or when a driver rejects a request. Ignores surge pricing, cancellation, and rating entirely. No thought given to adding new vehicle types or matching strategies in the future. |
| **3 — Acceptable** | Supports multiple concurrent ride requests with a central matching service. Handles the no-available-driver case by returning an appropriate error to the rider. Mentions that concurrent driver assignment is a concern and suggests synchronization on the matching operation. Acknowledges that new matching strategies or vehicle types could be added via interfaces. |
| **5 — Strong** | Designs for extensibility from the start: new matching strategies require only a new `MatchingStrategy` implementation; new vehicle types are added to the enum without modifying existing code (Open/Closed Principle); pricing strategies are composable (base + surge + promotional). Handles edge cases thoroughly: two riders matched to the same driver simultaneously (atomic driver reservation with locking or CAS), driver rejects the request (timeout with automatic re-matching to next-best driver), no available drivers (notification to rider with retry or queue), GPS coordinate precision and distance calculation (Haversine formula or grid-based approximation), ride cancellation (state transition with cancellation window and penalty logic), surge pricing (demand/supply ratio per geographic zone with configurable multipliers). Discusses fairness — ensuring drivers are not starved of requests and riders receive consistent matching quality. |

---

## 5. Code Quality & Communication

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Code is disorganized with inconsistent naming. Cannot explain trip state transitions when asked. Writes long methods with mixed responsibilities (matching logic, fare calculation, and notification in one method). Jumps between topics without a clear narrative. |
| **3 — Acceptable** | Code follows consistent naming conventions (PascalCase classes, camelCase methods). Methods are reasonably sized with single responsibilities. Explains key decisions (e.g., "I used Strategy here because we may want different matching algorithms for different cities") when prompted. Communicates the design in a logical order: entities → trip state machine → matching → fare calculation → extensions. |
| **5 — Strong** | Code reads like production quality: meaningful names, short focused methods, clear interfaces, and Javadoc/docstrings on public APIs. Proactively explains state transitions and matching decisions at each step without being asked. Walks through the design systematically — starts with the trip state machine, builds the rider/driver model, adds the matcher, layers in fare calculation, then discusses patterns and concurrency. Uses diagrams or pseudo-code to clarify complex flows (e.g., the request-to-match-to-trip sequence). Manages time well: covers core design in the first 20 minutes, then dives into surge pricing, concurrency, and edge cases. |

---

## Quick Calibration Guide

| Total Score (out of 25) | Rating | Recommendation |
|--------------------------|--------|----------------|
| 21–25 | 🟢 Strong Hire | Exceeds expectations across all dimensions |
| 15–20 | 🟡 Hire | Solid fundamentals, minor gaps in depth |
| 9–14 | 🟠 Lean No Hire | Acceptable basics but missing key design considerations |
| 5–8 | 🔴 No Hire | Significant gaps in OOP and design thinking |

---

*Use this rubric alongside [PITFALLS](./PITFALLS.md) to identify common failure modes and [FOLLOW-UPS](./FOLLOW-UPS.md) for extension questions that probe deeper.*
