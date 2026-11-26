# Code Walkthrough

## Version Delta Table
| Version | Features | Data Structures |
|---------|----------|-----------------|
| **v1** | Basic synchronous dispatch | Dictionary map for channels |
| **v2** | Asynchronous priorities, basic rate limits | `PriorityQueue`, `RateLimiter` |
| **v3** | User preferences, retry queue, exp. backoff | `UserPreferenceMatrix`, delayed `retryQueue` |

## Entry APIs
- `dispatch_based_on_preference` (Python) / `dispatchBasedOnPreference` (Java): Enqueues messages based on user preferences.
- `process_one` (Python) / `processOne` (Java): Dequeues and processes one notification, moving it to retry queue on failure or rate-limit.

## Correctness Invariants
1. **Rate Limit Concurrency**: The `RateLimiter` increments counts atomically (using `AtomicInteger` with `ConcurrentHashMap` in Java / `threading.Lock` in Python) to prevent race conditions across channels.
2. **Retry Boundaries**: Retry count never exceeds `max_retries` / `maxRetries`.
3. **Priority Order**: `PriorityQueue` guarantees O(log n) retrieval of the highest priority task (or oldest if equal priority).

## Algorithmic Complexity
- **Time Complexity**: Enqueue/Dequeue is O(log N) where N is queue size.
- **Space Complexity**: O(N) memory bound (noting that without a max queue size, this could OOM in spikes).
