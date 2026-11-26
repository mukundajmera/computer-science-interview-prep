# Market Alert Engine - Follow-Up Questions

## Follow-up questions

1.  **How would you handle historical data backtesting?**
    - Ensure the engine can process ticks based on the tick's timestamp, not the system's current clock time, allowing for simulated replays.

2.  **How would you scale this to millions of rules and high tick volumes?**
    - Partition the data streams by symbol and route to specific worker nodes (e.g., using Kafka partitions). Each worker evaluates rules only for its assigned symbols.

3.  **How would you handle conditions that depend on a window of time (e.g., "Price dropped 10% in the last 5 minutes")?**
    - Introduce stateful conditions that maintain sliding windows or use a stream processing framework (like Flink) to aggregate ticks before evaluation.

## Variants and extensions
- **Cross-Symbol Rules:** E.g., "Alert if AAPL price > GOOGL price". This breaks the symbol-indexing optimization and requires evaluating a joined state.
- **Dynamic Rule Modification:** Allowing users to update conditions or cooldowns on the fly without restarting the engine.

## Interviewer probes to prepare
- "What if the same rule applies to all tech stocks instead of just one symbol?"
- "Can you show me where the race condition might occur if two threads process ticks for the same symbol at the exact same millisecond?"
- "How do you ensure your composite condition tree doesn't cause a stack overflow during evaluation?"

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design](./DESIGN.md)
