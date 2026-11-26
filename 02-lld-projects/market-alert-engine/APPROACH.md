# Market Alert Engine - Approach

## Core Principles

1.  **Composite Pattern for Rules Engine**: 
    The conditions evaluated against the market data stream form a tree structure. Leaf nodes represent simple predicates (e.g., `PriceCondition`, `VolumeCondition`), while internal nodes represent logical operations (`AndCondition`, `OrCondition`, `NotCondition`). The Composite pattern allows treating simple and complex conditions uniformly.

2.  **Observer Pattern for Sinks**:
    Alert rules act as subjects that produce notifications. Sinks (like email, SMS, or console) act as observers. This allows dynamic addition or removal of notification channels without modifying the core rule engine.

3.  **Stateful Cooldown Throttling**:
    Market data is noisy. To prevent alert fatigue, a cooldown mechanism is necessary. When a rule triggers an alert for a specific symbol, a timestamp is recorded. Subsequent triggers for the same rule and symbol are suppressed until the cooldown period expires.

4.  **Thread Safety**:
    The system must handle multiple concurrent threads pushing ticks while simultaneously managing rule subscriptions and stateful cooldowns. Thread-safe data structures (`ConcurrentHashMap`, locks) are required to ensure data integrity during concurrent evaluation.

## Workflow

1.  **Rule Creation**: A user creates an `AlertRule` specifying the target symbol, a `Condition`, a cooldown period, and one or more `Sink`s.
2.  **Registration**: The rule is registered with the `AlertEngine`.
3.  **Tick Ingestion**: The `AlertEngine` receives a `Tick`.
4.  **Evaluation**: The engine looks up rules matching the tick's symbol and evaluates their condition.
5.  **Cooldown Check**: If a condition evaluates to `true`, the engine checks the cooldown state.
6.  **Notification**: If the cooldown has expired (or it's the first trigger), the engine updates the cooldown state and dispatches the alert to the associated sinks.
