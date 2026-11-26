# Code Walkthrough: Distributed Message Queue

## Supported Versions and Feature Deltas

The system evolves through three iterative versions, maintaining backward compatibility on core operations while adding advanced semantics:

1. **v1-basic:** Introduces the fundamental `MessageQueueBroker`, `Topic`, `Partition`, `Producer`, and `ConsumerGroup` classes. Implements simple publish-subscribe semantics with round-robin partitioning and basic polling.
2. **v2-extended:** Adds Consumer Group balancing where partitions are exclusively assigned to consumers in a group. Introduces offset tracking (commit, ack, nack).
3. **v3-optimized:** Introduces `SubscriberDAG` for dependency-based processing order, regex-based topic subscriptions, and robust `RetryPolicy` with a Dead Letter Queue (DLQ).

## Public APIs

The core interaction revolves around `MessageQueueBroker`, `Producer`, and `Consumer` (or consumer groups).
- `MessageQueueBroker.createTopic(name: str, partitions: int)`
- `Producer.send(topic: str, message: Message)`
- `Consumer.poll() -> List[Message]`
- `Consumer.ack(message: Message)`
- `Consumer.nack(message: Message)`

## Execution Flow Analysis and Reference Contracts

This walkthrough details the core write and read paths, explicitly highlighting normal operations and failure modes.

### 1. Normal Use-Case (Publishing and Polling)
In a healthy scenario, a producer sends messages, and consumers poll them based on their assignments. 

**Java 11+ Implementation:**
```java
import v3_optimized.*;
import java.util.List;

MessageQueueBroker broker = new MessageQueueBroker();
broker.createTopic("transactions", 2);

Producer producer = new Producer(broker);
producer.send("transactions", new Message("t1", "data1"));
producer.send("transactions", new Message("t2", "data2"));

Consumer c1 = new Consumer(broker, "groupA", "transactions");
List<Message> msgs = c1.poll();
for (Message m : msgs) {
    System.out.println("Processing: " + m.getId());
    c1.ack(m);
}
```

**Python 3.8+ Implementation:**
```python
from v3_optimized.broker import MessageQueueBroker
from v3_optimized.producer import Producer
from v3_optimized.consumer import Consumer
from v3_optimized.message import Message

broker = MessageQueueBroker()
broker.create_topic("transactions", 2)

producer = Producer(broker)
producer.send("transactions", Message("t1", "data1"))
producer.send("transactions", Message("t2", "data2"))

c1 = Consumer(broker, "groupA", "transactions")
msgs = c1.poll()
for m in msgs:
    print(f"Processing: {m.id}")
    c1.ack(m)
```

### 2. Empty/Invalid Input
The system handles empty queues gracefully by returning empty lists, and invalid topics throw precise exceptions.

**Java 11+ Contract:**
```java
// Empty queue
Consumer c1 = new Consumer(broker, "groupA", "transactions");
List<Message> emptyList = c1.poll(); 
assert emptyList.isEmpty(); // No blocking

// Invalid topic
try {
    producer.send("non_existent", new Message("id", "payload"));
} catch (IllegalArgumentException e) {
    // Expected: Topic does not exist: non_existent
}
```

**Python 3.8+ Contract:**
```python
# Empty queue
c1 = Consumer(broker, "groupA", "transactions")
empty_list = c1.poll()
assert len(empty_list) == 0 # Non-blocking read

# Invalid topic
try:
    producer.send("non_existent", Message("id", "payload"))
except ValueError as e:
    pass # Expected: Topic does not exist
```

### 3. Duplicate Operation (Duplicate Acks)
If a consumer sends an acknowledgment for an already acknowledged or non-inflight message, it acts idempotently without throwing errors.

**Java 11+ Contract:**
```java
Message m = new Message("m1", "data");
producer.send("topic", m);
List<Message> polled = c1.poll();
c1.ack(polled.get(0));

// Duplicate ack has no effect and doesn't crash
c1.ack(polled.get(0)); 
```

**Python 3.8+ Contract:**
```python
producer.send("topic", Message("m1", "data"))
polled = c1.poll()
c1.ack(polled[0])

# Idempotent duplicate ack
c1.ack(polled[0])
```

### 4. Capacity Boundary (Partition-to-Consumer Limits)
The number of active consumers in a group cannot exceed the total number of partitions assigned to that group. Additional consumers will sit idle (starvation) unless partitions are added.

**Java 11+ Contract:**
```java
broker.createTopic("topicA", 1); // Only 1 partition
Consumer c1 = new Consumer(broker, "groupX", "topicA");
Consumer c2 = new Consumer(broker, "groupX", "topicA");

producer.send("topicA", new Message("m1", "data"));
// c1 gets assigned partition 0
assert c1.poll().size() == 1;
// c2 gets no partitions
assert c2.poll().size() == 0; 
```

**Python 3.8+ Contract:**
```python
broker.create_topic("topicA", 1)
c1 = Consumer(broker, "groupX", "topicA")
c2 = Consumer(broker, "groupX", "topicA")

producer.send("topicA", Message("m1", "data"))
# Only one consumer gets the single partition
assert len(c1.poll()) == 1
assert len(c2.poll()) == 0
```

### 5. One Failure Rollback (RetryPolicy and DLQ)
In `v3-optimized`, when message processing fails continuously, the system rolls back the processing attempt and redirects the message to a Dead Letter Queue (DLQ).

**Java 11+ Contract:**
```java
import v3_optimized.RetryPolicy;

RetryPolicy policy = new RetryPolicy(2, 10, 100, 2.0); // max 2 retries
Message badMessage = new Message("err1", "bad_data");

boolean success = policy.execute(() -> {
    throw new RuntimeException("DB offline");
}, badMessage);

assert !success; // Action failed after retries
assert policy.getDeadLetterQueue().size() == 1; // Rolled back to DLQ
assert policy.getDeadLetterQueue().get(0).getId().equals("err1");
```

**Python 3.8+ Contract:**
```python
from v3_optimized.retry_policy import RetryPolicy

policy = RetryPolicy(max_retries=2, initial_backoff_millis=10)
bad_message = Message("err1", "bad_data")

def failing_action():
    raise ValueError("DB offline")

success = policy.execute(failing_action, bad_message)

assert not success
assert len(policy.dead_letter_queue) == 1
assert policy.dead_letter_queue[0].id == "err1"
```

## Concurrency Control
Concurrency is handled at the partition level. Each `PartitionManager` (or `Partition`) has a dedicated lock (e.g., `ReadWriteLock` in Java, `threading.RLock` in Python). Because writes are sequentially appended to a file, lock contention is minimal.
