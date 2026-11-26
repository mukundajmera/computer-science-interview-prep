
# YouTube Top-K LLD

## Problem Statement

Windowed top-K aggregation over large video-view event streams.

---

## Functional Requirements

1. Support core operations with clear request/response contracts.
2. Validate mutations and reject invalid transitions.
3. Provide read views for latest state and recent activity.

## Non-Functional Requirements

1. Deterministic behavior for repeated requests (idempotency support in v3).
2. Thread-safe structure for concurrent access in scaled versions.
3. Extensible interfaces for alternate persistence/backing stores.

## Core Types

- `ViewEventIngestor`
- `WindowedTopKAggregator`
- `TopKQueryService`
- `WindowStateStore`

## Version Roadmap

- `v1-basic`: in-memory baseline.
- `v2-extended`: abstraction boundaries and richer query flows.
- `v3-optimized`: distributed-friendly interfaces and idempotency hooks.
