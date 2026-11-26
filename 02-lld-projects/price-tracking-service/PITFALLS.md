# Price Tracking Service - Common Pitfalls

## Common pitfalls
1. Storing only the latest price and losing the history retrieval requirement.
2. Dispatching alerts before the accepted price mutation is recorded.
3. Treating duplicate price events as new changes when v3 requires idempotency.
4. Mixing subscription ownership, threshold evaluation, and notification delivery into one class.
5. Leaving history reads unbounded or dependent on full scans for every query.

## Why these fail interviews
- They break the stated event processing, history, and alert responsibilities.
- They make retries capable of duplicate notifications.
- They hide the storage and query tradeoffs behind one procedural collector.

## Mitigations
- Define the price event identity, product key, timestamp, and value before choosing storage.
- Persist the accepted mutation, then evaluate subscriptions and dispatch alerts.
- Keep collector, history store, subscription service, and dispatcher roles separate.
- Bound history queries by product and window so complexity can be explained.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
