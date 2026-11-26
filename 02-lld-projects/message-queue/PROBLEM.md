# In-Memory Message Queue - Problem Statement

## Functional Requirements
- **Topics**: Support publishing messages to specific topics.
- **Partitions**: Each topic can have multiple partitions for parallel processing.
- **Producers**: Publish messages to topics. They can optionally specify a partition.
- **Consumer Groups**: Consumers belong to consumer groups. A consumer group allows distributing messages among consumers (point-to-point) or broadcasting (pub-sub).
- **Per-Group Offset Tracking**: Maintain the last read message offset per partition per consumer group.
- **Regex Subscription**: Consumers/groups can subscribe to topics matching a regex pattern.
- **Subscriber Dependency DAG**: Order message delivery or processing among subscribers based on a dependency DAG.
- **Retry Policy & DLQ**: Configurable retry policies with dead letter queues for failed message processing.

## Non-Functional Requirements
- **In-Memory**: The queue operates entirely in memory.
- **Concurrency**: Thread-safe operations for concurrent producers and consumers.
- **Performance**: High throughput and low latency.
- **Extensibility**: Easy to add new retry policies, routing strategies, etc.

## Constraints
- Memory is finite, but we assume it's sufficient for the lifetime of the application run.
- Real-time persistence is out of scope (can be added as follow-up).

## Clarifying Questions
- Q: What happens if a consumer fails to process a message?
  A: It goes into a retry mechanism and eventually to a DLQ.
- Q: How is partition assignment handled?
  A: For simplicity, a round-robin or hash-based routing is used.
- Q: What does Subscriber Dependency DAG mean?
  A: Certain subscribers (or consumer groups) must process a message before others can.

## Core Entities
- Message, Topic, Partition, Producer, Consumer, ConsumerGroup, Broker, SubscriberDAG.
