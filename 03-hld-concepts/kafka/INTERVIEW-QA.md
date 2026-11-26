# Interview Questions: Kafka

## Basic Concepts and Capabilities

### 1. What core problem does Kafka solve in distributed systems?
**Q**: Why would a system architecture introduce Kafka instead of relying on traditional synchronous communication protocols like REST or gRPC?
**A**: Kafka provides a highly durable, scalable asynchronous event streaming platform that fundamentally decouples producers from consumers. By acting as a massive buffer, it prevents fragile downstream services from being overwhelmed during traffic bursts.

### 2. Topic vs. Partition
**Q**: What is the structural relationship between a Kafka topic and a partition?
**A**: A topic is a logical grouping. A partition is the physical, ordered, append-only log file residing on a broker's disk. Partitions allow horizontal scalability.

### 3. Offsets and Replayability
**Q**: What is an offset, how is it managed, and what capability does it unlock?
**A**: An offset is an immutable integer that uniquely identifies a record's position in a partition. It unlocks replayability, allowing consumers to rewind and reprocess historical data.

## Consumer and Producer Dynamics

### 4. Consumer Groups and Scalability Limits
**Q**: If a topic has 4 partitions and a consumer group has 6 consumers, what happens?
**A**: A partition can only be assigned to a maximum of one consumer in a group. 4 consumers will be active, and 2 will sit idle as hot standbys.

### 5. Idempotency and Deduplication
**Q**: Why is idempotent consumer design considered mandatory?
**A**: Kafka guarantees "at-least-once" delivery by default. Downstream systems must be idempotent to handle duplicate deliveries gracefully without data corruption.

### 6. Partition Key Strategy and Skew
**Q**: How do you determine an effective partition key, and what are the consequences of choosing a poor key?
**A**: A partition key guarantees ordering per key. A poor key creates data skew, overwhelming one broker and defeating horizontal scaling.

### 7. Batching and Latency vs. Throughput
**Q**: How do batching settings like `linger.ms` affect performance?
**A**: `linger.ms` introduces a small artificial delay, allowing the producer to batch multiple records into a single request, significantly increasing throughput at the cost of slight latency.

### 8. Consumer Fetch Mechanics
**Q**: How does a consumer pull data from a broker?
**A**: Consumers actively poll the broker for data in batches, rather than the broker pushing it. This avoids overwhelming the consumer.

## Advanced Architecture & Internals

### 9. Zero-Copy Data Transfer and OS Optimizations
**Q**: How does Kafka achieve high-throughput data transfer?
**A**: Kafka uses the `sendfile()` system call (Zero-Copy) to transfer data directly from the OS Page Cache to the network socket, bypassing the JVM heap and user space entirely.

### 10. Log Segments, Tombstones, and Compaction
**Q**: Explain log compaction and its use case.
**A**: Log compaction retains only the latest value for a specific key. Tombstones (null payload) are used to delete a key entirely during a compaction cycle.

### 11. Replication, Fault Tolerance, and the ISR
**Q**: What is the In-Sync Replicas (ISR) list and how does it relate to the High Watermark?
**A**: The ISR includes the leader and followers that are fully caught up. The High Watermark is the highest offset replicated to all ISR members, which is the maximum offset a consumer can read.

### 12. Producer Acknowledgment Semantics (`acks`)
**Q**: Explain the difference between `acks=1` and `acks=all` with `min.insync.replicas`.
**A**: `acks=1` only waits for the leader. `acks=all` waits for all ISR members. `min.insync.replicas` dictates the absolute minimum number of replicas that must acknowledge an `acks=all` request to prevent data loss.

### 13. Unclean Leader Election
**Q**: What is unclean leader election and its trade-offs?
**A**: It allows a follower not in the ISR to become the leader if all ISR members fail. It prioritizes availability over consistency, resulting in definitive data loss.

## Operational and Troubleshooting

### 14. Managing Consumer Lag
**Q**: What is consumer lag and how do you monitor it?
**A**: Lag is the difference between the partition's High Watermark and the consumer's committed offset. You monitor it via metrics and scale consumer groups to reduce it.

### 15. The "Poison Pill" Problem
**Q**: How do you handle poison pill messages that consistently fail processing?
**A**: Implement a Dead Letter Queue (DLQ). After N retries, the consumer forwards the failing message to a separate DLQ topic and commits the offset to move forward.

### 16. KRaft vs. ZooKeeper
**Q**: Why is Kafka migrating away from ZooKeeper to KRaft?
**A**: KRaft (Kafka Raft) manages metadata internally using a Raft quorum, simplifying deployment, improving scalability, and providing much faster controller failover.

### 17. Cooperative Sticky Rebalance Protocol
**Q**: How does cooperative rebalancing improve over eager rebalancing?
**A**: Eager rebalancing revokes all partitions globally (stop-the-world). Cooperative rebalancing only revokes partitions that must move, allowing unaffected consumers to continue processing.

### 18. Tiered Storage and Infinite Retention
**Q**: How does Tiered Storage alter cluster economics?
**A**: It offloads older log segments from expensive local broker disks to cheaper object storage (like S3), allowing for massive historical retention while decoupling compute from storage.
