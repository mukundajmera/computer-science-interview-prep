# Web Crawler - Common Pitfalls

## Common pitfalls
1. Treating raw URL strings as unique identifiers.
2. Scheduling before URL normalization and visited-set checks.
3. Ignoring host-level politeness and crawling too aggressively.
4. Mixing fetch, parse, retry, and frontier responsibilities in one class.
5. Leaving crawl depth, retry budget, or frontier size unbounded.

## Why these fail interviews
- They cause duplicate crawling and nondeterministic outcomes from the same seed set.
- They hide external-service pressure behind a local queue abstraction.
- They make restart, recovery, and metadata correctness hard to reason about.

## Mitigations
- Canonicalize and deduplicate before enqueueing work.
- Keep fetcher, parser, retry policy, host limiter, and frontier state as separate contracts.
- Persist fetch result metadata such as status, content hash, and fetch time.
- Encode retry reason categories and enforce max frontier guards.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Rate limiting concept](../../03-hld-concepts/rate-limiting/THEORY.md)
