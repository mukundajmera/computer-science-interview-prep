# In-Memory Event Bus - Design

## Architecture
- **EventBus**: Central manager for topics and routing.
- **Topic**: Contains one or more partitions.
- **Partition**: Thread-safe event store maintaining a deterministic, ordered sequence of events.
- **ConsumerGroup**: Tracks offsets per partition for its members.

## Class Diagram (Mermaid)
```mermaid
classDiagram
    class EventBus {
        +createTopic(name, partitions)
        +publish(topic, event)
        +subscribe(topic, group, callback)
        +unsubscribe(topic, group)
        +poll(group, topic)
    }
    class Topic {
        +publish(event)
    }
    class Partition {
        +append(event)
        +read(offset)
    }
    class ConsumerGroup {
        +commitOffset(partition, offset)
        +getOffset(partition)
    }
    EventBus "1" *-- "*" Topic
    EventBus "1" *-- "*" ConsumerGroup
    Topic "1" *-- "*" Partition
```

## Sequence Diagram
```mermaid
sequenceDiagram
    participant Publisher
    participant EventBus
    participant Consumer
    Publisher->>EventBus: publish(topic, event)
    EventBus-->>Publisher: ack
    Consumer->>EventBus: poll(topic, group)
    EventBus-->>Consumer: event
    Consumer->>EventBus: commitOffset(group, topic, partition, offset)
```

## Versioned Behavior Contracts
- **v1-basic**: Core `publish(topic, event)` and simple subscription. No advanced concurrency limits.
- **v2-extended**: Multi-partition, Consumer Groups (`commitOffset`).
- **v3-optimized**: Bounded queues (block/drop/reject on publish/poll), Retry/DLQ routing.
