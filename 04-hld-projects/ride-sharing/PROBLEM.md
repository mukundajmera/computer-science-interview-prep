# Ride Sharing Backend System

## Problem Statement

Design a ride-sharing backend that estimates fares, matches riders to nearby drivers, and tracks trip lifecycle updates in real time while preventing duplicate driver assignment.

---

## Requirements and Constraints

### Functional Requirements

1. Riders can request fare estimate for pickup/dropoff.
2. Riders can request rides from the estimate flow.
3. System matches riders with nearby available drivers.
4. Drivers can accept/decline and progress trip states.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Match latency | < 60 seconds |
| Location update latency | < 1 second ingestion |
| Consistency (assignment) | Strong |
| Availability | 99.99% |
| Peak hotspot handling | 100K+ local request bursts |

### Capacity Assumptions

- 50M riders, 5M drivers.
- 1M concurrent rides.
- 10M+ location updates/minute.

### Out of Scope

- Payments internals.
- Driver onboarding and compliance checks.
- Carpool routing optimization.

---

## High-Level Design Outline

### Core Services

- API Gateway
- Ride Service
- Matching Service
- Location Tracking Service
- ETA Service
- Surge Service

### API Surface (Illustrative)

```http
POST /api/v1/fare-estimates
POST /api/v1/rides
POST /api/v1/rides/{rideId}/accept
POST /api/v1/drivers/location
GET /api/v1/rides/{rideId}
```

---

## Scoring Rubric (Quick Signals)

1. Correct assignment consistency model.
2. Explicit driver availability and ride state machine.
3. Geo-indexed matching at scale.
4. Clear fallback behavior during overload.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Nearest-driver-only matching without dispatch flow.
- No separation between location ingestion and ride commands.
- Weak lifecycle validation causing illegal transitions.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How do we handle border-zone and multi-city matching?
- How do we support pooled rides?
- How do we reduce ETA error during high traffic?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Scheduled rides.
- Multi-vehicle categories.
- Safety/fraud event detection.

---

## Related Links

- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/real-time-updates](../../03-hld-concepts/real-time-updates/)
- [03-hld-concepts/contention-control](../../03-hld-concepts/contention-control/)
- [04-hld-projects/quick-commerce-delivery](../quick-commerce-delivery/)
