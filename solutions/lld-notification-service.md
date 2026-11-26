# Coach Solution: Notification Service

**Pacing Target:** 45 minutes

## 1. Requirements (5 mins)
**Say:** "Let's align on the requirements. We need a system that supports multiple channels, respects user preferences, applies rate limits per channel, handles priorities, and retries failed messages with exponential backoff."

## 2. Entity Modeling (5 mins)
**Say:** "We have `Notification`, `UserPreference`, `Channel`, `RateLimitRule`, and `RetryContext`. A `Notification` contains the payload and priority. `UserPreference` maps users to their preferred channels. `Channel` represents Email, SMS, Push, etc."

## 3. Design Pattern Justifications (10 mins)
**Say:** "I will use the **Strategy Pattern** for the different channels to make it easy to add new ones like Slack or Push without modifying the core dispatch logic. I'll use the **Command Pattern** for dispatching tasks, which naturally fits into our priority queue design. The **Observer Pattern** can be used to notify the retry engine of failures."

## 4. Concurrency Defense & Thread-Safety (10 mins)
**Say:** "For concurrency, I'll use a thread-safe `PriorityBlockingQueue` in Java (or `queue.PriorityQueue` with a explicit Locks in Python). This prevents race conditions when multiple producer threads submit notifications and multiple consumer worker threads pull them. The rate limiter will use atomic counters (`AtomicInteger` or explicitly synchronized blocks with `ReentrantLock`) to prevent race conditions when checking token bucket limits across concurrent dispatchers."

## 5. Scaling Limits & Indexing Trade-offs (5 mins)
**Say:** "In a single-node system, the scaling limit is dictated by CPU cores (worker thread saturation) and memory (the maximum size of the in-memory queues). If a massive spike in notifications occurs, an unbounded queue will cause an OutOfMemoryError. To scale horizontally, we would need to migrate from in-memory queues to a distributed broker like Kafka. For user preferences, storing them in a relational database works initially, but the indexing trade-off requires a composite index on `(user_id, notification_type)`. Caching these preferences locally with Redis or Memcached would be necessary in a production system to avoid database hits on every single dispatch request."

## 6. State Synchronization (5 mins)
**Say:** "State synchronization between the rate limiter and the dispatcher threads is critical. We must ensure that token acquisition is strictly atomic so that multiple threads do not over-consume the allowed capacity for a specific channel like SMS. Furthermore, when updating the status of a notification (e.g., from PENDING to SENT or FAILED), the state transition must be synchronized across threads. We achieve this state synchronization by wrapping the modification of state variables and associated objects within a single critical section guarded by a ReentrantLock."

## 7. Data Structure Rationale (3 mins)
**Say:** "The priority queue is implemented using a Heap data structure, which provides O(log n) insertions and removals. This allows us to efficiently fetch the highest priority message among potentially thousands of pending notifications."

## 8. Failure Handling & Production Trade-offs (2 mins)
**Say:** "Failed messages are placed in a secondary delay queue for retries using exponential backoff. If they exceed the configured maximum number of retries, they are moved to a Dead Letter Queue (DLQ). A significant trade-off here is strict ordering versus throughput; by allowing retries, we optimize for overall throughput and reliability, but this means that messages might be delivered out of order if retries occur concurrently with new messages."
