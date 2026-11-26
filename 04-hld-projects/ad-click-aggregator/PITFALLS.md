# Ad Click Aggregator — Common Pitfalls

1. Using processing-time windows when interview asks for event-time correctness.
2. No dedup key strategy, causing revenue inflation from repeated delivery.
3. Rebuilding aggregates from mutable state without immutable event logs.
4. Dropping late events silently instead of applying watermark policy.
5. Ignoring hot-key skew for popular campaigns/ad-groups.
6. Mixing serving schema with ingestion schema, leading to poor query performance.

## How to avoid them
- Keep immutable event logs and recomputable aggregates.
- Declare watermark, lateness budget, and correction/backfill path.
- Add skew-aware partitioning and adaptive hot-key splitting.
