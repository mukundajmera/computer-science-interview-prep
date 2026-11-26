# Approach: Event Bus / Pub-Sub Broker

## Recommended Interview Strategy

When tasked with designing an Event Bus or Pub-Sub Broker (like a simplified Kafka) in an object-oriented design interview, follow this structured approach:

### 1. Clarify Requirements (5-10 mins)
- Ask about the scope: Is this purely in-memory, or does it require disk persistence? (Assume in-memory for this LLD unless specified otherwise).
- Ask about delivery semantics: Do we need At-Most-Once, At-Least-Once, or Exactly-Once?
- Ask about consumer models: Do we need both fan-out (broadcast to all) and worker queues (competing consumers/consumer groups)?
- Ask about ordering: Does order matter? (Usually yes, per partition/topic).

### 2. Define Core Entities (10 mins)
Identify the primary nouns and design their interfaces:
- `Message`: Contains payload and metadata.
- `Topic`: Represents a stream of messages.
- `Partition`: A subdivision of a topic for ordering and concurrency.
- `Consumer`: An interface with a `consume(Message)` method.
- `Producer`: An interface or class for sending messages.
- `Broker`: The central orchestrator.

### 3. Establish the Abstractions and Patterns (10 mins)
Mention design patterns explicitly to show architectural knowledge:
- **Mediator**: The Broker manages all interactions, so Producers don't know about Consumers.
- **Observer**: Consumers subscribing to the Broker.
- **Strategy**: Pluggable partition assignment (e.g., RoundRobin vs. Hashing).

### 4. Implement Core Logic (15-20 mins)
Focus on the Broker's implementation. Start simple, then add complexity:
1. **Basic Pub-Sub**: Implement `publish(topic, message)` and `subscribe(topic, consumer)`. Use basic maps (`Map<String, List<Consumer>>`).
2. **Consumer Groups**: Upgrade the data structure to group consumers. `Map<String, Map<String, List<Consumer>>>` (Topic -> ConsumerGroup -> Consumers).
3. **Partitioning**: Introduce Partitions within Topics.

### 5. Address Concurrency (5-10 mins)
This is the most critical part for a senior candidate.
- Explain how you handle simultaneous publishes.
- Discuss using Thread-Safe collections (`ConcurrentHashMap`, `CopyOnWriteArrayList`).
- Discuss dispatching mechanisms: Will `publish()` block until all consumers process the message? (It shouldn't). Introduce an `ExecutorService` or worker threads to dispatch messages asynchronously.
- Mention potential issues with thread starvation or unbounded queues.

### 6. Refine and Discuss Trade-offs (5 mins)
- What happens if a consumer is slow? (Memory exhaustion). Discuss bounding the queues or eviction policies.
- How to handle retries?
- How would you evolve this into a distributed system? (Zookeeper/Raft for coordination, leader election for partitions).
