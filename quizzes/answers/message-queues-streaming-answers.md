# Message Queues and Streaming Quiz - Answer Key

## Answers

## Question 1

1. **A** - The Partition

**Explanation:** The partition is the fundamental unit of scalability in Kafka. A topic is split into multiple partitions. Each partition can be hosted on a different broker, and each partition can be read by exactly one consumer within a consumer group, dictating the maximum parallel consumption.

Distractor breakdowns:
- B: Consumer groups define logical subscribers, but their parallelism is hard-capped by the number of partitions.
- C: A topic is a logical grouping; it cannot be scaled without increasing partitions.
- D: Adding brokers helps, but if a topic has only 1 partition, it cannot be processed in parallel regardless of broker count.

## Question 2

2. **D** - The excess consumers will remain idle and receive no messages.

**Explanation:** Kafka enforces a rule: a single partition can only be consumed by ONE consumer thread within a specific consumer group. Therefore, if you have 4 partitions and 5 consumers, 1 consumer will sit idle.

Distractor breakdowns:
- A: Kafka never automatically creates partitions based on consumer count.
- B: While a rebalance occurs when a consumer joins, the topic does not go offline, and the end result is still an idle consumer.
- C: Kafka prevents duplicate reading within the same group by design.

## Question 3

3. **B** - By using a combination of idempotent producers and transactional commits across partitions.

**Explanation:** EOS in Kafka is achieved by assigning a unique ID and sequence number to producers (idempotency, preventing duplicate writes) and allowing producers to wrap reads and writes to multiple partitions in a transaction.

Distractor breakdowns:
- A: Distributed locks would severely bottleneck performance and aren't how Kafka solves this.
- C: Network reliability is impossible to guarantee at the protocol level.
- D: Kafka's durability relies entirely on writing to disk.

## Question 4

4. **B** - RabbitMQ pushes messages to consumers and deletes them when acknowledged; Kafka consumers pull messages from a persistent log.

**Explanation:** RabbitMQ is a smart-broker / dumb-consumer model that pushes messages and tracks individual message acknowledgements, deleting them when processed. Kafka is a dumb-broker / smart-consumer model where messages are persisted to a log, and consumers pull data, tracking their own position (offset).

Distractor breakdowns:
- A: This is reversed. Kafka is for high-throughput; RabbitMQ excels at complex routing (exchanges).
- C: Neither statement regarding semantics is strictly true.
- D: This is reversed. Kafka is the log; RabbitMQ is the queue.

## Question 5

5. **C** - Retaining only the most recent value for each specific message key, discarding older versions.

**Explanation:** Log compaction ensures that Kafka retains at least the last known value for each message key within the log of data for a single topic partition. It's useful for restoring state (like a database table) where you only care about the latest update for a given ID, not the entire history of changes.

Distractor breakdowns:
- A: This is time-based or size-based retention policy, not compaction.
- B: Partitions cannot be merged.
- D: This is payload compression.

## Question 6

6. **B** - A sequential ID number identifying a record's position within a partition.

**Explanation:** An offset is a simple integer that represents the logical position of a message within a specific partition. Consumers track their progress by periodically committing the offset they have successfully processed.

Distractor breakdowns:
- A: This is consumer lag.
- C: Offsets are logical, not physical disk addresses.
- D: This is compression ratio.

## Question 7

7. **B** - It retrieves its last committed offset from a special internal Kafka topic (`__consumer_offsets`).

**Explanation:** Kafka uses an internal topic called `__consumer_offsets` to store the committed offsets for every consumer group. When a consumer restarts, it fetches its last committed offset from this topic and resumes reading from that point.

Distractor breakdowns:
- A: It resumes from the committed offset, not 0, unless configured to `auto.offset.reset=earliest` on first boot.
- C: Producers don't track consumer state.
- D: While possible historically (e.g., in ZooKeeper), modern Kafka manages this internally.

## Question 8

8. **C** - It routes messages to one or more queues based on routing keys and binding rules.

**Explanation:** Producers in RabbitMQ do not publish directly to queues; they publish to an Exchange. The Exchange uses rules (bindings and routing keys) to determine which queue(s) should receive the message (e.g., direct, topic, fanout).

Distractor breakdowns:
- A: Queues store the messages, not Exchanges.
- B: This is handled by the connection/vhost layer.
- D: This is a TTL or dead-letter policy.

## Question 9

9. **D** - The message is duplicated and sent to every queue bound to that exchange, ignoring routing keys.

**Explanation:** A Fanout exchange acts as a broadcast mechanism. It completely ignores any routing key provided by the producer and sends a copy of the message to all queues that are bound to it.

Distractor breakdowns:
- A: This depends on the 'mandatory' flag, not the exchange type.
- B: This describes a Topic exchange.
- C: This describes a Direct exchange.

## Question 10

10. **B** - The difference between the latest offset written to the partition and the latest offset committed by the consumer.

**Explanation:** Consumer lag is a crucial metric representing how far behind a consumer is. It is calculated as the 'Log End Offset' (latest message) minus the consumer's 'Current Offset'. High lag means the consumer cannot keep up with the producer rate.

Distractor breakdowns:
- A: This is serialization overhead.
- C: This is network latency.
- D: Brokers use backpressure or rate limiting, not a 'lag penalty'.

## Question 11

11. **C** - By setting the topic to have exactly 1 partition.

**Explanation:** Kafka only guarantees order *within a single partition*. If a topic has multiple partitions, messages across different partitions are consumed concurrently and out of global order. To guarantee global order, you must restrict the topic to 1 partition (sacrificing scalability).

Distractor breakdowns:
- A: Unique keys mean messages are hashed to *different* partitions, destroying global order.
- B: Idempotency prevents duplicates, it doesn't solve multi-partition ordering.
- D: EOS ensures no duplicates/loss, not global ordering.

## Question 12

12. **A** - By hashing the key and calculating `hash(key) % number_of_partitions`.

**Explanation:** When a key (like a User ID) is provided, the Kafka producer hashes the key to determine the partition. This ensures that all messages with the same key (e.g., all events for User A) always go to the same partition, guaranteeing their relative order.

Distractor breakdowns:
- B: Producers don't route based on consumer load.
- C: Round-Robin is used when *no key* is provided.
- D: Producers don't route based on broker disk space.

## Question 13

13. **D** - A special queue where messages are routed if they cannot be processed successfully after multiple retries.

**Explanation:** A DLQ is a safety net. If a consumer repeatedly fails to process a message (e.g., due to a malformed payload or a bug), instead of blocking the queue forever or dropping the message, it is moved to the DLQ for manual inspection and later reprocessing.

Distractor breakdowns:
- A: Messages stay in their original partition during rebalancing.
- B: This is unrelated to routing key presence.
- C: This is completely fabricated.

## Question 14

14. **C** - If `enable.auto.commit=true` and the consumer process crashes after fetching messages but before finishing processing them.

**Explanation:** With auto-commit enabled, the Kafka client library automatically commits offsets in the background at intervals, regardless of whether your application logic has finished processing the message. If a crash occurs after auto-commit but before processing finishes, the message is 'skipped' upon restart.

Distractor breakdowns:
- A: Even/odd consumer counts don't affect reliability.
- B: Disk full causes broker errors, not consumer offset skipping.
- D: Missing keys just mean Round-Robin routing.

## Question 15

15. **D** - A mechanism where a slow consumer signals the producer or broker to slow down to prevent overwhelming the consumer's memory.

**Explanation:** Backpressure is a flow-control concept. When a downstream system (consumer) cannot keep up with the upstream system (producer), backpressure mechanisms slow down the upstream system to prevent the downstream system from crashing due to memory exhaustion (OOM).

Distractor breakdowns:
- A: This is a hardware joke.
- B: Time travel is not a streaming concept.
- C: This is log compaction/retention.

## Question 16

16. **C** - RabbitMQ

**Explanation:** RabbitMQ excels at complex routing topologies using Exchanges (Direct, Topic, Headers) and individual message acknowledgements. It is designed for task queues. Kafka is designed for high-throughput, dumb-routing log streaming.

Distractor breakdowns:
- A: HDFS is a distributed file system.
- B: Memcached is a simple key-value cache.
- D: Kafka is a log; building complex individual message routing on it requires heavy stream processing frameworks.

## Question 17

17. **A** - The system guarantees the message will be delivered, but it might be delivered multiple times in failure scenarios.

**Explanation:** At-Least-Once means no messages are lost, but duplicates are possible. If a consumer processes a message but crashes before acknowledging/committing it, upon restart, it will read and process that same message again.

Distractor breakdowns:
- B: This is At-Most-Once (Fire and Forget) semantics.
- C: This is delayed/scheduled delivery.
- D: This is Exactly-Once semantics.

## Question 18

18. **A** - Messages are deleted in bulk (segment files) based on a configured time retention policy (e.g., 7 days) or size limit.

**Explanation:** Kafka is a log-based system. It does not track individual message state. Instead, it relies on retention policies (time or size). When a segment file on disk exceeds the retention limit, the entire file is deleted, regardless of whether consumers have read it.

Distractor breakdowns:
- B: While possible, it is not the primary mechanism.
- C: This is how RabbitMQ works.
- D: Kafka has retention policies to prevent disk full.

## Question 19

19. **D** - It acts as a single server node within a Kafka cluster, responsible for storing partitions and handling read/write requests.

**Explanation:** A broker is simply a single server process running the Kafka software. A Kafka cluster is made up of multiple brokers working together to store partitions and serve client requests.

Distractor breakdowns:
- A: This would be a bridge/proxy.
- B: This is a Kafka Connect Sink or a consumer app.
- C: This describes tools like Kafka Drop or Confluent Control Center.

## Question 20

20. **A** - 10

**Explanation:** Because a single partition can be assigned to a maximum of ONE consumer in a group, only 10 consumers can be assigned partitions. The remaining 5 consumers will sit idle as hot standbys.

Distractor breakdowns:
- B: This is the number of idle consumers.
- C: Violates the 1-partition-to-1-consumer rule.
- D: Consumers will read data if partitions are available.

## Question 21

21. **B** - The broker rejects the payload, and the producer client receives a `RecordTooLargeException` without appending the message to the log.

**Explanation:** Kafka enforces rigid payload size limits at the broker level to maintain predictable memory usage and disk performance. If a producer attempts to publish a message exceeding `message.max.bytes`, the broker explicitly rejects it, returning a `RecordTooLargeException`. The system does not natively support chunking, auto-compression on the broker (compression is handled on the producer), or automatic external storage.

Distractor breakdowns:
- A: Kafka does not natively support message chunking; large payload segmentation must be manually implemented within the application layer.
- C: Compression in Kafka is typically executed on the producer side before transmission. The broker does not forcefully compress rejected payloads to force them to fit.
- D: While the "Claim Check" pattern (storing payloads in S3 and passing references) is widely used for large messages, it is not a built-in broker feature.


## Question 22

22. **A** - A consumer group receives a dedicated copy of every message published to a topic, allowing multiple independent systems to process the identical feed of events.

**Explanation:** In systems like Kafka, each consumer group represents an independent logical subscriber. When multiple consumer groups subscribe to the same topic, each group receives its own copy of all messages. This allows different applications (e.g., an analytics engine and a billing service) to independently consume and track their own progress (offsets) through the same stream of events.

Distractor breakdowns:
- B: Consumer groups do not handle broker-side storage replication or disk durability; this is handled by topic replication factor and partition replica placement.
- C: Within a *single* consumer group, messages are load-balanced across the consumers (each partition is read by at most one consumer). They do not process the exact same messages for redundancy.
- D: Consumer groups relate to message routing and consumption tracking, not payload serialization or schema enforcement (which is often handled by Schema Registries or client libraries).
