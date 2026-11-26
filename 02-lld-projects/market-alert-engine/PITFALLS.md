# Market Alert Engine - Common Pitfalls

## 1. Alert Flooding
- **Failure Signal:** A single price breach results in thousands of notifications sent to a sink in a few seconds.
- **Root Cause:** Missing or incorrectly implemented stateful cooldown throttling. Every tick meeting the condition triggers a new alert.
- **Mitigation:** Track the last triggered timestamp per rule-symbol combination and suppress alerts until `currentTime > lastTriggerTime + cooldown`.
- **Validation/Monitoring Signal:** Monitor the ratio of triggered alerts to condition evaluations.

## 2. Inefficient Rule Evaluation
- **Failure Signal:** System latency spikes during high market volatility.
- **Root Cause:** Evaluating every registered rule for every incoming tick, instead of indexing rules by the target symbol.
- **Mitigation:** Index rules by symbol (e.g., `Map<String, List<AlertRule>>`) so only relevant rules are evaluated for a given tick.
- **Validation/Monitoring Signal:** Measure evaluation latency per tick.

## 3. Concurrency Bugs in Cooldown Map
- **Failure Signal:** Duplicate alerts are sent sporadically, or system throws `ConcurrentModificationException`.
- **Root Cause:** Using a standard `HashMap` for cooldown state in a multi-threaded environment, or non-atomic check-and-update logic.
- **Mitigation:** Use `ConcurrentHashMap` and thread-safe atomic operations (e.g., `compute` or explicit locks) when updating the last trigger time.
- **Validation/Monitoring Signal:** Run concurrent tests and check for exact notification counts.

## 4. Tightly Coupled Conditions
- **Failure Signal:** Adding a new condition type requires modifying the core engine evaluation loop.
- **Root Cause:** Using `if/else` chains instead of polymorphism and the Composite pattern for condition evaluation.
- **Mitigation:** Define a common `Condition` interface and implement specific logic in separate classes.
- **Validation/Monitoring Signal:** Code review should ensure new conditions can be added as isolated classes.
