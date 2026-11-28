# Message Queues

## What is it?

A message queue is a middleware component that enables asynchronous communication between distributed system components by temporarily storing messages until they can be processed.

## Why do we need it?

**The Problem**: Synchronous communication creates tight coupling:
- Service A calls Service B, waits for response
- If B is slow or down, A is blocked
- Traffic spikes overwhelm downstream services
- No way to handle workloads at different rates

**Real Scenario**: An e-commerce site during Black Friday:
- Order placement triggers: payment, inventory, shipping, email, analytics
- If any service is slow, the entire checkout hangs
- Traffic spike overwhelms all downstream services

Message queues solve this by decoupling producers from consumers.

## Types/Approaches

### 1. Point-to-Point (Queue)
Each message is routed to one consumer for processing (though retries may cause multiple delivery attempts).

```
Producer → [Queue] → Consumer 1
                   → Consumer 2 (competing consumers)
                   → Consumer 3

Message A goes to Consumer 1 only
Message B goes to Consumer 2 only
```

**Use case**: Task distribution, job processing

### 2. Publish-Subscribe (Topic)
Each message is delivered to all subscribers.

```
Publisher → [Topic] → Subscriber 1 (gets all)
                    → Subscriber 2 (gets all)
                    → Subscriber 3 (gets all)
```

**Use case**: Event broadcasting, notifications

### 3. Consumer Groups
Combines queue and pub-sub: each group gets all messages, but within a group, each message goes to one consumer.

```
                    ┌─ Consumer A1 ─┐
Publisher → Topic → │  (Group A)    │ gets msg1
                    └─ Consumer A2 ─┘ gets msg2
                    ┌─ Consumer B1 ─┐
                    │  (Group B)    │ gets msg1 & msg2
                    └───────────────┘
```

**Use case**: Kafka consumer groups

## Key Concepts

### Message Acknowledgment
```
┌──────────┐  1. Send    ┌───────┐  2. Deliver  ┌──────────┐
│ Producer │───────────→│ Queue │────────────→│ Consumer │
└──────────┘             └───────┘←────────────└──────────┘
                              3. ACK (processed)
```

- **Auto-ACK**: Message removed on delivery
- **Manual ACK**: Consumer confirms processing
- **NACK**: Consumer rejects, message requeued

### Delivery Guarantees

| Guarantee | Description | Reality / Use Case |
|--- |--- |--- |
| At-most-once | May lose messages | Metrics, logs |
| At-least-once | May duplicate | Most applications |
| Exactly-once | Effectively-once via Idempotency | No universal "exactly-once" for external side effects. |


#### The "Exactly-Once" Myth and Effect Boundaries

It's critical to distinguish between different types of actions when discussing delivery guarantees:
- **Delivery Attempt**: The broker sending a message to a consumer over the network.
- **Broker Transaction**: An atomic commit of producing/consuming within the broker's own logs.
- **Consumer Offset**: The pointer indicating which messages a consumer group has successfully acknowledged.
- **Database Mutation**: A transactional update to a consumer's local data store.
- **External Side Effect**: Non-transactional actions outside the system's control, such as a payment gateway API call.

Because systems can crash at any point, a universal "exactly-once" delivery that magically guarantees an external effect is executed only once is impossible. Consider this four-step commit/ack crash table:

| Step | Action | Crash Outcome | Replay Result |
|--- |--- |--- |--- |
| 1 | **Receive**: Consumer pulls message from broker | Crash before effect | Message redelivered; no harm |
| 2 | **Effect**: Execute external side effect (e.g., payment API) | Crash after effect, before DB/ACK | **Duplicate payment** |
| 3 | **Mutate**: Update local database state | Crash after DB, before ACK | **Duplicate payment/mutation attempt** |
| 4 | **ACK**: Commit consumer offset to broker | - | Message processed successfully |

If a crash happens after the external effect (Step 2) but before the broker ACK (Step 4), the message will be redelivered. Therefore, successful broker transactions do not make an external payment "exactly once".

To solve this, we rely on **At-least-once attempts plus idempotent effect contracts**.
Instead of trying to prevent duplicates at the broker network level, the consumer's logic must be idempotent. This involves:
- **Offset/Effect Atomic Commit**: Updating the local DB state and the consumer offset in a single distributed transaction (often slow or unsupported).
- **Durable Inbox/Outbox/Key Payload Binding**: Using a local DB transaction to record the incoming message ID (Inbox), mutate state, and stage outbound messages (Outbox).
- Handling **duplicate IDs and payload mismatches**: The system must enforce that a re-processed ID does not repeat the side effect, and reject mismatched payloads for an already-processed ID. Bounded retention limits for deduplication keys must be clearly stated.

> **Deep Dive →** See [Idempotency](../idempotency/THEORY.md) for retry-safe side-effect patterns and [Distributed Transactions](../distributed-transactions/THEORY.md) for Saga/Outbox docs instead of duplicating them here.

### Dead Letter Queue (DLQ)
Messages that fail repeatedly go to DLQ for manual review.

```
Main Queue → Consumer (fails 3x) → Dead Letter Queue
```

**DLQ Redrive Requirements:**
When redriving (replaying) messages from a DLQ back to the main queue or consumer, care is needed to avoid data corruption:
- **Retained Event Identity**: Redriven messages must retain their original logical identity/IDs for deduplication.
- **Schema & Authorization Validation**: DLQ redrive cannot silently bypass ACL/schema checks. Events must be re-validated.
- **Bounded Attempts & Poison-Event Quarantine**: A poison message (e.g., malformed payload crashing the parser) must be isolated to a quarantine to prevent infinite redrive loops. Use strict, bounded attempts.
- **Explicit Order Effects**: Redriving a stale DLQ message might overwrite a newer, correct state if order isn't explicitly validated.
- **Dedup Retention Limits vs. Permanent Guarantees**: Distinguish dedup retention from permanent guarantees. If deduplication keys have bounded retention limits (e.g., 7 days), redriving an older DLQ message will bypass deduplication and *reset money side effects* or repeat actions.

## How it works

### Basic Flow
```
┌──────────────────────────────────────────────────────┐
│                    Message Broker                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │ Queue 1 │  │ Queue 2 │  │ Topic 1 │              │
│  │ [msg1]  │  │ [msg2]  │  │ [msg3]  │              │
│  │ [msg4]  │  │         │  │ [msg5]  │              │
│  └─────────┘  └─────────┘  └─────────┘              │
└──────────────────────────────────────────────────────┘
      ↑                           │
   produce                     consume
      │                           ↓
┌──────────┐                ┌──────────┐
│ Service A│                │ Service B│
└──────────┘                └──────────┘
```

### Partitioning for Scalability
```
Topic: orders
├── Partition 0: [order1, order4, order7]  → Consumer 1
├── Partition 1: [order2, order5, order8]  → Consumer 2
└── Partition 2: [order3, order6, order9]  → Consumer 3
```

### Message Ordering
- **Total ordering**: All messages in sequence (single partition)
- **Partition ordering**: Order within partition only (Kafka)
- **No ordering**: Best effort (some queues)

## When to use

1. **Decoupling services**
   - Services don't need to know about each other
   - Add new consumers without changing producers

2. **Load leveling**
   - Handle traffic spikes gracefully
   - Process at consumer's pace

3. **Async processing**
   - Fire-and-forget operations
   - Background jobs

4. **Event-driven architecture**
   - React to events
   - Build event sourcing systems

## When NOT to use

1. **Need synchronous response**
   - User waiting for result
   - Request-response pattern better

2. **Low latency required**
   - Queue adds latency
   - Direct calls faster

3. **Simple systems**
   - Overhead not worth it
   - Added operational complexity

4. **Strong consistency needed**
   - [Distributed transactions](../distributed-transactions/THEORY.md) are difficult
   - Eventual consistency is inherent

## Trade-offs

| Aspect | Queues | Direct Calls |
|--- |--- |--- |
| Coupling | Loose | Tight |
| Latency | Higher | Lower |
| Reliability | Better | Depends |
| Complexity | More | Less |
| Throughput | Higher | Limited |
| Debugging | Harder | Easier |

## Real-world examples

### LinkedIn (Kafka)
- 7+ trillion messages/day
- Used for activity tracking, metrics
- Powers real-time analytics

### Uber (Kafka)
- All ride events flow through Kafka
- Enables real-time surge pricing
- Connects 100s of microservices

### Netflix
- Uses Kafka for event sourcing
- SQS for job distribution
- Handles millions of streams

### Slack
- Uses Kafka for message processing
- Ensures message ordering per channel
- Handles billions of messages

## Event Streaming with Kafka

### What Makes Kafka Different?

Unlike traditional message queues that delete messages after consumption, Kafka is a **distributed event streaming platform** built on an append-only log architecture. This fundamental difference enables unique capabilities for modern distributed systems.

### Log-Based Architecture

```
Traditional Queue (RabbitMQ):
Producer → [msg1, msg2, msg3] → Consumer (messages deleted)

Kafka Topic (Log-based):
Producer → Partition 0: [msg1, msg2, msg3, msg4, ...] (retained)
                        ↑           ↑
                   offset:0    offset:1

Consumer maintains offset pointer → Can replay from any position
```

**Key insight**: Kafka is a **distributed commit log**, not just a queue. Messages are retained for a configurable time period (days, weeks, or forever), enabling:
- Multiple consumers reading at different speeds
- Replay for debugging or rebuilding state
- New consumers processing historical data
- Event sourcing architectures

### Topics and Partitions

```
Topic: "user-events" (logical grouping)
├── Partition 0: [event1, event4, event7, ...]  → Consumer A
├── Partition 1: [event2, event5, event8, ...]  → Consumer B
└── Partition 2: [event3, event6, event9, ...]  → Consumer C

Partitioning enables:
✓ Parallelism: Multiple consumers process independently
✓ Ordering: Guaranteed within a partition (not across)
✓ Scalability: Add partitions to increase throughput
```

**Partition key**: Messages with same key go to same partition, maintaining order for related events
```
key = user_id → Ensures all events for user_123 go to same partition
```

### Consumer Groups

Kafka's consumer groups combine pub-sub and queue patterns:

```
Topic: "orders" (3 partitions)

Consumer Group "payment-service":
├── Consumer A → reads Partition 0
├── Consumer B → reads Partition 1
└── Consumer C → reads Partition 2
(Each partition consumed by ONE consumer in group)

Consumer Group "analytics-service":
├── Consumer X → reads Partitions 0, 1, 2
(Independently gets ALL messages)
```

**Rebalancing**: When consumer joins/leaves, partitions automatically redistribute

### Durability and Replication

```
Topic: "transactions" (replication factor = 3)

Partition 0:
├── Leader (Broker 1)    ← Writes go here
├── Follower (Broker 2)  ← Sync replica
└── Follower (Broker 3)  ← Sync replica

If Leader fails → Follower elected as new Leader
```

**In-Sync Replicas (ISR)**: Only replicas caught up with leader can be elected

### Exactly-Once Semantics

Kafka supports exactly-once processing through:

1. **Idempotent Producer**: Duplicate messages detected and dropped
```
Producer config:
enable.idempotence = true
```

2. **Transactional Writes**: Atomic writes across multiple partitions
```
producer.beginTransaction()
producer.send(topic1, msg1)
producer.send(topic2, msg2)
producer.commitTransaction()
```

3. **Read Committed**: Consumers only see committed messages
```
consumer.setIsolationLevel(READ_COMMITTED)
```

**Use case**: Stream processing within Kafka (Kafka-to-Kafka). Note: This does not guarantee exactly-once for external side-effects like payments, which still require idempotent consumers. EOS covers only Kafka read-process-write via idempotent producer + transactions + read_committed, not external side effects.

### Kafka vs Traditional Queues

| Aspect | Kafka | RabbitMQ | AWS SQS |
|--- |--- |--- |--- |
| **Architecture** | Distributed log | Message broker | Cloud queue |
| **Message Retention** | Configurable (days/forever) | Until consumed | Up to 14 days |
| **Message Replay** | ✅ Yes (offset control) | ❌ No | ❌ No |
| **Ordering Guarantee** | Per partition | No guarantee | FIFO queues available |
| **Throughput** | Very high (millions/sec) | High (tens of thousands/sec) | Medium (SQS FIFO dedupes within 5 min; FIFO is 300 msg/s per action, 3000 with batching) |
| **Latency** | Low-medium (10-50ms) | Very low (1-10ms) | Medium (50-100ms) |
| **Persistence** | Always on disk | Memory + optional disk | AWS managed |
| **Scalability** | Horizontal (add partitions/brokers) | Vertical + clustering | AWS auto-scale |
| **Consumer Model** | Pull-based | Push-based | Pull-based (polling) |
| **Best For** | Event streaming, high-throughput pipelines | Task queues, routing complexity | Serverless, AWS integration |

### When to Choose Kafka

✅ **Use Kafka when:**
- High throughput event streaming (millions of events/sec)
- Need to replay messages or rebuild state
- Multiple consumers need independent processing
- Event sourcing or CQRS architecture
- Building data pipelines between systems
- Real-time analytics on event streams

**Example scenarios:**
- User activity tracking (clicks, views, purchases)
- System metrics and log aggregation
- Change data capture (CDC) from databases
- Microservices event bus
- Real-time fraud detection

❌ **Avoid Kafka when:**
- Simple task queue with low volume
- Need routing based on message content (use RabbitMQ)
- Require very low latency (<5ms)
- Complex priority queues needed
- Small team without Kafka expertise

### Kafka Performance Characteristics

```
Typical performance (properly tuned):
├── Throughput: 100K-1M messages/sec per broker
├── Latency: 10-50ms end-to-end
├── Retention: 7-30 days typical (configurable)
├── Replication: 3x common (RF=3)
└── Consumers: Hundreds per topic (independent groups)
```

### Kafka Use Cases in Industry

**LinkedIn** (Kafka creators):
- 7+ trillion messages/day
- Activity tracking, metrics, logging
- Powers real-time features across platform

**Uber**:
- All trip events flow through Kafka
- 1+ trillion messages/day
- Real-time surge pricing, dispatch, ETAs

**Netflix**:
- Event sourcing for viewing history
- Real-time recommendations
- Operational metrics and monitoring

**Airbnb**:
- Search ranking signals
- Payment events
- Booking flow analytics

## Comparison: Kafka vs RabbitMQ vs SQS

| Feature | Kafka | RabbitMQ | AWS SQS |
|--- |--- |--- |--- |
| Pattern | Log-based streaming | Traditional broker | Cloud queue |
| Architecture | Distributed commit log | Centralized broker | Serverless queue |
| Ordering | Per partition | No (unless single consumer) | FIFO option |
| Replay | ✅ Yes | ❌ No | ❌ No |
| Throughput | Very high (1M+/sec) | High (10K-100K/sec) | Medium (SQS FIFO dedupes within 5 min; FIFO is 300 msg/s per action, 3000 with batching) |
| Latency | Low-medium (10-50ms) | Very low (1-10ms) | Medium (50-100ms) |
| Persistence | Always (disk-based) | Memory + optional disk | AWS managed (14 days max) |
| Retention | Days to forever | Until consumed | Until consumed (14 days max) |
| Consumer Types | Pull-based consumer groups | Push-based subscriptions | Poll-based |
| Exactly-once | ✅ Supported | Manual idempotency | ❌ At-least-once only |
| Horizontal Scale | ✅ Add partitions/brokers | Clustering (complex) | ✅ AWS auto-scale |
| Operational Complexity | High (ZooKeeper/KRaft, tuning) | Medium (clustering) | Low (managed) |
| Use case | Event streaming, data pipelines | Task queues, complex routing | Serverless, AWS glue |
| Best for | High volume, replay needed | Low latency, flexible routing | Simple, cloud-native |

## Complexity Analysis

| Operation | Time | Notes |
|--- |--- |--- |
| Produce | O(1) | Append to log |
| Consume | O(1) | Sequential read |
| Random access | O(1) | With offset (Kafka) |
| Topic lookup | O(1) | Hash-based |

## Key Takeaways

1. **Choose delivery guarantee wisely** - At-least-once is usually enough
2. **Design for idempotency** - Messages may be delivered multiple times; see [Idempotency](../idempotency/THEORY.md) for retry-safe side-effect patterns
3. **Monitor consumer lag** - Indicates processing backlog
4. **Use DLQ for failures** - Don't lose messages, investigate later
5. **Partition for scale** - More partitions = more parallelism

---

## GenAI Notes

Message queues are essential infrastructure in LLM-powered systems for decoupling expensive, variable-latency inference from user-facing services:

| GenAI Queue Pattern | Description | Why It Matters |
|--- |--- |--- |
| **Async inference pipeline** | Enqueue user prompts; worker pool calls LLM and writes results | LLM latency (seconds) is too high for synchronous request paths at scale |
| **Document indexing queue** | Queue documents for chunking → embedding → vector DB ingestion | Decouple document upload from the multi-step RAG indexing pipeline |
| **Feedback / evaluation loop** | Queue model outputs for offline evaluation, human review, or fine-tuning data collection | Collect golden-set data without blocking the serving path |
| **Tool execution queue** | Agent dispatches tool calls to a queue; workers execute and return results | Isolate slow or unreliable tool calls from the agent reasoning loop |

**Key differences from classical queuing:**
- **Message sizes vary dramatically**: A prompt + context can be 100 KB+, while a tool-call result may be a few bytes. Size-based partitioning may be needed.
- **Idempotency is critical for agents**: An agent may retry a tool call; the tool must produce the same result without side effects (see [Prompting, Tools & Agents](../../06-genai-systems/00-concepts/prompting-tools-agents/)).
- **Priority queues for model tiers**: Route premium-tier users to faster models while queueing free-tier requests for batch inference.

> **Deep dive →** [RAG Architecture](../../06-genai-systems/00-concepts/rag-architecture/) · [Prompting, Tools & Agents](../../06-genai-systems/00-concepts/prompting-tools-agents/)

## 📊 Diagrams

- [Ack, retry, and dead-letter flow](./diagrams/ack-retry-dead-letter-flow.mmd) - the delivery lifecycle from producer through broker to a consumer group: ACK commits the offset, a NACK within the retry budget requeues the message, and exhausted attempts move it to the dead-letter queue.
