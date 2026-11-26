# Rate Limiter - Common Pitfalls

## Common pitfalls
1. Returning only `allow/deny` and omitting retry metadata.
2. Coupling policy lookup with per-key mutable algorithm state.
3. Ignoring fallback behavior during config/store failures.
4. Using wall-clock inconsistently at window boundaries.
5. Treating thread safety as a later optimization.

## Why these fail interviews
- They hide product-impacting behavior under load.
- They produce brittle code when policies grow.
- They under-specify contracts needed by API consumers.

## Mitigations
- Standardize result envelope with limit/reset/retry fields.
- Keep policy engine and algorithm state store separated.
- Define fallback mode at design time, not incident time.
- Add same-key concurrent access tests.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Concurrency in LLD](../../00-theory/system-design-fundamentals/concurrency-in-lld.md)
