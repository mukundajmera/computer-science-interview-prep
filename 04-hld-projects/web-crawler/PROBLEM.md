# Web Crawler

## Problem Statement

Design a crawler that starts from seed URLs, respects politeness constraints, extracts content, and scales to very large crawl sets.

---

## Requirements and constraints

### Functional requirements
1. Create crawl jobs from seed URLs with domain/path scope rules, crawl depth, priority, and optional recrawl SLA.
2. Enforce robots.txt, per-host politeness, and configurable fetch budgets.
3. Normalize URLs, deduplicate already-seen URLs, and detect near-duplicate content.
4. Fetch, parse, extract outbound links, store metadata/content pointers, and schedule recrawls based on freshness priority.
5. Expose job status, frontier size, per-host error trends, retry reasons, and freshness lag.

### Non-functional requirements

| Requirement | Target |
|---|---|
| Availability | 99.9% |
| Crawl throughput | 50K fetches/s peak |
| URL corpus | 2B tracked URLs, 5% daily recrawl |
| Politeness | no host exceeds configured requests/s or robots constraints |
| Freshness | high-priority pages recrawled inside SLA window |

### Constraints
- Fetch content storage and crawl-control metadata should scale independently.
- Robots and politeness are correctness requirements, not optional niceties.
- JavaScript rendering is expensive; render only flagged pages or route to a separate render queue.
- Keep search ranking/index serving out of baseline scope.

### Out of scope
- Search index ranking, full browser rendering for every page, and content moderation policy decisions.
- Geo-specific legal takedown workflows beyond crawl allow/deny policy hooks.
- Build/deploy pipeline internals.

## API / system interface


```http
POST /api/v1/crawl-jobs
POST /api/v1/crawl-jobs/{id}/pause
POST /api/v1/crawl-jobs/{id}/resume
GET  /api/v1/crawl-jobs/{id}/stats
GET  /api/v1/crawl-jobs/{id}/errors?host=...
GET  /api/v1/operators/frontier-lag?scope=...
```

## Key design challenges

1. Scheduling the frontier so high-priority pages stay fresh without starving small hosts.
2. Enforcing robots/politeness under worker retries and distributed fetchers.
3. Deduplicating URLs and content while still discovering new links.
4. Separating crawl metadata, fetched content, and extracted graph edges so each can scale and expire differently.

## Related links
- [HLD Design Template](../DESIGN-TEMPLATE.md)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/THEORY.md)
- [Write Scaling](../../03-hld-concepts/write-scaling/THEORY.md)
