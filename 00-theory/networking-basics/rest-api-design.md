# REST API Design

REST remains the safest default for interview API design. The goal is not perfect API governance; the goal is to define a clean interface quickly and move to higher-impact architecture decisions.

---

## API Style Selection

| Style | Best Fit | Trade-off |
|------|----------|-----------|
| REST | Standard product APIs and CRUD-heavy surfaces | Endpoint proliferation for highly variable clients |
| GraphQL | Multiple clients with different response-shape needs | Resolver complexity and N+1 risks |
| RPC/gRPC | Internal service-to-service calls with strict contracts | Less web-native ergonomics |

Use REST by default unless requirements clearly demand GraphQL flexibility or RPC performance.

---

## Resource Modeling Rules

- Model nouns, not actions (`/bookings`, not `/bookTicket`).
- Use plural resources.
- Use path params for required identity (`/events/{eventId}`), query params for optional filters.
- Keep nested resources shallow and purposeful.

Example:

```text
GET    /events
GET    /events/{eventId}
GET    /events/{eventId}/tickets
POST   /events/{eventId}/bookings
GET    /bookings/{bookingId}
DELETE /bookings/{bookingId}
```

---

## Method Semantics and Idempotency

- `GET`: read-only, idempotent.
- `POST`: create/trigger, not guaranteed idempotent.
- `PUT`: full replacement, typically idempotent.
- `PATCH`: partial update; idempotency depends on operation semantics.
- `DELETE`: idempotent from state perspective.

For retry-prone create calls, add idempotency keys:

```text
Idempotency-Key: req-1234
```

---

## Pagination, Versioning, and Error Contracts

- Offset pagination: simple, weaker consistency at scale.
- Cursor pagination: stable for large/append-heavy datasets.
- Prefer URL versioning (`/v1/...`) for interview clarity.
- Keep error format consistent (`code`, `message`, optional `details`).

---

## Security and Policy Essentials

- Authentication: session/JWT for users, API keys for service/app access.
- Authorization: role/ownership checks at endpoint boundary.
- Rate limiting: per user/IP/endpoint for abuse control.
- Validate input strictly and fail closed.

---

## Requirements and constraints

- Keep public contracts backward compatible by default.
- Define idempotency behavior for all retryable write operations.
- Make pagination explicit on list endpoints expected to grow.
- Standardize error and auth behavior across all routes.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Resource design | Clear entities and clean URL hierarchy | Action-heavy endpoint naming |
| Method usage | Correct HTTP semantics and idempotency reasoning | Arbitrary verb usage |
| Reliability | Handles retries, idempotency keys, pagination | Ignores network retry behavior |
| Security | Mentions authn/authz/rate limiting boundaries | Security discussed as afterthought |

## Common pitfalls

- Over-designing API details and missing architecture trade-offs.
- Confusing required identity parameters with optional filters.
- Missing idempotency strategy for create endpoints.
- Using GraphQL/RPC without requirement justification.

## Follow-up questions

- When does GraphQL outperform REST for this problem?
- How do you version APIs without breaking old clients?
- Where should rate limiting be enforced: gateway or service?
- What contract changes are backward compatible?

## Variants and extensions

- BFF (backend-for-frontend) per client surface.
- Hybrid API: REST externally, gRPC internally.
- Event-driven writes with async status resources.

## Related Topics

- [Networking Essentials](./networking-essentials.md)
- [HTTP/HTTPS](./http-https.md)
- [API Gateway](../../03-hld-concepts/api-gateway/)
- [Rate Limiting](../../03-hld-concepts/rate-limiting/)
- [URL Shortener HLD](../../04-hld-projects/url-shortener/)
