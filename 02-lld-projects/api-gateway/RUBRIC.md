# Grading Rubric: API Gateway

## Core Functionality (0-7 points)

- **L4 (Intuitive minimum example):** Basic prefix-based routing works; can dispatch to a backend handler via `handle(Request)`. Implements a filter chain that can successfully short-circuit requests (e.g., authentication).
- **L5 (Trade-offs):** Filter chain supports both pre and post filters (e.g., logging duration). Implements stateful filters like rate limiting and correctly handles edge cases (e.g., missing headers). Explains trade-offs of in-memory sliding window versus distributed token bucket.
- **L6/L7 (Optional failure trace with assumptions):** Identifies race conditions in rate limiting and circuit breakers. Implements fine-grained locking and atomic state transitions to prevent thundering herd problems during HALF_OPEN recovery. Distinguishes proof sketch simulation from a fully deployed, distributed rate-limited system.

## Resiliency and Circuit Breaking (0-3 points)

- **0 points:** No circuit breaker implemented.
- **1 point (L4):** Circuit breaker tracks failures and transitions to an OPEN state, failing fast.
- **2 points (L5):** Circuit breaker correctly transitions to HALF_OPEN after a timeout and can recover back to CLOSED. Uses thread-safe primitives.
- **3 points (L6/L7):** Circuit breaker explicitly differentiates between gateway-generated errors (like 429) and backend errors (like 500 or timeouts), ensuring the backend is not penalized for gateway rejections.
