# Strong Answer: Dynamic Configuration & Feature Flag Service

A strong candidate approaches the Feature Flag Service not just as a map of booleans, but as a robust, highly concurrent evaluation engine. They recognize that in production, reads outnumber writes by orders of magnitude (millions of evaluations vs. a few updates per day).

## Key Characteristics of a Strong Answer

### 1. Correct Application of the Strategy Pattern
Instead of writing a massive, hard-to-maintain `switch(flag.getType())` statement inside the `evaluate` method, the candidate immediately abstracts the evaluation logic into an `EvaluationStrategy` interface.
*   **BooleanStrategy:** Returns the hardcoded state.
*   **AllowlistStrategy:** Leverages an O(1) Set lookup.
*   **PercentageStrategy:** This is the key discriminator. The candidate correctly identifies that percentage rollouts **must be deterministic**. They reject `random()` and implement a fast, stable string hashing algorithm (like MD5) combining `userId + flagKey`, modulo 100. They understand the difference between random assignment (which breaks on refresh) and deterministic hashing.

### 2. Lock-Free Read Optimization
A strong answer avoids coarse synchronization.
*   They don't put a `synchronized` or `Lock` around the entire `evaluate()` method.
*   They use a `ConcurrentHashMap` (Java) to hold the configurations.
*   They enforce immutability for the `FeatureFlag` data objects. When an update occurs, they create a brand new `FeatureFlag` object and swap the reference in the map. This atomic reference swap guarantees that read threads are never blocked by write operations, resulting in maximum throughput.

### 3. Graceful Rule Engine Design
When tackling the rule-based requirements, the candidate uses the Composite pattern effectively. They don't try to invent a custom parser. Instead, they model rules programmatically (e.g., `AndCondition(new StringCondition("country", EQUALS, "US"), new NumericCondition("version", GREATER_THAN, 2))`). They remember to implement short-circuiting in their `AND`/`OR` evaluations for performance.

### 4. Robust Observer Implementation
They implement the Observer pattern to notify listeners of configuration changes. Crucially, they anticipate the `ConcurrentModificationException` that occurs if an observer deregisters *while* the list is being iterated over to dispatch updates. They solve this by using thread-safe collections like `CopyOnWriteArrayList` for managing subscriptions.

### 5. Defensive Programming (Defaults)
The candidate ensures the system can never crash due to a missing flag or a missing user context attribute. Every evaluation strictly honors the user-provided `defaultValue`.

### Summary
The resulting design is O(1) for most evaluations, scales perfectly across multiple threads without locking bottlenecks, guarantees deterministic A/B testing buckets, and provides a clean, extensible API for adding new evaluation logic in the future.
