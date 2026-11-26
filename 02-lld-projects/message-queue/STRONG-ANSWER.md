# Strong Answer: Message Queue

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Message Queue, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

By clarifying upfront, we frame the design around deterministic logic and strict state transitions. The functional requirements define a system that accepts publications and accurately resolves message state per consumer group, while non-functional requirements push us to optimize thread safety and handle concurrency for a multi-partition broker environment.

## 2. Entity Modeling & Core Components (15 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."

- **`Topic`**: Encapsulates the N partitions, serving as the logical container for broadcasted messages.
- **`Partition`**: Acts as a thread-safe circular buffer or append-only queue (e.g., `ConcurrentLinkedQueue` or standard lists with locks).
- **`Message`**: The fundamental payload unit.
- **`ConsumerGroup`**: Manages the offset tracking for a cluster of workers using offset maps (`committed_offsets`, `read_offsets`) and orchestrates `ack`/`nack`.
- **`MessageQueueBroker`**: The central orchestrator managing topics, publishers, and the `SubscriberDAG` to resolve cross-group consumption ordering.
- **`SubscriberDAG`**: Evaluates consumer dependency graphs before delivering messages to blocked consumer groups.

## 3. APIs and Version Deltas (10 mins)
**Say:** "Our public API centers around the `MessageQueueBroker` and `ConsumerGroup` classes orchestrating the interaction:
- `MessageQueueBroker.publish(topic_name, message)`: Validates the topic, appends the message, and updates subscribers.
- `ConsumerGroup.read_message(topic, partition, dag)`: Resolves redelivery offsets or blocks if dependent groups haven't acked.

As the implementation evolves through versions, feature deltas emerge:
- **v1-basic**: Implements the core broker, in-memory partition, and naive publisher/consumer matching without DAG dependency logic.
- **v2-extended**: Introduces Regex subscriptions, tracking consumer groups, and naive retry limits.
- **v3-optimized**: Introduces a sophisticated `SubscriberDAG` for dependent queue routing, robust `RetryPolicy` capturing Dead Letter Queues (DLQ), and robust thread locks managing consumer load balancing across multi-partitions."

To maintain clarity, our public APIs and version-specific feature deltas are heavily documented. To prevent regression, our focused test suite strictly targets this specific version's isolated components rather than silently importing standard code from the earlier v1 baseline.

## 4. Normal Use-Cases and Edge Cases (10 mins)
**Say:** "Let's trace the execution lifecycle and failure handling:
- **Normal Play**: A producer submits `publish("orders", msg)`. The `MessageQueueBroker` locks the topic, appends to the target `Partition`, and resolves. A `ConsumerGroup` polls, checks the `SubscriberDAG` to ensure it's eligible, consumes the message, and calls `ack()`, bumping the committed offset.
- **Empty/Invalid Input**: If a consumer submits an `ack` for an out-of-bounds offset or a topic that doesn't exist, the broker gracefully ignores it or throws a deterministic `ValueError` (Python) / `IllegalArgumentException` (Java) without corrupting offset maps. 
- **Duplicate Operation**: If a consumer group attempts to `ack` the exact same message offset twice, the broker's idempotency logic strictly evaluates `unacked_messages`. The second `ack` will act as a no-op since the offset is already committed, preserving identical state exactly once.
- **Capacity Boundary**: In **v3-optimized**, attempting infinite retries for a malformed poison message hits our bounded RetryPolicy limit (e.g., `max_retries = 2`). Instead of locking the partition infinitely, it hits the boundary and transitions into a Dead Letter Queue.
- **Failure Rollback**: If a consumer crashes mid-processing and fails to `ack` within the expected window, or explicitly issues a `nack()`, the offset is pushed into `redelivery_offsets`. The system rolls back the assumed success, removing it from `unacked_messages` and allowing the next poll to immediately serve the rolled-back offset before advancing."

### Code Verification
The following integration snippet (Python and Java equivalent) demonstrates how v3 enforces DAG dependencies and rolls back un-acked messages deterministically:

#### Python 3.8+ (Standard Library)
```python
def test_subscriber_dag_dependencies():
    broker = MessageQueueBroker()
    broker.create_topic("topic2", 1)
    
    dag = broker.get_dag("topic2")
    dag.add_dependency("groupA", "groupB") # groupB depends on groupA
    
    producer = Producer(broker)
    producer.send("topic2", Message("m1", "data"))
    
    cA = Consumer(broker, "groupA", "topic2")
    cB = Consumer(broker, "groupB", "topic2")
    
    # cB polls, but cannot read because cA hasn't acked
    msgs_B = cB.poll()
    assert len(msgs_B) == 0
    
    # cA polls and gets the message
    msgs_A = cA.poll()
    assert len(msgs_A) == 1
    assert msgs_A[0].id == "m1"
    
    # Still cB cannot read
    msgs_B = cB.poll()
    assert len(msgs_B) == 0
    
    # cA acks
    cA.ack(msgs_A[0])
    
    # Now cB can read
    msgs_B = cB.poll()
    assert len(msgs_B) == 1
    assert msgs_B[0].id == "m1"
```

#### Java 11+ (Standard Library)
```java
    @Test
    void testSubscriberDagDependencies() {
        MessageQueueBroker broker = new MessageQueueBroker();
        broker.createTopic("topic2", 1);
        
        SubscriberDAG dag = broker.getDag("topic2");
        dag.addDependency("groupA", "groupB"); // groupB depends on groupA
        
        Producer producer = new Producer(broker);
        producer.send("topic2", new Message("m1", "data"));
        
        Consumer cA = new Consumer(broker, "groupA", "topic2");
        Consumer cB = new Consumer(broker, "groupB", "topic2");
        
        List<Message> msgsB = cB.poll();
        assertEquals(0, msgsB.size());
        
        List<Message> msgsA = cA.poll();
        assertEquals(1, msgsA.size());
        assertEquals("m1", msgsA.get(0).getId());
        
        msgsB = cB.poll();
        assertEquals(0, msgsB.size());
        
        cA.ack(msgsA.get(0));
        
        msgsB = cB.poll();
        assertEquals(1, msgsB.size());
        assertEquals("m1", msgsB.get(0).getId());
    }
```

## 5. Production Trade-offs (5 mins)
**Say:** "In a real production environment, this in-memory or single-node design would require certain trade-offs and adaptations. An in-memory message queue provides sub-millisecond latency but is highly vulnerable to process crashes, risking total message loss. In production, we use append-only logs on disk (like Kafka) with multi-node replication, sacrificing minimal latency for maximum durability and avoiding JVM heap exhaustion."