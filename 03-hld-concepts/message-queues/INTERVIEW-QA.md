# Interview Questions: Message Queues

## Basic Questions

### 1. What is a message queue?
**Q**: What is a message queue and why is it used?

**A**: A message queue is middleware that enables asynchronous communication between system components by temporarily storing messages until they can be processed.

Key benefits:
- **Decoupling**: Producer and consumer don't need to be available simultaneously
- **Load leveling**: Handles traffic spikes by buffering messages
- **Reliability**: Messages persist even if consumer is temporarily down
- **Scalability**: Add more consumers to handle load

Example: Order service publishes "order created" event, multiple services (inventory, payment, notification) process it independently.

### 2. Point-to-Point vs Pub-Sub
**Q**: What's the difference between point-to-point and publish-subscribe messaging?

**A**: 
**Point-to-Point (Queue)**:
- Each message is routed to one consumer for processing (though retries may cause multiple delivery attempts)
- Multiple consumers compete for messages
- Use case: Task distribution, job processing

**Publish-Subscribe (Topic)**:
- Each message delivered to ALL subscribers
- Multiple consumers each get a copy
- Use case: Event broadcasting, notifications

Kafka's consumer groups combine both: within a group, one consumer gets each message; across groups, all get copies.

### 3. What are delivery guarantees?
**Q**: Explain the different message delivery guarantees.

**A**:
1. **At-most-once**: 
   - Message may be lost, never duplicated
   - Fire-and-forget, no retries
   - Use for: Metrics, non-critical logs

2. **At-least-once** (most common):
   - Message never lost, may be duplicated
   - Retry on failure, ACK after processing
   - Requires idempotent consumers

3. **Exactly-once (Effectively-Once)**:
   - "Exactly-once" delivery over a network is a myth; instead we use at-least-once attempts + idempotent effect contracts.
   - Requires handling duplicate IDs and payload mismatches.
   - Must state bounded retention limits for deduplication keys.
   - Use for: Financial transactions (via idempotency keys)

At-least-once with idempotent consumers is the sweet spot for most systems.

### 4. What is message acknowledgment?
**Q**: How does message acknowledgment work?

**A**: Acknowledgment (ACK) confirms successful message processing:

1. **Consumer receives message** (message still in queue, marked as in-flight)
2. **Consumer processes message**
3. **Consumer sends ACK** (message removed from queue)
4. **If no ACK within timeout**: Message requeued for retry

Types:
- **Auto-ACK**: ACK sent immediately on delivery (can lose messages)
- **Manual ACK**: Consumer explicitly confirms (safer)
- **NACK**: Consumer rejects, triggers requeue or DLQ

### 5. What is a Dead Letter Queue?
**Q**: What is a Dead Letter Queue (DLQ) and when is it used?

**A**: A DLQ is a queue that stores messages that fail processing repeatedly.

Flow:
```
Main Queue → Consumer → Fails
            ↓ (retry 1)
         → Consumer → Fails
            ↓ (retry 2)
         → Consumer → Fails
            ↓ (max retries exceeded)
         → Dead Letter Queue
```

Use cases:
- Messages with invalid format
- Processing exceptions
- Poison messages that crash consumers (requires quarantine to prevent infinite redrive loops)

Benefits & Redrive Requirements:
- Prevents stuck consumers
- Preserves failed messages for debugging
- Enables manual intervention
- **Redrive Identity**: Must retain logical event identity.
- **Validation**: Cannot silently bypass ACL/schema checks on redrive.
- **Bounded Attempts**: Strict limits to prevent looping.
- **Order Effects**: Must handle explicit order effects so stale redrives don't overwrite new data.
- **Retention Limits**: If bounded dedup retention limits expire, redrive can reset money side effects/repeat actions.

## Intermediate Questions

### 1. Kafka vs RabbitMQ
**Q**: When would you choose Kafka over RabbitMQ?

**A**:
**Choose Kafka when**:
- High throughput (millions of messages/second)
- Need message replay (log-based storage)
- Event sourcing/streaming
- Long retention (days/weeks)
- Already have Kafka ecosystem

**Choose RabbitMQ when**:
- Traditional message queue patterns
- Need very low latency
- Complex routing requirements
- Smaller scale
- Need priority queues

| Aspect | Kafka | RabbitMQ |
|--------|-------|----------|
| Throughput | Very high | High |
| Latency | ~ms | ~µs |
| Replay | Yes | No |
| Ordering | Per partition | No guarantee |
| Protocol | Custom | AMQP |

### 2. Handling Duplicate Messages
**Q**: How do you handle duplicate messages?

**A**: With at-least-once delivery, duplicates are inevitable. Solutions:

1. **Idempotent operations**:
   - Design operations to be safely repeated
   - e.g., SET instead of INCREMENT

2. **Deduplication with message ID**:
   ```python
   if message_id in processed_ids:
       return  # Skip duplicate
   process(message)
   processed_ids.add(message_id)
   ```

3. **Idempotency keys**:
   - Producer assigns unique key
   - Consumer tracks processed keys
   - Use Redis/DB for tracking

4. **Database constraints**:
   - Use unique constraints to prevent duplicate inserts

### 3. Message Ordering
**Q**: How do you ensure message ordering in a distributed queue?

**A**: Ordering is challenging with multiple partitions/consumers:

**Total ordering** (single partition):
- All messages in sequence
- Single consumer only
- Low throughput

**Partition ordering** (Kafka approach):
- Order guaranteed within partition only
- Use partition key (e.g., user_id)
- Related messages go to same partition

```
user_123's messages → Partition 0 → Consumer 1 (ordered)
user_456's messages → Partition 1 → Consumer 2 (ordered)
```

**Key insight**: Often, you only need order within an entity (user, order), not globally.

### 4. Consumer Lag
**Q**: What is consumer lag and how do you handle it?

**A**: Consumer lag is the number of messages waiting to be processed (difference between latest offset and consumer offset).

**Causes**:
- Slow consumers
- Traffic spike
- Consumer crashes

**Solutions**:
1. **Scale consumers**: Add more instances
2. **Increase partitions**: More parallelism
3. **Optimize processing**: Reduce per-message time
4. **Batch processing**: Process multiple messages together

**Monitoring**:
- Alert on lag thresholds
- Track lag trend (growing = problem)
- Kafka: `kafka-consumer-groups.sh --describe`

### 5. Backpressure Handling
**Q**: How do you handle backpressure when consumers can't keep up?

**A**: Backpressure occurs when producer rate exceeds consumer capacity.

**Strategies**:
1. **Buffering**: Queue absorbs spikes (temporary solution)

2. **Scaling**: Add more consumers dynamically

3. **Dropping**: Discard low-priority messages
   - Use message priority
   - Expire old messages

4. **Flow control**: Slow down producers
   - Return errors when queue full
   - Implement rate limiting

5. **Load shedding**: Reject some requests entirely

**Best practice**: Monitor queue depth and auto-scale consumers.

## Advanced Questions

### 1. Exactly-Once Semantics
**Q**: How would you implement exactly-once processing?

**A**: True "exactly-once" delivery is a myth for external systems. If a crash happens after an external payment API call but before the broker ACK, the message will be re-delivered, resulting in a duplicate effect.

We achieve **"effectively-once"** processing through at-least-once delivery + idempotent consumers.

**Producer side**:
- Assign unique message ID
- Kafka: Enable idempotent producer (handles broker transaction exactly-once, but not external effects)

**Consumer side**:
- **Offset/Effect Atomic Commit**: Update DB state and consumer offset in one transaction (if supported).
- **Durable Inbox/Outbox/Key Payload Binding**:
  - Open DB transaction.
  - Check/Insert message ID into **Inbox** table (deduplication).
  - Check for payload mismatches (reject if ID matches but payload differs).
  - Execute database mutation.
  - Insert downstream messages into **Outbox** table.
  - Commit DB transaction.
- **External Effects**: Must rely on the external system's idempotency key.

**Key constraints to mention**:
- Bounded retention limits on deduplication tables (e.g., if you only store keys for 7 days, older replays will bypass dedup).
- See [Idempotency](../idempotency/THEORY.md) and [Distributed Transactions (Saga/Outbox)](../distributed-transactions/THEORY.md) for detailed patterns.

### 2. Cross-Region Replication
**Q**: How would you design a globally distributed message queue?

**A**:
**Challenges**:
- Network latency between regions
- Ordering guarantees across regions
- Failover handling

**Approaches**:

1. **Active-Passive**:
   - Single primary region
   - Replicate to standby
   - Manual failover

2. **Active-Active**:
   - Producers in all regions
   - Aggregate to single topic
   - Complex conflict resolution

3. **Kafka MirrorMaker**:
   - Replicate topics between clusters
   - Eventually consistent

4. **Confluent Cluster Linking**:
   - Real-time replication
   - Offset preservation

**Considerations**:
- Accept higher latency for cross-region
- Design for eventual consistency
- Plan for split-brain scenarios

### 3. Event Sourcing with Queues
**Q**: How do you implement event sourcing with message queues?

**A**: Event sourcing stores state changes as a sequence of events:

```
User Events:
1. UserCreated {id: 123, email: "a@b.com"}
2. EmailChanged {id: 123, email: "new@b.com"}
3. Deactivated {id: 123}

Current State = replay(all events)
```

**With Kafka**:
- Topic per aggregate type
- Key = aggregate ID
- Log compaction for snapshots

**Benefits**:
- Complete audit trail
- Replay/rebuild state
- Event-driven integration

**Pattern**:
```
Command → Aggregate → Events → Kafka → Projections
                                    → Notifications
                                    → Analytics
```

## Common Follow-ups

- How do you monitor queue health?
- How do you handle poison messages?
- How do you do zero-downtime queue migrations?
- How do you test message-driven systems?
- How do you handle large messages (>1MB)?
- How do you implement priority queues?

## Red Flags to Avoid

1. **Ignoring idempotency**: At-least-once means duplicates
2. **Blocking in message handlers**: Use async processing
3. **No DLQ**: Lost messages with no investigation path
4. **Ignoring consumer lag**: Leads to data delays
5. **Tight coupling via message format**: Use schema registry
6. **No monitoring**: Can't see queue problems

## How to Explain in 30 Seconds

"Message queues enable asynchronous communication between services. A producer sends a message to a queue, and one or more consumers process it later. This decouples services, handles traffic spikes through buffering, and improves reliability since messages persist until processed. The main considerations are choosing the right delivery guarantee—usually at-least-once with idempotent consumers—and ensuring proper monitoring of consumer lag. Popular choices include Kafka for high-throughput event streaming and RabbitMQ for traditional task queues."
