# Ticketing Platform System

## Problem Statement

Design a high-scale ticketing platform for live events where users can discover events, inspect seat availability, temporarily hold seats, and complete payment without double booking.

---

## Requirements and Constraints

### Functional Requirements

1. Users can browse and search events by city, date range, and category.
2. Users can view venue seat maps with near-real-time availability.
3. Users can place temporary holds on one or more seats.
4. Users can confirm booking and receive digital tickets.
5. Users can view booking status and booking history.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability (browse/search) | 99.99% |
| Availability (booking path) | 99.95% |
| Search latency | < 500 ms P99 |
| Seat-hold latency | < 250 ms P99 |
| Hold timeout | 2-5 minutes |
| Consistency | Strong for seat state transitions |

### Capacity Assumptions

- 30M DAU during normal periods.
- Peak onsale surge at 100K+ seat actions/sec.
- 250K events/month, each event with 1K-80K seats.
- Read-heavy outside onsale windows; extreme contention during onsale.

### Out of Scope

- Fraud/risk modeling internals.
- Complex tax and regulatory billing flows.
- Promoter back-office workflows.

---

## High-Level Design Outline

### Core Services

- API Gateway and Admission Queue Service
- Event Catalog Service and Search Service
- Seat Inventory Service
- Seat Hold Service (distributed lock + TTL)
- Booking and Payment Orchestrator
- Ticket Issuance Service
- Notification Service

### Data Stores

- Relational DB for orders/bookings/payments.
- KV/Redis for hot seat state and short-lived holds.
- Search index for event discovery.
- Object store for ticket artifacts (QR/PDF assets).

### API Surface (Illustrative)

```http
GET /api/v1/events?city=...&start=...&end=...&page=...
GET /api/v1/events/{eventId}/seats?section=...
POST /api/v1/holds
POST /api/v1/bookings
GET /api/v1/bookings/{bookingId}
```

---

## Scoring Rubric (Quick Signals)

1. Requirement scoping and explicit contention assumptions.
2. Correct seat state machine and consistency boundaries.
3. Strong hold + booking idempotency approach.
4. Queue/admission strategy for onsale spikes.
5. Clear trade-offs between UX speed and booking safety.

See [RUBRIC](./RUBRIC.md) for detailed scoring.

---

## Common Pitfalls

- Treating seats as fungible stock instead of unique inventory.
- Using long DB transactions for hold lifecycles.
- Missing idempotency for booking and payment retries.
- No degraded strategy during onsale traffic spikes.

See [PITFALLS](./PITFALLS.md) for full breakdown.

---

## Follow-Up Questions

- How do you handle bot traffic during major onsales?
- How do you support resale while preventing ticket duplication?
- What changes for global multi-region launches?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- General admission events (no seat map).
- Dynamic pricing by demand segment.
- Waitlist + automatic seat reallocation.

---

## Related Links

- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/rate-limiting](../../03-hld-concepts/rate-limiting/)
- [03-hld-concepts/caching](../../03-hld-concepts/caching/)
- [03-hld-concepts/message-queues](../../03-hld-concepts/message-queues/)
- [02-lld-projects/movie-ticket-booking](../../02-lld-projects/movie-ticket-booking/)
- [04-hld-projects/ecommerce-backend](../ecommerce-backend/)
