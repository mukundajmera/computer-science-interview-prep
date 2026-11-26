# Common Pitfalls: Event Bus / Pub-Sub Broker

## 1. Synchronous Dispatch (The Biggest Mistake)
- **Pitfall**: Implementing the `publish()` method such that it iterates through all subscribers and calls their `consume()` method sequentially on the caller's thread.
- **Why it's bad**: If one consumer is slow, or blocks for I/O, the producer is blocked. The entire system grinds to a halt.
- **Solution**: Decouple reception from dispatch. `publish()` should only enqueue the message. A separate worker thread (or pool) should dequeue and dispatch.

## 2. Ignoring Thread Safety
- **Pitfall**: Using `HashMap` or `ArrayList` to manage topics and subscribers in a highly concurrent environment.
- **Why it's bad**: Concurrent modifications (e.g., adding a consumer while iterating over consumers to dispatch a message) will cause `ConcurrentModificationException` or silent data corruption.
- **Solution**: Use `ConcurrentHashMap`, `CopyOnWriteArrayList`, or explicit locks (`ReentrantReadWriteLock`).

## 3. Lack of Consumer Group Logic
- **Pitfall**: Assuming all consumers want a copy of every message (pure broadcast) and ignoring the load-balancing aspect.
- **Why it's bad**: Fails to meet the "Kafka Lite" requirement. Competing consumers are essential for scaling out processing.
- **Solution**: Explicitly model a `ConsumerGroup`. A topic maps to multiple groups. A group contains multiple consumers. Dispatching iterates over groups, but selects only *one* consumer within each group.

## 4. Unbounded Queues
- **Pitfall**: Storing messages in an unbounded queue (like an unbound `LinkedList` or `queue.Queue` with no maxsize).
- **Why it's bad**: In a system where producers outpace consumers (a common scenario), memory will eventually be exhausted, leading to an OutOfMemory (OOM) error and crashing the broker.
- **Solution**: Use bounded queues. Decide on a policy when full (e.g., drop oldest, reject new publishes, or block the producer).

## 5. Over-engineering Persistence early on
- **Pitfall**: Spending half the interview trying to write to files or databases.
- **Why it's bad**: Usually, LLD interviews focus on the in-memory orchestration, concurrency, and OOP design.
- **Solution**: Focus on the in-memory structures first. Design the interfaces such that persistence *could* be added later via the Strategy pattern (e.g., a `StorageStrategy` interface).

## 6. Faulty Consumer Crashing the Broker
- **Pitfall**: Dispatching a message without a `try-catch` block around the consumer's callback.
- **Why it's bad**: If Consumer A throws a `NullPointerException`, the dispatching thread might die, preventing Consumer B from getting the message, or worse, taking down the broker's executor service.
- **Solution**: Wrap consumer invocations in a generic `catch (Exception e)` block to isolate faults.
