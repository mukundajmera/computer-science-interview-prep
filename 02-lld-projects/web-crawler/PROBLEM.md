# Web Crawler

## Problem Statement
Design interview-focused low-level components for a web crawler with progressive implementations (`v1-basic`, `v2-extended`, `v3-optimized`) in Java and Python.

## Requirements and constraints

### Functional requirements
1. Manage crawl frontier from seed URLs with deterministic dequeue order.
2. Normalize and deduplicate URLs before scheduling fetches.
3. Persist fetch result metadata (`status`, `content_hash`, `fetched_at`).
4. Support host-level politeness policy and retry budget per URL.

### Non-functional requirements
- No live network dependency in tests; use fetcher abstraction.
- Deterministic crawl outcomes under fixed seed set.
- Thread-safe frontier processing in `v3`.
- Standard-library-only implementation.

## Version roadmap
- **v1-basic:** single-thread frontier + visited set.
- **v2-extended:** pluggable URL normalizer, retry policy, and host limiter.
- **v3-optimized:** concurrent fetch pipeline, partitioned frontier, recovery hooks.

## Related content
- [HLD Web Crawler](../../04-hld-projects/web-crawler/)
- [Rate Limiting Concept](../../03-hld-concepts/rate-limiting/THEORY.md)
