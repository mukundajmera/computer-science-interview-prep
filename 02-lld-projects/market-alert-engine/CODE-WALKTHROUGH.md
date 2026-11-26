# Market Alert Engine - Code Walkthrough

## 1. Tick Representation
A simple immutable data class holding the market data.

## 2. Condition Evaluation (Composite Pattern)
The `Condition` interface has a single method: `evaluate(Tick)`.
- `PriceCondition` and `VolumeCondition` compare the tick's price or volume against a configured threshold.
- `AndCondition`, `OrCondition`, and `NotCondition` compose other conditions to form complex logical expressions.

## 3. Alert Rules and Sinks
An `AlertRule` encapsulates the condition, the target symbol, the desired cooldown period, and the output `Sink`s.
Sinks implement the `send` method to route notifications (e.g., `ConsoleSink`).

## 4. The Alert Engine
The `AlertEngine` coordinates the workflow:
- **Registration**: Rules are indexed by symbol for O(1) retrieval during tick processing.
- **Tick Processing**: When a tick arrives, the engine retrieves all rules for that symbol.
- **Evaluation and Cooldown**: It evaluates each rule's condition. If true, it checks the cooldown map using a compound key (`ruleId + symbol`).
- **Thread Safety**: Concurrent data structures (`ConcurrentHashMap`) and locks ensure thread safety when reading/updating cooldowns and processing ticks concurrently.
