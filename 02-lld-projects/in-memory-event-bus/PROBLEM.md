# In-Memory Event Bus - Problem Statement

## Functional Requirements
- **Topics & Partitions**: Support publishing events to specific topics. Each topic can have multiple partitions for parallel processing.
- **Publishers**: Publish events to topics deterministically per partition.
- **Consumer Groups**: Consumers belong to consumer groups. Distribute events among consumers (point-to-point) or broadcast (pub-sub).
- **Offset Tracking**: Maintain the exact last read event offset per partition per consumer group. Replay offsets must be deterministic per partition. Handler replay never masquerades as exactly-once external effects.
- **At-least-once delivery**: Ensure events are processed at least once, assuming consumer callbacks are idempotent.
- **Bounded Queues**: Bounded subscriber queues must define block/drop/reject behavior for backpressure. Concurrent subscribe/unsubscribe, handler failure, cancellation and shutdown do not leak threads or silently lose promised deliveries.
- **Retry Queues**: Support retry mechanism for failed event processing.
- **Dead-letter topics**: Events that fail repeatedly go to a dead-letter topic.

## Non-Functional Requirements
- **In-Memory**: Operates entirely in memory.
- **Concurrency**: Thread-safe operations using standard library constructs.
- **Performance**: High throughput and low latency.
- **Version Compatibility**: Implementations across v1-basic, v2-extended, and v3-optimized APIs with deterministic fixture inputs/expected outputs. No production/security promise is inferred.
