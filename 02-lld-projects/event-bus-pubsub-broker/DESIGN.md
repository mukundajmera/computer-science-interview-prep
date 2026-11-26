# Design: Event Bus / Pub-Sub Broker (Kafka Lite)

## Architecture Overview
The system models a lightweight, in-memory publish-subscribe messaging broker. The primary goal is to decouple the producers (who generate data) from the consumers (who process data).

## Core Components
1. **Message / Event**: The fundamental unit of data being transmitted. Contains an ID, payload, optional key, and metadata (timestamp).
2. **Topic**: A logical channel or category to which messages are published. A topic can be split into multiple **Partitions** to enable parallel processing and ordering guarantees per partition.
3. **Producer**: An entity that publishes messages to a topic.
4. **Consumer**: An entity that subscribes to topics to receive messages.
5. **Consumer Group**: A group of consumers that cooperate to consume messages from a topic. Each message in a topic is delivered to exactly one consumer instance within a subscribing consumer group.
6. **Broker / Event Bus**: The central mediator that receives messages from producers, stores them temporarily, and routes them to appropriate consumers.

## Architectural Patterns Used

### 1. Observer Pattern
- **Usage**: The core Pub-Sub mechanism.
- **Role**: Consumers (Observers) subscribe to Topics (Observables). When a Producer publishes a Message to a Topic, the Broker notifies the subscribed Consumers.

### 2. Mediator Pattern
- **Usage**: The Broker itself.
- **Role**: Producers and Consumers do not interact directly. They communicate exclusively through the Broker. This centralizes routing, storage, and consumer group logic, reducing coupling between components.

### 3. Producer-Consumer Pattern
- **Usage**: Inside the Broker handling partitions.
- **Role**: Producers push data into queues (partitions), and consumers pull (or are pushed) data from these queues. This helps in buffering and managing rate mismatches between publishing and consuming.

### 4. Strategy Pattern
- **Usage**: Partitioning logic and Delivery policies.
- **Role**: 
  - **Partitioning Strategy**: Determines which partition a message goes to (e.g., RoundRobin, HashKey).
  - **Delivery Strategy**: Determines how messages are dispatched (e.g., At-Most-Once, At-Least-Once).

## High-Level Workflow
1. A **Topic** is created with a specified number of partitions.
2. **Consumers** subscribe to the Topic, optionally specifying a **Consumer Group**.
3. A **Producer** publishes a Message to the Topic.
4. The Broker uses a **Partitioning Strategy** to assign the message to a specific Partition.
5. The Broker enqueues the message in the chosen Partition.
6. The Broker identifies all subscribed Consumer Groups for the Topic.
7. For each Consumer Group, the Broker dispatches the message to *one* Consumer (e.g., using round-robin among active consumers in the group). If a Consumer is not in a group, it acts as its own group and receives a copy of the message.

## Thread Safety and Concurrency
Since this is an in-memory broker, it must handle concurrent access:
- **Publishing**: Multiple producers might publish to the same topic simultaneously. The partitions (queues) must be thread-safe (e.g., using `ConcurrentLinkedQueue` or `BlockingQueue` in Java, or `queue.Queue` in Python).
- **Consuming**: Dispatching messages must not block producers. A thread pool or executor service can be used for asynchronous message dispatching.
- **State Management**: Modifying topics and subscriptions requires thread-safe collections (e.g., `ConcurrentHashMap`).
