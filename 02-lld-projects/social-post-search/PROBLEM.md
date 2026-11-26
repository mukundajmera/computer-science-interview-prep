
# Social Post Search LLD

## Problem Statement

Keyword indexing pipeline with query planning and ranking abstraction.

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

- `PostIngestionService`
- `InvertedIndex`
- `QueryPlanner`
- `SearchRankingService`

## Version Roadmap

- `v1-basic`: in-memory baseline.
- `v2-extended`: abstraction boundaries and richer query flows.
- `v3-optimized`: distributed-friendly interfaces and idempotency hooks.
