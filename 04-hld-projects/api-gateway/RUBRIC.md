# API Gateway Rubric

## Requirements
- Supports HTTP/2 to HTTP/1.1 reverse proxy.
- Distributed Rate Limiting.
- Resilience (Circuit breaker).

## Design Contract
- Matches the design contract outlined in [DESIGN.md](./DESIGN.md).
- Architecture diagram is at [architecture.mmd](./diagrams/architecture.mmd).

## Failure Trace
- Trace demonstrates circuit breaker state transitions (CLOSED -> OPEN -> HALF-OPEN) when downstream repeatedly times out.

## Beginner vs Staff
### Beginner
- Focuses on basic routing and reverse proxying concepts.
### Staff
- Focuses on detailed capacity planning, high availability, and specific distributed consensus trade-offs (e.g. Redis Lua vs Cassandra).
