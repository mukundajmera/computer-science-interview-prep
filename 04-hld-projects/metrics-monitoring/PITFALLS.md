# Metrics Monitoring — Common Pitfalls

1. Accepting unbounded labels, causing cardinality explosions.
2. Mixing raw samples and downsampled data without query-time semantics.
3. Alerting directly on noisy raw series without burn-rate windows.
4. No late-data policy, leading to unstable dashboards and repeated re-alerting.
5. Single storage tier for all retention horizons, increasing cost and query latency.
6. Ignoring per-tenant quota isolation.

## How to avoid them
- Enforce label allow-lists, per-series budgets, and drop/transform policies.
- Define hot/warm/cold retention with explicit query fallback order.
- Separate alert evaluation from dashboard query serving.
