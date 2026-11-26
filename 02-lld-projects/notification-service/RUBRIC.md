# Interview Rubric

- **L4 (Intuitive Minimum Example):** Implements `Notification`, `Channel` interface, and a basic priority queue. Demonstrates synchronous or basic async processing without strict thread safety.
- **L5 (Trade-offs):** Correctly implements concurrency controls (e.g., Locks or Atomics on `RateLimiter` and dispatcher queues). Identifies trade-offs between in-memory queues (faster but prone to OOM/data loss) and distributed brokers.
- **L6/L7 (Failure Trace & Assumptions):** Maps out exact failure traces (e.g., how a rate-limited message moves to `retryQueue` with exponential backoff and eventually drops after `maxRetries`). Accurately calculates memory footprint of the queue.
