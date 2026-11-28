# API Design

API design defines how clients and services interact. In HLD interviews, a strong API section is concise, requirement-driven, and resilient under retries and growth.

## Core responsibilities

- Define stable resource contracts.
- Capture identity, filtering, pagination, and mutation semantics.
- Enforce authn/authz and abuse controls.
- Support backward-compatible evolution.

## Interface style choices

- REST: best default for external product APIs.
- GraphQL: useful for response-shape flexibility across clients.
- RPC/gRPC: efficient internal service contracts.

## Resource and method discipline

- Resource-oriented paths (`/bookings`, `/events/{id}/tickets`).
- Correct HTTP semantics and idempotency behavior.
- Explicit pagination strategy for large collections.
- Consistent status/error contract.

## Reliability concerns

- Idempotency keys for retry-safe create operations.
- Timeout and retry policy aligned with method semantics.
- Versioning strategy that preserves existing clients.

---

## Requirements and constraints

- Every endpoint should map to a clear business capability.
- Mutating APIs must define retry/idempotency behavior.
- Large list endpoints require pagination and ordering guarantees.
- Authn/authz and rate-limit boundaries must be explicit.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Contract clarity | Clean resources and parameter boundaries | Action-heavy endpoint design |
| Correctness | Method semantics and idempotency handled correctly | Retry behavior ignored |
| Evolution | Versioning and compatibility strategy stated | Breaking changes assumed acceptable |
| Production readiness | Auth, rate limit, error shape included | Security and abuse controls omitted |

## Common pitfalls

- Spending too long on endpoint naming and too little on architecture.
- Mixing filtering, identity, and mutation payload concerns.
- Missing idempotency strategy for client retries.
- Designing versioning only after breaking clients.

## Follow-up questions

- When would you switch from offset to cursor pagination?
- What would make GraphQL a better fit than REST here?
- How do you roll out v2 without forcing immediate client migration?

## Variants and extensions

- BFF APIs per client surface.
- Hybrid API: external REST + internal gRPC.
- Async command API with job status resource.

## 📊 Diagrams

- [Versioning evolution flow](./diagrams/versioning-evolution-flow.mmd): how a breaking change is shipped as a parallel v2, clients migrate gradually without forced upgrades, and v1 is deprecated only after migration completes.
- [Pagination selection](./diagrams/pagination-selection.mmd): the offset versus cursor decision for large list endpoints, driven by whether clients need deep pages over fast-changing data.

## Related concepts

- [REST API Design](../../00-theory/networking-basics/rest-api-design.md)
- [API Gateway](../api-gateway/)
- [Idempotency](../idempotency/THEORY.md)
- [Rate Limiting](../rate-limiting/)
- [Microservices Communication](../microservices-communication/)
- [E-commerce HLD](../../04-hld-projects/ecommerce-backend/)
