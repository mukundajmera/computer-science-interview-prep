# Interview Questions: Real-time Updates

## Basic Questions

### 1. How do you choose between polling, SSE, and WebSocket?
**A**: Start with required interaction direction and freshness SLO. Use polling for low-frequency updates, SSE for server push only, and WebSocket for high-frequency bidirectional traffic. A decision table helps: SSE is often best for dashboards, WebSockets for chat.

### 2. Why is long polling better than simple polling?
**A**: It reduces empty responses and improves perceived freshness, but still keeps request-response overhead and connection churn.

### 3. What is the biggest hidden cost of WebSocket at scale?
**A**: Stateful connection management and memory/heartbeat overhead across many nodes. Load balancers must be configured for long idle-timeouts, and servers need ~20KB per connection.

## Intermediate Questions

### 4. How do you preserve ordering in real-time systems?
**A**: Define ordering scope (per conversation/user/partition), keep monotonic sequence IDs, and replay missed sequence gaps on reconnect.

### 5. How do you handle multi-device users?
**A**: Maintain a user-to-connection index and deduplicate device delivery where needed by idempotency keys or event IDs.

### 6. How does load balancing change for persistent channels?
**A**: You need affinity or stable routing for connection state; stateless round-robin assumptions break for channel-based delivery. LBs also need appropriate idle timeouts and capability to handle massive connection counts without port exhaustion.

## Advanced Questions

### 7. What is a resilient reconnect strategy?
**A**: Client sends last acknowledged offset/event ID (Last-Event-ID), server replays missed events from durable log or in-memory replay buffer, then resumes live stream. If the buffer has rotated past the offset, the client must do a full state sync.

### 8. How do you handle a reconnect storm (thundering herd)?
**A**: Use jittered reconnect storm math. If 500K clients reconnect simultaneously, they will crush the auth service. Introducing exponential backoff with random jitter spreads the load over a minute, keeping the request rate within safe bounds.

### 9. How do you handle slow consumers?
**A**: Implement slow-consumer policies. If a client can't read fast enough, buffers grow and cause OOM. The best policy is usually to disconnect the slow consumer, forcing them to reconnect and catch up later.

### 10. How do you scale fan-out to millions of connections?
**A**: Use a fan-out architecture with pub/sub (like Redis Pub/Sub). For a "celebrity channel" with millions of subscribers, avoid sending 1M messages from the broker; instead, send 1 message per connection manager, which then locally fans out to its subscribers.

## Rapid Follow-up Drill

1. Which channel would you pick for live stock ticker web UI?
2. Which metric tells you connection manager saturation is near?
3. Where would you enforce event deduplication?
4. How do you roll out channel protocol upgrades safely?

---

### Live-comments follow-up

Q: How do you recover missed comments after reconnect?
A: Track per-stream cursors and replay recent events from a replay buffer before switching back to live stream push. If the gap is too large, trigger a full fetch.
