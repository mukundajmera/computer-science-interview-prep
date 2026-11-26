# Web Crawler — Interview Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---|---|
| Scope control | 10% | Defines crawl boundary, robots policy, and freshness targets |
| Throughput sizing | 15% | Estimates URLs/sec, frontier growth, and storage footprint |
| API and contracts | 10% | Clear seed, pause, resume, and crawl-status interfaces |
| Data model | 15% | Frontier, visited fingerprint, fetch result, and index-ready document models |
| Architecture | 20% | Frontier scheduler, fetchers, parser, dedup, and storage are separated cleanly |
| Reliability + politeness | 20% | Per-host rate limit, retry budget, and content dedup strategy are explicit |
| Communication | 10% | Trade-offs between freshness, coverage, and cost are defended |

## Score bands (0-35)
- **30-35:** Strong hire; correctness and web politeness constraints are handled.
- **22-29:** Hire; mostly solid with minor crawl-control gaps.
- **15-21:** Lean no-hire; crawler works conceptually but risks abuse or low quality.
- **<15:** No-hire; lacks frontier or dedup fundamentals.

## Related content
- [Caching](../../03-hld-concepts/caching/THEORY.md)
- [Rate Limiting](../../03-hld-concepts/rate-limiting/THEORY.md)
- [LLD Web Crawler](../../02-lld-projects/web-crawler/)
