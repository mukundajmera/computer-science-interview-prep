# Grading Rubric: Event Bus / Pub-Sub Broker

## 1. Functional Completeness (30%)
- **[ ] Basic Pub-Sub**: Can a producer publish a message and a consumer receive it?
- **[ ] Topic Management**: Are topics explicitly modeled?
- **[ ] Consumer Groups**: Does the system correctly handle broadcast (multiple groups) and load balancing (competing consumers within a group)?
- **[ ] Partitioning**: Does the system support partitioning messages within a topic based on a key?

## 2. Object-Oriented Design (25%)
- **[ ] Separation of Concerns**: Are Producer, Consumer, Topic, and Broker well-defined and decoupled?
- **[ ] Design Patterns**: Are appropriate patterns (Observer, Mediator, Strategy) utilized and correctly implemented?
- **[ ] Interface Design**: Are the APIs clean, intuitive, and easy to use for external clients?
- **[ ] Extensibility**: How easy is it to add a new partitioning strategy or a new type of consumer?

## 3. Concurrency and Thread Safety (25%)
- **[ ] Safe State Mutation**: Are topic registries, consumer group lists, and partition queues safe from race conditions during concurrent modifications?
- **[ ] Non-blocking Publish**: Does publishing a message block the producer while consumers process it? (It should not).
- **[ ] Asynchronous Dispatch**: Is message delivery handled by background threads or an executor service?
- **[ ] Deadlock Prevention**: Is there any risk of deadlocks when managing locks or concurrent data structures?

## 4. Error Handling and Resilience (10%)
- **[ ] Bad Inputs**: Does the system gracefully handle null messages, invalid topic names, or subscribing to non-existent topics?
- **[ ] Faulty Consumers**: If a consumer throws an exception during `consume()`, does it crash the broker or block other consumers?
- **[ ] Queue Management**: Are there bounds or limits on how many messages can be queued in memory?

## 5. Code Quality and Testing (10%)
- **[ ] Readability**: Is the code clean, well-named, and easy to follow?
- **[ ] Testing**: Are there comprehensive tests demonstrating pub-sub, consumer groups, and thread safety? (Tests must pass).
