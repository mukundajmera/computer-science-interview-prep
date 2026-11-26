
# Price Tracking Service - Approach

## 1. Clarify boundaries first

- Confirm required consistency boundary.
- Confirm acceptable freshness window.
- Split read path and write path explicitly.

## 2. Estimate only what changes design

- Peak QPS and burst profile.
- Storage/write amplification assumptions.
- Primary bottleneck category.

## 3. Choose architecture progression

- v1: single-region baseline.
- v2: cache + async fanout/indexing pipeline.
- v3: distributed and replay-safe architecture.

## 4. Lead with deep dives

1. Correctness and idempotency path.
2. Hotspot handling.
3. Failure recovery and replay.

## 5. Closing pattern

- Re-state key SLOs.
- Name one intentional trade-off.
- Name one concrete next evolution step.
