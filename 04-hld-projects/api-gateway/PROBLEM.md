# API Gateway

## Problem Statement
Design an API Gateway that acts as a single entry point for a microservices architecture. It handles reverse proxy routing, distributed rate limiting, security (auth/mTLS), and resilience (circuit breaking/retries).

---

## Requirements and Constraints

### Functional Requirements
1. **Reverse Proxy Routing**: Path/Host-based routing, HTTP/2 to HTTP/1.1 down-conversion.
2. **Distributed Rate Limiting**: Token Bucket algorithm with client-tier quotas (e.g., Free vs Premium) using Redis Lua scripts and local token caching.
3. **Security & Auth**: JWT validation (local public key verification via JWKS), mTLS termination, CORS handling, and header scrubbing.
4. **Resilience**: Circuit breaker (Netflix Hystrix pattern: CLOSED -> OPEN -> HALF-OPEN), retry budgets with exponential backoff and jitter, shedding non-critical traffic.

### Non-Functional Requirements
| Requirement | Target |
|---|---|
| Added Latency | < 10 ms P99 (excluding downstream) |
| Availability | 99.99% |
| Throughput | 100k peak QPS |

### Capacity Assumptions
- 10M DAU making an average of 50 API calls/day.
- 500M total requests per day.
- Avg QPS: ~6k QPS.
- Peak QPS (burst factor x15): ~90k-100k QPS.
- Bandwidth: 100k QPS * 2 KB avg payload = ~200 MB/s.

### Out of Scope (Non-Goals)
- Detailed implementation of simulators in code.
- Admin UI/portal for routing configuration.
