# Approach: API Gateway

The API Gateway is a central entry point for all client requests, responsible for routing, cross-cutting concerns (authentication, rate limiting), and resiliency.

## System Components

1. **Request and Response Objects**
   - Simple value objects representing an HTTP request and response.
   - Contains path, method, headers, bounded request body, and deadlines.
   - Supports downstream cancellation tokens or flags.

2. **Router Registry**
   - Maintains a mapping between URL prefixes and target backend identifiers.
   - During request processing, it matches the incoming path against the registered prefixes to determine the appropriate backend. Gracefully handles invalid routes.

3. **Filter Chain (Chain of Responsibility Pattern)**
   - The Gateway maintains a list of `Filter` interfaces.
   - Pre-filters run before the request is routed (Authentication strictly precedes protected routing). If a pre-filter returns a `Response` (e.g., auth failure or rate limit hit), the request is short-circuited, and post-filters are applied before returning to the client.
   - Post-filters run after the backend has processed the request or after a short-circuit, allowing for logging, metrics, or response transformation.

4. **Resiliency Integration (Circuit Breaker, Retries, Deadlines)**
   - **Circuit Breaker:** Integrated at the routing/dispatching layer to track the health of specific backends. Maintains states: `CLOSED`, `OPEN`, and `HALF_OPEN`. Only backend errors count towards failures; filter short-circuits (like HTTP 429) are excluded.
   - **Retries & Deadlines:** Enforces duplicate retry eligibility based on method/headers, and propagates timeouts to downstream handlers.

## Concurrency Strategy

- **Rate Limiting:** Uses a thread-safe data structure or lock to manage the sliding window of timestamps per client.
- **Circuit Breaker:** Uses atomic variables and locks to manage the failure count and state transitions safely across multiple concurrent requests.
- **Router & Filter Chains:** Usually immutable after initialization, allowing concurrent reads without locking. If dynamic updates are required, concurrent data structures (like `CopyOnWriteArrayList`) are used.

## Evolution of the Design

- **v1 (Basic):** Implements core routing (with exact filter order: authentication precedes routing) and simple pre-filtering using fake request/response fixtures (no live servers). Validates bounded request bodies and invalid route handling.
- **v2 (Extended):** Adds sophisticated filters (rate limiting, logging), support for post-filtering running synchronously, and duplicate retry eligibility.
- **v3 (Optimized):** Introduces the Circuit Breaker for resiliency, thread-safe primitives for concurrent request processing, deadline propagation, and downstream cancellation. Deterministic fixture inputs/expected outputs are fixed across versions.
