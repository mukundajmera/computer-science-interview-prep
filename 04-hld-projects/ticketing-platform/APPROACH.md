# Ticketing Platform - Approach

## 1. Clarify the Hard Boundary First

- Separate read path (event browsing/search) from write path (holds/booking).
- Confirm hold timeout and payment retry expectations.
- Lock scope to unique seat state transitions.

## 2. Estimate for Peak, Not Average

- Compute peak seat-selection burst during onsale launch.
- Size admission queue and hold service for worst 5-10 minute window.
- Keep search and event details isolated so booking spikes do not collapse discovery.

## 3. Define the Seat State Machine

`AVAILABLE -> HELD -> BOOKED` and `HELD -> AVAILABLE` on TTL expiry.

Rules:

- Exactly one active hold owner per seat.
- Booking only succeeds from `HELD` state by same hold owner.
- All state transitions are idempotent.

## 4. Architecture Strategy

- API Gateway + rate limits + queue admission token.
- Seat Hold service backed by Redis/KV TTL entries.
- Booking orchestrator commits order/payment/ticket issuance with saga steps.
- Async notifications for confirmation and fallback error handling.

## 5. Deep Dives to Lead

1. High-contention hold design (lock granularity, fairness, TTL).
2. Queueing and traffic shaping during onsales.
3. Payment/booking idempotency and recovery.

## 6. Interview Wrap-Up Pattern

- Re-state strict consistency for seat commits.
- Summarize throughput strategy (queue + cache + async).
- Call out one key trade-off and one future extension.
