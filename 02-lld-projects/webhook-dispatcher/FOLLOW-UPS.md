# Webhook Dispatcher - Follow-Up Questions

## Follow-up questions

1. **How would you scale this to multiple nodes?**
   - Use a distributed message broker (like Kafka or RabbitMQ) instead of an in-memory queue to share tasks across worker nodes. Use Redis or a database for distributed rate limiting/semaphores.
2. **How do you handle strictly ordered event delivery?**
   - Group events by an aggregation key (e.g., `user_id`) and ensure all events for that key are routed to the same partition/worker, processing them sequentially.
3. **What happens if the dispatcher crashes with pending events in the queue?**
   - With an in-memory queue, data is lost. For durability, events must be persisted to a write-ahead log (WAL) or durable queue before acknowledgment.

## Variants and extensions
- **Circuit Breaker:** Instead of just retrying, implement a circuit breaker that stops sending requests entirely to a destination that fails consistently.
- **Batching:** Allow subscribers to receive multiple events in a single HTTP request to reduce overhead.

## Interviewer probes to prepare
- "Show me exactly how you calculate the backoff delay."
- "What happens if a destination URL is dynamically generated for each request? Will your per-destination semaphore map grow indefinitely?"
