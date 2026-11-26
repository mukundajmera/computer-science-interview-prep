# API Gateway Strong Answer

## Overview
Say: "I will design an API Gateway handling 100k peak QPS, terminating mTLS, validating JWTs via locally cached JWKS, and enforcing distributed rate limits via Redis."

## Design Contract
Say: "The architecture adheres strictly to the design contract with a stateless Filter Chain intercepting HTTP/2 traffic and routing to HTTP/1.1 microservices, as outlined in [DESIGN.md](./DESIGN.md) and [architecture.mmd](./diagrams/architecture.mmd)."

## Failure Trace
Say: "In a failure trace where a downstream service times out, the Circuit Breaker filter will transition from CLOSED to OPEN, shedding traffic with 503s. It will later transition to HALF-OPEN to test recovery."

## Beginner vs Staff
### Beginner
Say: "The API Gateway proxies requests to backend services."
### Staff
Say: "The gateway uses Redis Lua scripts for atomic token bucket operations, but relies on a local token batch cache to meet the <10ms P99 latency target by avoiding Redis network round-trips on every request."
