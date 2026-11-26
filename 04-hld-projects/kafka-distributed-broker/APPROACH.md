# Approach: Distributed Partitioned Commit Log Broker

The core philosophy is to model messaging as a distributed, append-only commit log rather than a traditional queuing system (like RabbitMQ or ActiveMQ). This shifts the complexity of tracking read state from the broker to the consumer, enabling massive scale and decoupled processing.

## 1. Log-Centric Partitioned Storage

Topics are broken down into **partitions**. Each partition is an ordered, immutable sequence of messages that is continually appended to—a commit log. 

By partitioning topics, the broker cluster can distribute the storage and network load across multiple machines. A single topic is no longer bottlenecked by the CPU, memory, or disk I/O of a single server. Events within a partition are strictly ordered and assigned a sequential ID called an offset.

## 2. Pull vs Push Consumer Model

Traditional message queues often push data to consumers. A commit log broker uses a **pull-based model**. 

Consumers actively poll the broker for new messages. This design allows consumers to process messages at their maximum capacity without being overwhelmed. It also allows batching of reads to maximize throughput. If a consumer falls behind, it simply lags in its offset but doesn't cause backpressure on the broker or affect other consumer groups reading the same data.

## 3. Consensus-Backed Metadata

To maintain a coherent view of the cluster—knowing which broker holds which partition leader, which brokers are alive, and topic configurations—the system requires a strongly consistent metadata store.

Older architectures relied on external systems like **ZooKeeper**. Modern approaches integrate consensus directly into the broker cluster (e.g., **KRaft** in Apache Kafka) using algorithms like Raft. This eliminates the operational burden of a separate distributed system and improves cluster startup and failover times.
