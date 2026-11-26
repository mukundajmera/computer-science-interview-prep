# Movie Ticket Booking - Common Pitfalls

## Common pitfalls
1. Check-then-lock race on seat selection.
2. Confirming bookings without validating lock ownership.
3. Releasing seats on timeout even after confirmation.
4. Allowing cancel operations by non-owners.
5. Breaking prior API contracts while adding `v3` methods.

## Why these fail interviews
- They expose correctness gaps under realistic contention.
- They hide weak state-transition discipline.
- They create avoidable regressions in tests and demos.

## Mitigations
- Use atomic lock acquisition for full seat set.
- Centralize lifecycle transition guards in one service boundary.
- Add compatibility wrappers when renaming or reordering method signatures.
- Add explicit timeout and cancellation tests.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
