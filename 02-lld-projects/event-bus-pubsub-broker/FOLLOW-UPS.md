# Follow-Up Questions: Event Bus / Pub-Sub Broker

Once the core implementation is complete, interviewers often ask follow-up questions to test your system design thinking and understanding of trade-offs.

## 1. Handling Slow Consumers
**Question**: "What happens if a consumer goes offline for a day, or processes messages much slower than the producer creates them? How do we prevent Out Of Memory (OOM) errors?"
- **Discussion Points**:
  - **Bounded Queues**: Discuss implementing a max size for in-memory partitions.
  - **Eviction Policies**: When the queue is full, what is dropped? (Drop oldest, reject newest).
  - **Backpressure**: Can we signal to the producer to slow down?
  - **Spill to Disk**: Can we temporarily write overflow messages to disk?

## 2. Exactly-Once Delivery Guarantees
**Question**: "Currently, if the broker crashes right after a consumer processes a message but before the broker records it, the consumer might get it again upon restart. How do we achieve Exactly-Once semantics?"
- **Discussion Points**:
  - Explain that purely Exact-Once is technically impossible in distributed systems without cooperation from the consumer.
  - Explain **Idempotency**: The consumer must be designed to safely process duplicate messages (e.g., using a database with unique constraints on Message ID).
  - Discuss two-phase commits or transactional publishing.

## 3. Durability and Persistence
**Question**: "How would you change your design to ensure messages survive a broker restart?"
- **Discussion Points**:
  - Introduce a `StorageEngine` interface.
  - Implement a Write-Ahead Log (WAL). Before a message is acknowledged to the producer, it is appended to a file on disk.
  - Discuss the performance impact of disk I/O and how batching (grouping multiple messages into one disk write) mitigates this.

## 4. Distributed Broker (Scaling Out)
**Question**: "One machine is no longer enough. How do we scale this broker to run across 10 machines?"
- **Discussion Points**:
  - **Partitioning Across Nodes**: Different partitions of a topic live on different physical machines.
  - **Replication**: Partitions must be replicated to handle node failures.
  - **Coordination**: Need a consensus mechanism (like ZooKeeper or Raft) to manage cluster metadata, leader election for partitions, and track which consumers are reading which partitions.

## 5. Message Ordering
**Question**: "How do you guarantee strict ordering of messages?"
- **Discussion Points**:
  - Global ordering is too expensive. Ordering is guaranteed only *within a partition*.
  - Explain how a `HashPartitionStrategy` based on a message key (e.g., `UserId`) ensures all events for that user go to the same partition, and therefore the same consumer, maintaining order.
