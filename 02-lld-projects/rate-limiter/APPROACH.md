# Design Approach for Rate Limiter

## Approach overview
Separate three concerns early: policy resolution, algorithm math, and mutable client state updates. This keeps algorithm swaps and distributed evolution manageable.

## Step 1: Clarify API contract
1. Define an explicit result object instead of raw boolean.
2. Standardize time fields (`reset_at`, `retry_after`) and units.
3. Define behavior for unknown keys/endpoints and store outages.

## Step 2: Design for correctness first
- Treat per-key decision as an atomic operation.
- Avoid check-then-act races in token/window updates.
- Keep clock handling monotonic and deterministic in tests.

## Step 3: Keep algorithm pluggable
- Use `RateLimitAlgorithm` strategy boundary.
- Keep `RateLimiterFactory` responsible for algorithm construction.
- Keep policy model independent of algorithm internals.

## Step 4: Handle scarcity explicitly
- Represent capacity as tokens/permits/window budget.
- Define refill/release semantics and timeout behavior clearly.
- Add weighted consumption hooks for high-cost operations.

## Step 5: Progressive versions
- `v1-basic`: one algorithm, one policy, simple response.
- `v2-extended`: strategy/factory, richer metadata, better policy handling.
- `v3-optimized`: thread-safe state, efficient counters, cleanup hooks.

## Requirements and constraints checklist
- Deterministic decision under concurrent calls for same key.
- Stable API contract for callers and tests.
- Clear fallback mode under dependency failure.
- Java/Python parity for algorithm responsibilities.

## Scoring rubric
See [RUBRIC.md](./RUBRIC.md).

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Variants and extensions
1. Multi-dimensional throttling (requests + bytes + compute cost).
2. Priority classes with reserved quota pools.
3. Shadow-mode policy validation before rollout.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
- [Job Scheduler pitfalls](../job-scheduler/PITFALLS.md)
