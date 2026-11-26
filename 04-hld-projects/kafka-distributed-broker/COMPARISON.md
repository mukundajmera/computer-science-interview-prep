# Comparison: Distributed Partitioned Commit Log Broker

| Feature | Log-centric (Kafka/Pulsar) | Message Queue (RabbitMQ/ActiveMQ) |
|---|---|---|
| **Storage Model** | Append-only partitioned logs | Transient queue storage |
| **Consumer Tracking** | Offset-based (Consumer tracks) | Acknowledgment-based (Broker tracks) |
| **Delivery Model** | Pull (Consumer polls) | Push (Broker pushes) |
| **Durability** | Persistent by default | Optional, often transient |
| **Scalability** | Horizontal via partitions | Vertical or limited clustering |
| **Replayability** | Native (change offset) | Difficult or impossible |
