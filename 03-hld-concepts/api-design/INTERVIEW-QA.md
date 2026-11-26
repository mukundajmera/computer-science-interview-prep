# Interview Questions: API Design

## Core questions

### 1) What is your default API style and why?
REST is the default for most interview problems due to clarity, ecosystem maturity, and predictable operational behavior.

### 2) How do you model resources quickly?
Start from core entities, expose collection/item paths, then layer required relationships and filters.

### 3) Where do path, query, and body parameters belong?
Path = required identity, query = optional modifiers/filtering, body = mutation payload.

### 4) How do you handle retries on create endpoints?
Use idempotency keys so client retries do not create duplicate resources.

### 5) What is your pagination default?
Offset for simple low-scale lists; cursor for large/append-heavy feeds requiring stable traversal.

## Scenario questions

### 6) Your mobile and web clients need different payload shapes. What do you do?
Start with tailored REST endpoints or sparse fieldsets; move to GraphQL only if flexibility pressure is persistent and high.

### 7) How do you version APIs safely?
Use explicit versioning (commonly URL path), keep previous version active during migration, and publish deprecation timeline.

### 8) Where should rate limiting live?
Usually at gateway/edge for broad protection, with optional service-level guardrails for critical paths.

### 9) How do you enforce authorization?
At endpoint boundary with role/ownership checks, then enforce domain-level checks in service logic.

### 10) What makes an API answer "senior" in interviews?
Clear contract, correct semantics, retry safety, growth path, and explicit trade-offs in under a few minutes.

---

## Requirements and constraints

- Each answer must identify contract, correctness, and failure behavior.
- Must include compatibility/evolution consideration.
- Must include one abuse-control mechanism.
- Must stay scoped; no unnecessary protocol complexity.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Resource modeling | Clean entity-driven endpoints | Verb/action endpoint sprawl |
| Semantics | Correct method + retry/idempotency behavior | Ignores duplicate-write risks |
| Operability | Versioning, rate limits, error contract | API discussed as static spec only |
| Trade-off quality | Justifies style choice by requirements | Technology-first arguments |

## Common pitfalls

- Confusing API surface design with backend storage design.
- Adding GraphQL/RPC without clear requirement signal.
- Missing standardized error payloads.
- Ignoring authorization edge cases.

## Follow-up questions

- How would this API change at 10x traffic?
- Which endpoints would you make asynchronous first?
- How do you test backward compatibility?

## Variants and extensions

- API aggregation/BFF layer for frontends.
- Event-driven command endpoint patterns.
- Multi-tenant quota and policy controls.

## Related concepts

- [API Design Theory](./THEORY.md)
- [REST API Design](../../00-theory/networking-basics/rest-api-design.md)
- [API Gateway](../api-gateway/)
- [Rate Limiting](../rate-limiting/)
- [Notification Service HLD](../../04-hld-projects/notification-service/)
