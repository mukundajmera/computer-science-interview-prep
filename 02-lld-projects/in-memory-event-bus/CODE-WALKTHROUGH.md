# In-Memory Event Bus - Code Walkthrough

## Interview Pacing (45 minutes)
- **0-10m: Requirements & Design**: Define topics, partitions, consumer groups. Clarify assumptions on concurrency and in-memory constraints.
- **10-25m: Core Implementation (v1 & v2)**: Implement topic creation, partitioning, pub-sub/point-to-point via consumer groups, and thread-safe appending (`ReentrantReadWriteLock` / `threading.Lock`).
- **25-35m: Advanced Features (v3)**: Implement retry logic and dead-letter queues (DLQ).
- **35-45m: Review & Edge Cases**: Discuss correctness invariants, concurrency bottlenecks, and testing strategies.

## Version Progression Table
| Version | Focus | Key Components | Complexity |
| --- | --- | --- | --- |
| `v1-basic` | Pub-Sub | `EventBus`, basic `Topic` | O(1) pub/sub |
| `v2-extended` | Partitions, Consumer Groups | `Partition`, `ReadWriteLock`, Offset Tracking | O(1) publish, O(1) poll |
| `v3-optimized` | Retries, DLQ | Retry Queues, DLQ, Max Retries | O(1) amortized |

## Entry APIs
- `createTopic(name, numPartitions)`
- `publish(topicName, event, partitionKey)`
- `subscribe(group, topicName)`
- `poll(group, topicName, partitionId)`
- `commitOffset(group, topicName, partitionId, offset)`
- `failEvent(group, topicName, event)`

## Correctness Invariants
- **Thread Safety**: Appends to partitions must be atomic and prevent race conditions.
- **Offset Consistency**: Committing offsets must monotonically increase and be safely tracked per consumer group per partition.
- **Message Durability (In-Memory)**: Events in a partition are immutable and never deleted (within memory bounds).

## Flow
1. Publisher calls `publish()`. Event is routed to a `Partition` using modulo math on `partitionKey`.
2. `Partition.append()` securely adds the event under a write lock.
3. Consumer calls `poll()`. EventBus checks retry queues first. If empty, reads the next offset from the `Partition` under a read lock.
4. If successful, consumer calls `commitOffset()`. If failed, calls `failEvent()` which handles retries and DLQ routing.
