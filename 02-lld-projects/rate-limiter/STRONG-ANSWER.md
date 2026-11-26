# Strong Answer: Rate Limiter

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Rate Limiter, I'll start by clarifying the core requirements. I want to build a system that enforces per-client request limits using predictable behavior under concurrency. It must evaluate allow/deny decisions per client key, support different algorithms like Token Bucket, Sliding Window Log, and Sliding Window Counter, and return structured metadata (`remaining`, `retry_after`, `reset_at`). We also need to plan a path from single-node to distributed enforcement while ensuring a constant-time hot-path and thread-safe updates."

## 2. Entity Modeling & APIs (10 mins)
**Say:** "Let's define the primary entities and our API contract. We separate policy resolution, algorithm math, and mutable client state."
*   **`RateLimiter`**: The primary API, receiving requests and returning a `RateLimitResult`.
*   **`RateLimitAlgorithm`**: A strategy contract for limit computation (`tryAcquire`, `getRemainingRequests`).
*   **`RateLimitConfig`**: Holds policy parameters (e.g., burst capacity, window size, refill rate).
*   **`RateLimitResult`**: The decision payload (`allowed`, `remaining_tokens`, `reset_time_ms`).
*   **`ClientState`**: The per-key mutable state used by the algorithm (e.g., `TokenBucketState`, `SlidingWindowCounterState`).

## 3. Design Alternatives & Data Structure Rationale (10 mins)
**Say:** "We need an extensible algorithm architecture and must handle scarcity explicitly. Different algorithms offer specific trade-offs."
*   **Token Bucket (`v1-basic`)**: Memory efficient and allows burst up to bucket capacity. A map stores bucket state (`tokens`, `last_refill_timestamp`) per client. Good for smooth rate limiting over time.
*   **Sliding Window Log (`v2-extended`)**: Exact counting but memory-intensive. Maintains exact timestamps of incoming requests in a deque per client. Useful for strict, precise limits but scales poorly with high limits.
*   **Sliding Window Counter (`v3-optimized`)**: Balances memory efficiency and accuracy by using weighted proportional overlap (e.g., previous window weight + current window count). Uses fixed memory per client (O(1)).

## 4. Correctness & Complexity (10 mins)
**Say:** "Correctness, especially under contention, is critical. Our algorithm updates for the same key must be serialized or made atomic."
*   **Acceptance Case 1 - Burst & Contention:** With a frozen monotonic time, a burst capacity $B$, and 8 concurrent contenders, successes are exactly $\min(B, \text{requests})$. Rejected operations immediately return `false` and do *not* consume or refill incorrectly.
*   **Acceptance Case 2 - Determinism:** Tests for clock rollback, long idle intervals, boundary refill math, independent tenant keys, invalid rates/capacities, and bounded state cleanup are deterministic.
*   **Complexity:** We achieve O(1) time complexity for Token Bucket and Sliding Window Counter per operation, and O(1) memory per client. Sliding Window Log is O($N$) memory where $N$ is the limit.

## 5. Concurrency Defense & Failure Handling (8 mins)
**Say:** "In a multi-threaded `v3-optimized` environment, ensuring thread-safe state without massive bottlenecks is my priority."
*   **Concurrency:** We use optimistic locking (e.g., `AtomicReference.compareAndSet` in Java) for the `TokenBucketState` to update the token count. This ensures atomic check-and-decrement operations without heavy lock contention, avoiding check-then-act races.
*   **Failure & Scarcity:** Systems fail, so we design for 'Fail-Open' behavior under dependency outage. If our remote cache or limiter subsystem is unavailable, we allow requests through to prevent the limiter from taking down the core service.
*   **Distributed Evolution:** In a real production system, this single-node design scales to a distributed cache like Redis using Lua scripts for atomic operations, ensuring that the same correctness constraints (no over-admission, exact bursts) hold across multiple application nodes.

## 6. Edge Cases & Reference Contracts
*   **Normal Use-Case:** Requests within limits receive `allowed=true` and update metadata (`remaining`, `retry_after`, `reset_at`).
*   **Empty/Invalid Input:** An empty or invalid client key throws a `ValueError` (Python) or `IllegalArgumentException` (Java). Invalid config dimensions throw equivalent exceptions.
*   **Duplicate Operations/Contention:** 8 concurrent requests battling for capacity $B$ guarantee exact exhaustion where successes $=\min(B, \text{requests})$.
*   **Capacity Boundaries:** Clock rollback safely uses current token counts without giving extra quota. Boundary refill tests confirm timestamp precision math.
*   **Failure Rollbacks:** Unused tokens are not deducted if an operation gets rejected.

## 7. Version Feature Deltas
*   **`v1-basic`:** Single-threaded Token Bucket algorithm.
*   **`v2-extended`:** Adds Strategy pattern for Sliding Window Log and configurable results.
*   **`v3-optimized`:** Sliding Window Counter, thread-safety mechanisms (optimistic locking / atomics), and O(1) memory bound per client.
