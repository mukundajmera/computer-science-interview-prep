# URL Shortener System

## Problem Statement

Design a URL shortener that converts long URLs into compact links, serves low-latency redirects at global scale, and supports lightweight analytics.

---

## Requirements and Constraints

### Functional Requirements

1. Create short URL for a long URL.
2. Redirect short URL to original URL.
3. Optional custom alias support.
4. Optional expiration for links.
5. Basic per-link click counting.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Redirect latency | < 100 ms P99 |
| Create latency | < 200 ms P99 |
| Availability | 99.99% |
| Durability | No link loss after acknowledgement |
| Read/Write ratio | ~100:1 |
| Scale | Billions of redirects/month |

### Capacity Assumptions

- 100M DAU.
- 100M new links/month.
- 10B redirects/month.
- 5-year retention default for active links.

### Out of Scope

- Full abuse detection pipeline internals.
- Billing/subscription logic.
- Rich campaign attribution modeling.

---

## High-Level Design Outline

### Core Services

- API Gateway + rate limiter
- URL Creation Service
- Redirect Service
- Key generation strategy (counter/range or random + collision check)
- Analytics ingestion pipeline

### Storage and Cache

- Primary key-value/NoSQL store keyed by short code.
- Redis cache for hot redirects.
- Event stream + OLAP/time-series store for analytics.

### API Surface (Illustrative)

```http
POST /api/v1/urls
GET /{shortCode}
GET /api/v1/urls/{shortCode}/stats
```

---

## Scoring Rubric

Strong answers explicitly cover:

1. Unique short-code generation strategy and collision handling.
2. Read-heavy optimization with cache-first redirect path.
3. Idempotency and conflict handling for custom aliases.
4. Redirect-path isolation from analytics latency.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Relying only on random keys without collision strategy.
- Blocking redirect on analytics writes.
- Missing custom-alias conflict semantics.
- Ignoring hot-key behavior for viral links.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- Deterministic shortening (same long URL -> same short URL)?
- Multi-region write acceptance and key-space partitioning?
- Safety interstitials for suspicious links?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Vanity domains per tenant.
- Bulk shorten API.
- Delayed activation and campaign windows.

---

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/caching](../../03-hld-concepts/caching/)
- [03-hld-concepts/consistent-hashing](../../03-hld-concepts/consistent-hashing/)
- [03-hld-concepts/rate-limiting](../../03-hld-concepts/rate-limiting/)
- [04-hld-projects/file-storage](../file-storage/)
