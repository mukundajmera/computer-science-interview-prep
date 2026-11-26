
# Social Post Search System

## Problem Statement

Design a post search platform that indexes social content and serves keyword queries with freshness and ranking controls.

---

## Requirements and Constraints

### Functional Requirements

1. Ingest posts and engagement signals
2. Search posts by keywords
3. Sort by recency or popularity

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Search latency | < 500 ms P95 |
| Ingestion to searchable | < 1 minute |
| Availability | 99.95% |
| Scale | Hundreds of millions of posts |

### Out of Scope

- Full recommendation/ads internals.
- Back-office analytics tooling.
- Third-party billing and compliance details.

---

## High-Level Design Outline

- API Gateway + stateless app tier
- Domain service layer
- Cache + durable primary store
- Async pipeline for fanout/indexing/notifications
- Monitoring, alerting, and replay controls

### Sample APIs

```http
POST /api/v1/posts
POST /api/v1/posts/{postId}/likes
GET /api/v1/search/posts?q=...&sort=...
GET /api/v1/search/posts/suggest?q=...
```

---

## Scoring Rubric

- Requirement framing and boundary definition
- Capacity assumptions tied to architecture
- Correct consistency model on critical operations
- Clear failure handling and degraded mode

See [RUBRIC](./RUBRIC.md).

## Common Pitfalls

See [PITFALLS](./PITFALLS.md).

## Follow-Up Questions

See [FOLLOW-UPS](./FOLLOW-UPS.md).

## Variants and Extensions

- Global multi-region rollout.
- Cost-optimized variant with relaxed freshness.
- Compliance-first variant with stricter audit rules.

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/elasticsearch](../../03-hld-concepts/elasticsearch/)
- [03-hld-concepts/read-scaling](../../03-hld-concepts/read-scaling/)
- [03-hld-concepts/write-scaling](../../03-hld-concepts/write-scaling/)
- [solutions/hld-social-post-search.md](../../solutions/hld-social-post-search.md)
