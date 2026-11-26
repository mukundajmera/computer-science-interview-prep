# Common Pitfalls

- **Pushing instead of Pulling:** Designing the broker to push messages to consumers. This requires complex backpressure and state management at the broker, which fails at scale.
- **Random Access Storage:** Using a standard SQL database for storage. A commit log must use sequential, append-only disk I/O to achieve high throughput.
- **Ignoring the Network:** Failing to mention batching and compression. At 5M events/sec, network I/O is the primary bottleneck.
- **Overcomplicating Consumer State:** Forcing the broker to remember exactly which messages each consumer has read. The broker should only track an offset per consumer group.
