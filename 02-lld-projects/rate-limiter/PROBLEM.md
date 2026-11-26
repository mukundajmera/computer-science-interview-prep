# Rate Limiter System

## Problem statement
Design an interview-grade rate limiter that enforces per-client request limits with clear metadata, predictable behavior under concurrency, and a path from single-node to distributed enforcement.

## Requirements and constraints

### Functional requirements
1. Evaluate `allow`/`deny` decisions per client key and policy.
2. Support multiple algorithms (`TokenBucket`, `SlidingWindowLog`, `SlidingWindowCounter`).
3. Return structured result metadata (`remaining`, `retry_after`, `reset_at`).
4. Support endpoint-specific overrides and safe default policy behavior.
5. Allow policy composition across scopes (global, tenant, client, endpoint).

### Non-functional requirements
- Constant-time hot-path decisions for common policies.
- Thread-safe updates for shared client state in `v3-optimized`.
- Memory-aware state model for high-cardinality keyspaces.
- Deterministic behavior for local tests.

### Constraints and assumptions
- In-memory state for LLD scope; no external datastore required for core versions.
- Single-process monotonic clock assumption in local implementation.
- Config and algorithm selection are runtime inputs, not compile-time forks.
- Failure behavior must be explicit (`fail-open`, `fail-closed`, or hybrid).

## Core entities
| Entity | Responsibility |
|---|---|
| `RateLimiter` | Primary API for request evaluation |
| `RateLimitAlgorithm` | Strategy contract for limit computation |
| `RateLimitConfig` | Policy parameters and defaults |
| `RateLimitResult` | Decision + metadata returned to caller |
| `ClientState` | Per-key mutable state used by algorithm |

## Concurrency and scarcity expectations
- Updates for the same key are serialized or made atomic.
- No over-admission during concurrent check/update operations.
- Scarce resources (tokens/permits/window budget) are released or refilled safely.

## Scoring rubric
See [RUBRIC.md](./RUBRIC.md).

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Variants and extensions
1. Weighted request cost (e.g., read=1, write=3).
2. Burst-sensitive endpoint policies with custom cooldown behavior.
3. Hybrid local + remote quota enforcement.
4. Dynamic config rollout with versioned snapshots.

## Version roadmap
| Version | Scope |
|---|---|
| `v1-basic` | Token bucket + basic allow/deny |
| `v2-extended` | Multi-algorithm strategy + richer result contract |
| `v3-optimized` | Concurrency-safe updates + memory-efficient counters |

## Cross-links
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
- [Strategy pattern](../../01-design-patterns/behavioral/strategy/)
- [Factory method pattern](../../01-design-patterns/creational/factory-method/)
- [Movie Ticket Booking project](../movie-ticket-booking/)
- [Job Scheduler project](../job-scheduler/)
