# Webhook Dispatcher - System Design

## Architecture

1. **Dispatcher Engine:** The main entry point. Accepts events and places delivery tasks onto an internal queue.
2. **Subscription Manager:** Stores subscriber configurations, including target URL, secret for HMAC, and topic/regex filter.
3. **Worker Pool:** Consumes from the internal queue.
4. **Delivery Task:** Represents a pending dispatch. Keeps track of its current attempt count.
5. **HTTP Dispatcher (Abstracted):** Generates the HMAC-SHA256 signature, acquires the destination-specific semaphore, and performs the outbound HTTP call.

## Component Interactions
1. Client publishes `Event(topic="order.created", payload={"id": 123})`.
2. `DispatcherEngine` looks up subscribers matching the topic.
3. For each subscriber, a `WebhookTask` is created and queued.
4. A worker thread picks up the task.
5. The worker calculates the HMAC signature.
6. The worker attempts to acquire a permit from the destination's semaphore.
7. Upon acquiring, the HTTP call is simulated.
8. If success (200 OK), task completes.
9. If failure, attempt count increments. If `attempt <= max_retries`, a new delayed task is scheduled using exponential backoff with full jitter. If exhausted, it routes to the DLQ.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Approach](APPROACH.md)
- [Rubric](RUBRIC.md)
- [Pitfalls](PITFALLS.md)
- [Follow-Ups](FOLLOW-UPS.md)
