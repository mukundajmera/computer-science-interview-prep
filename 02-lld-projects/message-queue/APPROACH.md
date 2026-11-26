# In-Memory Message Queue - Approach

## Decoupled Producer-Consumer Mechanics
The broker acts as an intermediary. Producers append messages to partitions in topics, and consumers poll messages from partitions.

## Partition Append-Only Log
Each partition is an append-only list of messages. This ensures fast writes and easy offset-based reads.

## Offset Commit Semantics
- At-least-once: Commit offset after successful processing.
- At-most-once: Commit offset before processing.
For this implementation, consumers commit offsets. The broker tracks offsets per consumer group.

## Topological Sort for Subscriber Dependency DAG
If subscribers have dependencies (e.g., A must process before B), we construct a DAG. A topological sort defines the execution order or a coordinator manages the dispatching based on dependencies resolving.

## Backoff Retry Algorithms
Retry policies dictate how many times and with what delay a message should be retried before moving to a DLQ.
