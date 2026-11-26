# Market Alert Engine - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---|---|
| **Composite Pattern Application** | 30% | Correctly models conditions as a tree using the Composite pattern, supporting arbitrary nesting of AND/OR/NOT expressions. |
| **Stateful Cooldown Handling** | 25% | Implements thread-safe throttling using compound keys (Rule ID + Symbol) and checks timestamps effectively to prevent alert storms. |
| **Thread Safety & Concurrency** | 25% | Safe against concurrent tick ingestion and rule evaluation. Uses appropriate locks or concurrent collections. |
| **Extensibility (Sinks/Conditions)** | 20% | Easy to add new condition types (e.g., Moving Average) and new notification sinks (e.g., Email, Webhook) without modifying core logic. |

## Performance bands

- **Hire:** Implements the composite rules engine elegantly, handles concurrency gracefully, and correctly implements the cooldown mechanism. Tests pass under concurrent load.
- **Leaning Hire:** Working implementation but may have minor race conditions in cooldown handling or less elegant composite condition structures.
- **Leaning No Hire:** Fails to implement the Composite pattern correctly, hardcodes conditions, or ignores cooldowns leading to alert spam.
- **No Hire:** Cannot design the condition evaluation engine, struggles with basic concurrency concepts, or code is tightly coupled and untestable.

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design](./DESIGN.md)
