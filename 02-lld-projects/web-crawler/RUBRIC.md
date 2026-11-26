# Web Crawler - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies seed handling, depth/frontier bounds, metadata persistence, retries, and host politeness |
| Frontier design | 25% | Separates deterministic queue behavior, visited tracking, URL canonicalization, and partitioning |
| Correctness and deduplication | 25% | Normalizes URLs before scheduling and records fetch metadata/content hashes consistently |
| Concurrency and politeness | 20% | Keeps fetch, parse, retry, and host-budget decisions safe under concurrent frontier processing |
| Extensibility and communication | 15% | Explains v1 to v3 evolution through pluggable policies, recovery hooks, and no-live-network tests |

## Performance bands
- `1/5`: raw URL queue with direct network calls and no dedup or politeness boundary.
- `3/5`: working crawler with basic visited set and retries but weak frontier recovery or host controls.
- `5/5`: deterministic frontier design with canonicalization, metadata capture, bounded retries, and concurrent-safe host policy.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Rate Limiter rubric](../rate-limiter/RUBRIC.md)
