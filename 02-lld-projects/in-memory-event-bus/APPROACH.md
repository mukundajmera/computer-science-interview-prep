# In-Memory Event Bus - Approach

We will design a thread-safe in-memory event bus supporting pub-sub, partitioning, consumer groups, offset tracking, retries, and dead-letter queues. 

## Bounded Lifecycle and Backpressure
- Subscriber queues will be explicitly bounded. The system will define clear behaviors (block, drop, reject) when a queue is full.
- The system will ensure that concurrent subscribe/unsubscribe, handler failures, and shutdowns cleanly release resources and do not leak threads or silently lose promised deliveries.

## Deterministic Ordering and Replay
- Event sequences and offsets will be deterministically ordered per partition. 
- While delivery guarantees are 'at-least-once', the approach clarifies that handler replay does not magically provide 'exactly-once' external side effects; external idempotency is required.

## Phased Implementation
- **v1-basic**: Basic topic and pub-sub mechanics, simple threading.
- **v2-extended**: Adds partitions, consumer groups, and offset tracking.
- **v3-optimized**: Adds retry queues, dead-letter topics, and explicit bounded queues for backpressure handling.

Key components:
- EventBus Broker
- Topic (with partitions)
- Partition (stores events, thread-safe append/read, deterministic offsets)
- Consumer Group (tracks offsets)
- Consumer Worker (polls and processes events, bounded queues)
- Retry/DLQ Manager
