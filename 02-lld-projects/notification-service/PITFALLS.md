# Pitfalls

- **Concurrency Race Conditions:** Modifying counts in `RateLimiter` without concurrency controls (e.g., non-atomic increments in Java or missing Locks in Python) allows limits to be exceeded under high thread contention.
- **Unbounded Queues:** Using an unbounded `PriorityBlockingQueue` without capacity limits. A traffic spike will lead to OutOfMemoryError.
- **Busy Waiting on Rate Limits:** Re-enqueueing a rate-limited notification immediately into the main queue causes CPU thrashing instead of using a delayed/retry queue for backoff.
