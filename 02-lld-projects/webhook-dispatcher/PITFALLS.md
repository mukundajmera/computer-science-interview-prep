# Webhook Dispatcher - Common Pitfalls

## 1. Thread Exhaustion / Blocking
- **Signal:** The system becomes unresponsive under high load or when downstream services are slow.
- **Root Cause:** Using an unbounded thread pool or holding threads while waiting for long exponential backoffs instead of rescheduling the task asynchronously.
- **Mitigation:** Use a bounded thread pool and a delayed queue (or separate scheduler thread) for retries rather than `Thread.sleep()` in the worker thread.

## 2. Global Concurrency Limits Instead of Per-Destination
- **Signal:** A slow destination slows down delivery to all other healthy destinations.
- **Root Cause:** Using a single global lock or semaphore for all outbound HTTP requests.
- **Mitigation:** Use a `ConcurrentHashMap` of `Semaphore` objects keyed by the destination domain/URL.

## 3. Incorrect Full Jitter Implementation
- **Signal:** Retries still cluster together causing thundering herds.
- **Root Cause:** Implementing pure exponential backoff (`delay = base * 2^attempt`) without randomizing the delay.
- **Mitigation:** Ensure the delay is `random(0, base * 2^attempt)`.

## 4. Unsafe Payload Modification
- **Signal:** HMAC signature validation fails on the receiver side.
- **Root Cause:** Serializing the JSON payload differently on the sender and receiver, or modifying the payload after signing.
- **Mitigation:** Sign the exact byte array/string representation that will be transmitted.
