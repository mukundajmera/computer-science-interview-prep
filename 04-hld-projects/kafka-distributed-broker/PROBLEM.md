# Problem Statement: Distributed Partitioned Commit Log Broker

Design a distributed, partitioned, replicated commit log service (similar to Apache Kafka or Apache Pulsar). The system will serve as the central nervous system for asynchronous event-driven architectures, decoupling data production from data consumption across many downstream applications.

## Core Requirements

1. **High Ingress Rate:** Handle massive continuous data streams (5M events/sec ingress).
2. **Low Latency Delivery:** Provide millisecond end-to-end pub-to-sub latency for real-time consumers.
3. **Durable Storage:** Ensure events are persisted durably to disk and protected against single-node failures.
4. **Scalability:** Horizontally partitionable topics across many broker nodes to scale throughput beyond a single machine's capacity.
5. **Fault Tolerance:** Robustness against broker crashes and network partitions without data loss or prolonged unavailability.

## Usage Patterns

- Producers publish events in high volumes, often in micro-batches.
- Multiple independent consumer applications need to read the same streams at their own pace.
- Some consumers require strict ordering guarantees at the partition level.
- Consumers may crash and need to resume processing from their last committed checkpoint without missing events.

## Scale Target Considerations

- Thousands of topics, tens of thousands of partitions.
- Petabytes of retained historical data.
- 5M messages per second peak ingress rate.
- Read heavy: Each message might be read by 5-10 different consumer groups.
