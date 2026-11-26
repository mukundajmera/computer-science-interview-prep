# Strong Answer

**Pacing Target:** 45 minutes

## 1. Requirements (5 mins)
**Say:** "Let's align on the requirements. We need a multi-channel dispatcher handling user preferences, priority levels, rate limits, and exponential backoff retries."

## 2. Component Design & APIs (10 mins)
**Say:** "We define an entry API `dispatchBasedOnPreference` (or `dispatch_based_on_preference` in Python) that checks a `UserPreferenceMatrix` and queues the `Notification`. The `RateLimiter` checks channel capacity. The worker thread runs `processOne` (or `process_one`)."
*(See [CODE-WALKTHROUGH.md](./CODE-WALKTHROUGH.md) for details)*

## 3. Concurrency Defense (10 mins)
**Say:** "We use a thread-safe priority queue and atomic operations (like `AtomicInteger` in Java or explicit locks in Python) to ensure thread-safe capacity checking in the rate limiter."
*(See [PITFALLS.md](./PITFALLS.md) for counterexamples)*

## 4. Failure & Retry Trace (10 mins)
**Say:** "If a channel is rate-limited or fails, the message is placed in a retry queue with an exponential delay based on attempt count. Once `maxRetries` is reached, it is dropped."

## 5. Deployment Reality vs. Simulation (10 mins)
**Say:** "This implementation is an in-memory proof sketch. In a deployed system, we would replace the memory queues with Kafka/RabbitMQ, the in-memory preferences with Redis, and the single-node rate limiter with a distributed counter (e.g., Redis Lua script)."
*(See [FOLLOW-UPS.md](./FOLLOW-UPS.md) for extensions and [RUBRIC.md](./RUBRIC.md) for evaluation)*
