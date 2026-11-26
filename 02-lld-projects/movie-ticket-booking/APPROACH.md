# Design Approach for Movie Ticket Booking

## Approach overview
Use a state-oriented domain model where `Show` owns seat state and `BookingSystem` owns API orchestration. Keep correctness rules explicit before adding scale optimizations.

## Step 1: Clarify contracts first
1. Define booking lifecycle states and legal transitions.
2. Define lock ownership rules (`userId`, TTL, release semantics).
3. Freeze method signatures early to avoid test/client drift.

## Step 2: Model seat state around correctness
- Keep `ShowSeat` as the unit of contention.
- Enforce atomic lock-all-or-fail for multi-seat booking requests.
- Ensure confirm/cancel paths validate booking ownership and current state.

## Step 3: Isolate concurrency boundary
- Route lock, confirm, and cancel through synchronized/locked critical sections in `v3-optimized`.
- Keep reads cheap, but never perform check-then-act without a guard.
- Prefer explicit helper abstractions for lock coordination and expiry cleanup.

## Step 4: Keep payment integration interview-sized
- Treat payment as input that triggers booking transition.
- Avoid gateway complexity unless interviewer explicitly asks.
- Preserve retry-safe behavior with idempotent confirm calls.

## Step 5: Progressive versions
- `v1-basic`: simple entities + happy-path booking.
- `v2-extended`: richer search/pricing/booking metadata.
- `v3-optimized`: thread safety, lifecycle APIs, compatibility wrappers.

## Requirements and constraints checklist
- Seat double-book prevention under concurrent attempts.
- Lock TTL expiry without corrupting confirmed state.
- Backward-compatible API wrappers for previous demos/tests.
- Java/Python parity for core behaviors.

## Scoring rubric
See [RUBRIC.md](./RUBRIC.md).

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Variants and extensions
1. Add reservation priority tiers (VIP/member) with fairness rules.
2. Add partial fulfillment policy (book subset vs fail-all).
3. Add event sourcing for booking/audit replay.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
- [Job Scheduler follow-ups](../job-scheduler/FOLLOW-UPS.md)
