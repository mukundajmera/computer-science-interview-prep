# In-Memory Message Queue - Design

## Architecture
- **MessageQueueBroker**: Central hub managing topics and consumer groups.
- **Topic**: Contains multiple partitions.
- **Partition**: Manages an ordered list of messages and handles concurrent appends.
- **Producer**: Sends messages to the broker.
- **ConsumerGroup**: Manages offsets for a group of consumers and coordinates partition reads.
- **Consumer**: Polls messages from the broker for its group.
- **SubscriberDAG**: Manages dependencies between consumer groups for a given topic.

## Class Diagram (Mermaid)
```mermaid
classDiagram
    class Broker {
        +createTopic(name, partitions)
        +publish(topic, message)
        +poll(group, topic)
    }
    class Topic {
        +publish(message)
    }
    class Partition {
        +append(message)
        +read(offset)
    }
    Broker "1" *-- "*" Topic
    Topic "1" *-- "*" Partition
```

## Sequence Diagram
```mermaid
sequenceDiagram
    participant Producer
    participant Broker
    participant Consumer
    Producer->>Broker: publish(topic, msg)
    Broker-->>Producer: ack
    Consumer->>Broker: poll(topic, group)
    Broker-->>Consumer: msg
    Consumer->>Broker: commitOffset(group, topic, partition, offset)
```
## Cross-links
- [PROBLEM.md](./PROBLEM.md)
- [APPROACH.md](./APPROACH.md)
