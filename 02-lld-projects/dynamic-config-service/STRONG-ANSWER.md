# Strong Answer: Dynamic Feature Flag Engine

This guide provides a structured 45-minute verbal pacing target for presenting a comprehensive design of a Dynamic Feature Flag Engine.

## 1. Requirements & Problem Scoping (5 mins)
**Say:** "To build an effective dynamic config service, the core requirement is to evaluate flags deterministically for users without impacting latency. We need multi-variant support, segment targeting via user attributes, percentage rollouts, and change listeners for real-time updates. The engine must be robust and provide sensible fallbacks when evaluation fails."

## 2. Entity Modeling & Data Structure Rationale (10 mins)
**Say:** "The core entities include `ConfigEngine`, `FeatureFlag`, `Rule`, `Rollout`, and `UserContext`. I will use a `ConcurrentHashMap` for storing `FeatureFlag` objects to support high-throughput lock-free reads while allowing thread-safe updates. `FeatureFlag` and `Rule` objects will be immutable. When an update occurs, the engine replaces the entire `FeatureFlag` instance atomically."

## 3. Concurrency Defense & State Synchronization (10 mins)
**Say:** "Concurrency defense is critical here. Reads happen constantly and must not be blocked by updates. By using a `ConcurrentHashMap` and immutable configuration objects, we prevent read-write contention. For state synchronization, particularly when listeners are involved, we use a thread-safe observer pattern. When a flag updates, listeners are notified asynchronously or in a separate thread pool to prevent blocking the update thread. This avoids scenarios where a slow listener halts configuration propagation."

## 4. Rollout Logic & Hashing (10 mins)
**Say:** "For percentage rollouts, we must guarantee determinism. If we use a random number generator, users will bounce between variants across requests, causing a poor experience. Instead, I will hash a combination of the `userId` and `flagKey` using a non-cryptographic hash function like MurmurHash3, modulo 100, to get a consistent bucket from 0 to 99. This bucket determines which variant the user receives according to the configured rollout percentages."

## 5. Scaling Limits & Indexing Trade-offs (5 mins)
**Say:** "At scale, storing configurations in memory is highly efficient, but the memory footprint could grow if there are tens of thousands of complex rules. The primary limit is RAM. Indexing trade-offs come into play if we want to reverse-query 'which flags affect this user?'. Typically, flag evaluation is forward-only (give me the value for this flag given this user context). If we needed reverse lookups, we'd need inverted indices mapping attributes to flags, which significantly increases memory and update complexity. In a distributed environment, synchronizing this state across nodes typically involves a system like etcd or Redis Pub/Sub to invalidate local caches."

## 6. Failure Handling & Production Trade-offs (5 mins)
**Say:** "Failure handling relies heavily on defaults. If a user context is missing an attribute required by a rule, the rule evaluation safely fails, and the engine falls back to the flag's default variant. A key production trade-off is eventual consistency versus strict consistency across nodes. For feature flags, eventual consistency (milliseconds to seconds delay) is almost always acceptable and allows us to prioritize low latency and high availability over strong consensus for every read."

