# Ticketing Platform — Model Answer (Time-Boxed)

Say: "I will make seat holds and payment finalization the correctness boundary: reads can be cached, but a seat cannot be sold twice."

## 0-5 min: Requirements

- Scope to browse/search + seat hold + booking.
- Confirm strict no-double-book requirement.
- Lock out-of-scope areas (fraud internals, promoter tooling).

## 5-10 min: Estimates

- Peak onsale seat actions/sec.
- Typical event/seat counts.
- Read vs write split outside/inside onsale windows.

## 10-15 min: API + State Model

- `GET /events`, `GET /events/{id}/seats`, `POST /holds`, `POST /bookings`.
- Seat transitions: `AVAILABLE -> HELD -> BOOKED`.

## 15-30 min: Architecture

- Gateway + admission queue.
- Search/Event path separated from hold/booking path.
- Hold store with TTL and ownership.
- Booking orchestrator with payment idempotency.

## 30-40 min: Deep Dives

1. Onsale throttling and fairness.
2. Hold expiration and stale hold cleanup.
3. Partial failure reconciliation (payment vs booking).

## 40-45 min: Trade-Off Wrap

- Why strict consistency only on seat commit path.
- Why queueing beats open flood during spikes.
- Next step: resale and transfer lifecycle support.
