
# Price Tracking Service - Common Pitfalls

1. No explicit consistency boundary for critical mutations.
2. No idempotency handling for retries.
3. Over-reliance on cache without invalidation/rebuild strategy.
4. Missing hot-key/hot-partition mitigation.
5. No degraded mode when downstream dependencies fail.

## Self-check

- Did you define which operation must be strongly correct?
- Did you define replay/backfill behavior for derived state?
- Did you quantify at least one peak bottleneck?
