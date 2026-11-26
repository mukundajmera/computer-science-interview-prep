# Ad Click Aggregator

## Problem Statement
Design low-level components for ingesting click events and producing windowed aggregates with progressive versions in Java and Python.

## Requirements and constraints

### Functional requirements
1. Accept click events with idempotency identity and event timestamp.
2. Deduplicate repeated events before counting.
3. Aggregate by configurable windows (for example, minute/hour) and dimensions.
4. Expose query APIs for campaign/ad-group level counters.

### Non-functional requirements
- Deterministic event ordering in tests through injected event source.
- Explicit late-event handling policy.
- Thread-safe updates in `v3`.
- Standard-library-only implementation.

## Version roadmap
- **v1-basic:** in-memory counters by key.
- **v2-extended:** pluggable dedup + windowing policies.
- **v3-optimized:** concurrent ingestion pipeline and replay-friendly state snapshots.

## Related content
- [HLD Ad Click Aggregator](../../04-hld-projects/ad-click-aggregator/)
- [Stream Processing Concept](../../03-hld-concepts/stream-processing/THEORY.md)
