# Design Approach for Web Crawler

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify requirements | 6 min | Scope boundary, freshness, robots/politeness policy |
| Capacity estimation | 6 min | URLs/day, frontier growth, host skew, storage |
| API + data model | 10 min | Crawl job APIs, frontier, visited, fingerprint model |
| Architecture | 13 min | Frontier scheduler, fetchers, parsers, dedup, storage |
| Deep dives | 7 min | Host-level throttling, retry classification, trap avoidance |
| Wrap-up | 3 min | Incremental recrawl and JS rendering extension |

## Suggested execution order
1. Define crawl scope and compliance constraints first.
2. Model host-aware frontier and dedup strategy.
3. Build fetch/parse/storage path with retries.
4. Add monitoring for crawl quality and failure hotspots.
5. Close with scale-out and focused-crawl variants.
