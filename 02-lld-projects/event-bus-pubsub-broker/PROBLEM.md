# Problem Statement: Event Bus / Pub-Sub Broker (Kafka Lite)

## Objective
Design and implement an in-memory Event Bus / Publish-Subscribe Broker. The system should decouple message producers from message consumers using a topic-based messaging model.

## Functional Requirements
1. **Topic Management**: 
   - Create, list, and delete topics.
   - Topics should support multiple partitions for scalability.
2. **Publishing (Producers)**:
   - Publish messages to a specific topic.
   - Support publishing with keys to guarantee order within a partition.
3. **Subscribing (Consumers)**:
   - Subscribe to topics.
   - Support consumer groups where each message in a topic is delivered to only one consumer in a group (load balancing).
   - Support broadcast where multiple consumer groups each receive a copy of every message.
4. **Message Delivery**:
   - Deliver messages to active subscribers.
   - Ensure messages are not lost if consumers are temporarily unavailable (durability/retention, constrained by memory for this project).

## Non-Functional Requirements
1. **Concurrency and Thread Safety**:
   - The broker must handle concurrent publishing and consuming without race conditions or data corruption.
2. **Performance**:
   - High throughput and low latency for message routing.
3. **Extensibility**:
   - Easy to add new delivery guarantees, persistence mechanisms, or partitioning strategies.

## Example Use Cases
- A logging system where multiple services publish logs, and a single aggregator service consumes them to write to a database.
- A notification system where a user action triggers multiple distinct events (email notification, mobile push, in-app alert).
