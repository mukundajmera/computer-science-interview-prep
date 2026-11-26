# Problem: Distributed Key-Value Store

Design a distributed, highly available, and scalable key-value store (Dynamo-style).

## Requirements

*   **Core functionality:** `put(key, value)` and `get(key)`.
*   **High availability:** The system must be able to serve read and write requests even if some nodes fail or are unreachable due to network partitions.
*   **Scalability:** The system should scale incrementally by adding more nodes without requiring a complete rewrite or downtime.
*   **Tunable consistency:** Allow clients to balance availability and consistency (e.g., using N, R, W quorum parameters).

## Scope constraints

*   Values are relatively small (e.g., up to 1MB).
*   Keys are generally uniformly distributed.
