# Message Queues and Streaming Quiz

22 questions focused on relevant concepts.

Time: 20 minutes
Difficulty: Medium

---

## Section 1: Core Concepts (22)

### Question 1
In Apache Kafka, what is the primary unit of parallelism and scale?

A) The Partition
B) The Consumer Group
C) The Topic
D) The Broker

### Question 2
What happens if a Consumer Group has more consumers than the number of partitions in the subscribed Kafka topic?

A) Kafka will automatically create new partitions to accommodate the consumers.
B) The consumer group will rebalance, causing the topic to temporarily go offline.
C) The excess consumers will read duplicate messages to increase throughput.
D) The excess consumers will remain idle and receive no messages.

### Question 3
How does Kafka achieve 'Exactly-Once Semantics' (EOS) for stream processing?

A) By forcing consumers to use a distributed lock before reading any message.
B) By using a combination of idempotent producers and transactional commits across partitions.
C) By ensuring network packets are never dropped between the producer and the broker.
D) By keeping all messages in memory and never flushing them to disk.

### Question 4
What is the primary difference between RabbitMQ (AMQP) and Apache Kafka?

A) RabbitMQ is designed for high-throughput analytics, while Kafka is designed for complex routing.
B) RabbitMQ pushes messages to consumers and deletes them when acknowledged; Kafka consumers pull messages from a persistent log.
C) RabbitMQ only supports exactly-once semantics, whereas Kafka only supports at-most-once.
D) RabbitMQ is a distributed append-only log, while Kafka is a traditional message queue.

### Question 5
In Kafka, what is 'Log Compaction'?

A) Deleting the oldest messages when the topic exceeds its maximum storage limit.
B) Merging multiple small partitions into one large partition.
C) Retaining only the most recent value for each specific message key, discarding older versions.
D) Compressing the network traffic between brokers using GZIP.

### Question 6
What does an 'Offset' represent in Kafka?

A) The time difference between when a message was produced and consumed.
B) A sequential ID number identifying a record's position within a partition.
C) The physical memory address of a message on the broker.
D) The difference in byte size between the compressed and uncompressed message.

### Question 7
If a Kafka consumer fails mid-processing and restarts, how does it know where to resume?

A) It automatically starts from the very beginning of the topic (offset 0).
B) It retrieves its last committed offset from a special internal Kafka topic (`__consumer_offsets`).
C) It asks the producer to resend the last batch of messages.
D) It queries a centralized database where all consumers manually store their state.

### Question 8
In RabbitMQ, what is the role of an 'Exchange'?

A) It is the disk storage layer where messages are persisted.
B) It handles the authentication and authorization of clients.
C) It routes messages to one or more queues based on routing keys and binding rules.
D) It is a background process that deletes unacknowledged messages.

### Question 9
What happens in a 'Fanout' exchange in RabbitMQ?

A) The message is discarded if no consumer is currently active.
B) The message is routed based on a pattern match (e.g., `*.logs.*`).
C) The message is routed to exactly one queue based on a strict string match.
D) The message is duplicated and sent to every queue bound to that exchange, ignoring routing keys.

### Question 10
What is 'Consumer Lag' in a message streaming system?

A) The time it takes for a message to be serialized before sending.
B) The difference between the latest offset written to the partition and the latest offset committed by the consumer.
C) The network latency between the broker and the consumer.
D) The penalty applied by the broker when a consumer reads too fast.

### Question 11
If you need strict, global ordering of all messages in a Kafka topic, how must you configure it?

A) By assigning a unique key to every single message.
B) By using an idempotent producer.
C) By setting the topic to have exactly 1 partition.
D) By enabling exactly-once semantics (EOS).

### Question 12
In Kafka, how is a message routed to a specific partition by default when a key is provided?

A) By hashing the key and calculating `hash(key) % number_of_partitions`.
B) By querying the consumer group to find the least busy consumer.
C) By randomly selecting a partition using a Round-Robin algorithm.
D) By checking the payload size and routing to the partition with the most disk space.

### Question 13
What is a 'Dead Letter Queue' (DLQ)?

A) A temporary queue that holds messages while the primary queue is rebalancing.
B) A queue that only stores messages without a routing key.
C) A queue used specifically for shutting down the broker gracefully.
D) A special queue where messages are routed if they cannot be processed successfully after multiple retries.

### Question 14
Why might a Kafka consumer experience an 'auto-commit' data loss scenario?

A) If the consumer group contains an odd number of consumers.
B) If the broker disk fills up completely.
C) If `enable.auto.commit=true` and the consumer process crashes after fetching messages but before finishing processing them.
D) If the producer forgets to assign a key to the message.

### Question 15
In the context of streaming, what is 'Backpressure'?

A) The physical pressure exerted on server fans during high CPU utilization.
B) When a consumer reads messages from the future.
C) The process of compressing old log files in Kafka.
D) A mechanism where a slow consumer signals the producer or broker to slow down to prevent overwhelming the consumer's memory.

### Question 16
Which system is typically better suited for implementing a complex, conditional task routing system (like a state machine for order processing)?

A) HDFS
B) Memcached
C) RabbitMQ
D) Apache Kafka

### Question 17
What is 'At-Least-Once' delivery semantics?

A) The system guarantees the message will be delivered, but it might be delivered multiple times in failure scenarios.
B) The system sends the message once, and if it fails, it is dropped forever.
C) The system guarantees the message will be delivered at least one minute after it was produced.
D) The system guarantees the message will be delivered exactly one time, never duplicated.

### Question 18
How does Kafka handle message deletion?

A) Messages are deleted in bulk (segment files) based on a configured time retention policy (e.g., 7 days) or size limit.
B) Messages are deleted only when explicitly requested by an admin API call.
C) Messages are deleted individually immediately after a consumer acknowledges them.
D) Messages are never deleted under any circumstances.

### Question 19
What does a Kafka 'Broker' do?

A) It is a protocol translator that converts AMQP messages to Kafka messages.
B) It is a specialized client application that reads from Kafka and writes to a database.
C) It is the central UI dashboard used to monitor the Kafka cluster.
D) It acts as a single server node within a Kafka cluster, responsible for storing partitions and handling read/write requests.

### Question 20
If you have a Kafka topic with 10 partitions and a Consumer Group with 15 consumers, how many consumers will actively receive messages?

A) 10
B) 5
C) 15
D) 0

### Question 21
What happens to a message in Kafka when its payload size exceeds the maximum configured limit (`message.max.bytes`) on the broker?

A) The broker automatically chunks the message into smaller segments and distributes them across multiple partitions.
B) The broker rejects the payload, and the producer client receives a `RecordTooLargeException` without appending the message to the log.
C) The broker forcefully applies gzip compression to the payload to reduce its size below the limit before writing it to disk.
D) The broker writes the payload to a native external blob store and stores only a reference pointer in the partition log.

### Question 22
Which of the following best describes how consumer groups function in a publish-subscribe message queue system like Kafka?

A) A consumer group receives a dedicated copy of every message published to a topic, allowing multiple independent systems to process the identical feed of events.
B) Consumer groups are used to increase the durability of a topic by writing messages to multiple disjoint disks concurrently.
C) Within a single consumer group, multiple consumers process the exact same messages to provide redundancy in case of processing failure.
D) A consumer group is a configuration that forces the message broker to convert unstructured text streams into strongly typed events before delivery.
