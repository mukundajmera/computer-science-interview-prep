# Evaluation Rubric

## 1. Multi-variant Flags
- **[L4] Intuitive Minimum Example**: A flag can return strings or ints, and falls back to a default if rules fail to match.
- **[L5] Trade-offs**: Discusses how complex evaluation types (e.g., JSON) affect memory.

## 2. Segment Evaluation
- **[L4] Intuitive Minimum Example**: Supports basic matching operators (`EQUALS`) against a simple map of context attributes.
- **[L5] Trade-offs**: Analyzes latency constraints if we support deeply nested conditions or regex attributes.

## 3. Percentage Rollouts
- **[L4] Intuitive Minimum Example**: The same user deterministically hashes to the same variant based on percentage thresholds.
- **[L5] Trade-offs**: Compares different non-cryptographic hashes for speed versus distribution uniformity.

## 4. Change Listeners
- **[L4] Intuitive Minimum Example**: Observers are notified upon an update event.
- **[L5] Trade-offs**: Discusses asynchronous/non-blocking callbacks instead of running listener code on the same update thread.

## 5. Correctness Invariants & Concurrency
- **[L4] Intuitive Minimum Example**: Lock-free evaluation via replacing the entire `FeatureFlag` instance during updates instead of in-place mutation.
- **[L5] Trade-offs**: Highlights read/write separation via `ConcurrentHashMap` or explicit read/write locks, preventing contention during frequent access.

## Reading Path
**Beginner**: Start at [CODE-WALKTHROUGH.md](CODE-WALKTHROUGH.md) (v1-basic/v2-extended).  
**Senior**: See [STRONG-ANSWER.md](STRONG-ANSWER.md) for 45-minute pacing and scale.  
**Staff**: Check [PITFALLS.md](PITFALLS.md) and [FOLLOW-UPS.md](FOLLOW-UPS.md) for failure traces and extensions.
