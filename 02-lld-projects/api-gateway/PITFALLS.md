# Pitfalls: API Gateway

## Common Mistakes

### Penalizing Backends for Client Errors
A common mistake when integrating circuit breakers is to wrap the entire `handle()` method or include filter responses (like 401 Unauthorized or 429 Too Many Requests) as failures against the backend. This causes the circuit breaker to trip due to bad client behavior, rendering the healthy backend inaccessible to good clients. The circuit breaker must only wrap the actual dispatch call and only record 5xx errors or timeouts. Code counterexample: If `backendRes.statusCode >= 500` is missing and it triggers on `429`.

### Not Applying Post-Filters on Short-Circuits
When a pre-filter (like an Auth filter) rejects a request, some implementations just return the response directly, skipping the post-filters. This results in lost metrics and missing logs for rejected requests. The `handle()` method must catch the short-circuited response and pass it through the post-filters in reverse order before returning via `applyPostFilters(request, response)`.

### Coarse-Grained Locking in Rate Limiters
Using a single global lock for the entire rate limiting filter creates a severe bottleneck. Thread-safe implementations should use fine-grained locking, such as a concurrent hash map for the client buckets, and lock only at the specific client's bucket level (`clientLocks.computeIfAbsent`) when appending timestamps.

### Unbounded In-Memory State
In the rate limiting filter, appending timestamps indefinitely without cleaning up old ones will lead to memory leaks. Implementations must proactively remove timestamps that fall outside the sliding window before making a rate limit decision (`clientRequests.removeIf(t -> now - t >= windowMillis)`).

### Mismanaging Circuit Breaker State Transitions
Failing to handle the `HALF_OPEN` state atomically can lead to a "thundering herd" problem where multiple concurrent threads see the timeout has passed and all attempt to test the backend simultaneously. State transitions from `OPEN` to `HALF_OPEN` must use atomic compare-and-set operations (`state.compareAndSet(State.OPEN, State.HALF_OPEN)`) to ensure only one test request is allowed through.
