# Strong Answer: Event Bus / Pub-Sub Broker

A "Strong Hire" answer for the Event Bus/Pub-Sub Broker LLD problem demonstrates a balance between clean object-oriented architecture and practical handling of concurrency, which is the crux of this problem.

## What Constitutes a Strong Answer?

### 1. Robust Concurrency Handling
A weak answer uses basic `ArrayList` and `HashMap` and ignores threading. An average answer sprinkles `synchronized` keywords everywhere, creating massive contention. 
A **strong answer**:
- Uses fine-grained concurrency controls: `ConcurrentHashMap` for topic registries, `BlockingQueue` or `ConcurrentLinkedQueue` for partition message storage.
- Clearly separates the thread doing the publishing from the thread(s) doing the consuming. E.g., placing the message on a queue and letting a background `ExecutorService` handle the dispatch.

### 2. Comprehensive Implementation of Consumer Groups
A weak answer only implements basic broadcast (fan-out).
A **strong answer**:
- Explicitly models the difference between subscribing as a distinct entity (getting all messages) vs. subscribing as part of a group (competing for messages).
- Implements a routing mechanism that iterates through all subscribed groups, and for each group, selects exactly one consumer (e.g., using round-robin) to receive the message.

### 3. Clear Separation of Concerns (SOLID)
A strong answer doesn't put all the logic in a God-class `Broker`. It defines distinct roles:
- `Message`: Immutable data carrier.
- `Partition`: Manages the queue and ordering.
- `Topic`: Manages a collection of partitions.
- `ConsumerGroup`: Manages load balancing across its consumers.
- `Router / Dispatcher`: Handles the delivery logic.

### 4. Pluggable Strategies
A strong answer anticipates changing requirements. It uses the Strategy Pattern for:
- **Partitioning Strategy**: An interface determining which partition a message goes to (e.g., `DefaultPartitionStrategy`, `KeyHashPartitionStrategy`).
- **Delivery Strategy**: Providing hooks for retries or different acknowledgment semantics.

### 5. Defensive Programming
A strong answer considers failure states:
- What if a topic doesn't exist when publishing? (Create it or throw an error, but handle it explicitly).
- What if a consumer's `consume` method throws an exception? (Catch it in the dispatcher so it doesn't kill the broker thread).
- What if the system runs out of memory? (Implement bounded queues).

### 6. Executable and Verifiable
The candidate writes a `main` method or unit tests that actually compile (in their language) and run to prove the core functionality:
- Scenario A: Two independent consumers both get the same message (Broadcast).
- Scenario B: Two consumers in the *same* group. Only one gets message 1, the other gets message 2 (Load Balancing).
