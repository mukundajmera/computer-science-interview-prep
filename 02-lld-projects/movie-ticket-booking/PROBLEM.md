# Movie Ticket Booking System

## Problem statement
Design an interview-grade movie ticket booking system that supports seat discovery, temporary seat locks, booking confirmation, and cancellation under concurrent user traffic.

## Requirements and constraints

### Functional requirements
1. Browse movies, shows, and seat maps.
2. Lock selected seats for a short TTL before payment completes.
3. Create bookings only if all requested seats are currently lockable.
4. Confirm booking after successful payment and release locks on failure/timeout.
5. Cancel bookings with ownership checks and seat release.
6. Expose booking/search APIs that remain backward-compatible across versions.

### Non-functional requirements
- Correctness under contention: one seat can be confirmed by only one booking.
- Low-latency seat checks and lock attempts for hot shows.
- Deterministic behavior in local tests (no external infra required).
- Thread-safe mutation paths in `v3-optimized`.

### Constraints and assumptions
- In-memory implementation for interview scope.
- Lock duration is configurable (default 10 minutes in examples).
- Payment is modeled as a state transition, not a full gateway integration.
- A show owns its seat state; no cross-show seat coupling.

## Core entities
| Entity | Responsibility |
|---|---|
| `Movie` | Metadata used for search and listing |
| `Show` | Time-bound screening with seat inventory |
| `ShowSeat` | Seat status for a specific show (`AVAILABLE`, `LOCKED`, `BOOKED`) |
| `Booking` | Reservation intent, lifecycle, and ownership |
| `Payment` | Confirmation/cancellation trigger input |
| `BookingSystem` | API surface and concurrency boundary |

## Booking lifecycle
1. User selects a show and seat IDs.
2. System tries atomic lock acquisition for all requested seats.
3. If lock succeeds, system creates `PENDING` booking.
4. On payment success, seats transition to `BOOKED` and booking becomes `CONFIRMED`.
5. On timeout/failure/cancel, seats are released and booking becomes terminal.

## Concurrency expectations
- Concurrent requests for overlapping seats produce a single winner per seat.
- Lock expiry cleanup cannot release seats already confirmed by another transition.
- Read-modify-write paths are guarded to avoid stale reads and double booking.

## Scoring rubric
See [RUBRIC.md](./RUBRIC.md).

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Variants and extensions
1. Dynamic pricing by seat class, demand band, or show time.
2. Waitlist queues for sold-out shows with auto-retry lock attempts.
3. Idempotent booking confirmation APIs for client/network retries.
4. Theater-level sharding to reduce lock contention hotspots.

## Version roadmap
| Version | Scope |
|---|---|
| `v1-basic` | Core entities + simple booking flow |
| `v2-extended` | Better search, richer booking/payment behavior |
| `v3-optimized` | Concurrency-safe lock/confirm/cancel paths and stats hooks |

## Cross-links
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
- [Strategy pattern](../../01-design-patterns/behavioral/strategy/)
- [Observer pattern](../../01-design-patterns/behavioral/observer/)
- [Rate Limiter project](../rate-limiter/)
- [Job Scheduler project](../job-scheduler/)
