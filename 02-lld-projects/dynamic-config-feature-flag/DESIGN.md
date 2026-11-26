# Design: Dynamic Configuration & Feature Flag Service

## Core Components & Architecture

### 1. `FeatureFlagManager` (Singleton & Facade)
* **Responsibility:** Acts as the central point of entry for clients. Manages the internal registry of feature flags, handles updates, and provides methods for evaluation.
* **Design Pattern:** **Singleton**. Ensure there is only one authoritative source of configuration state within the application lifecycle to prevent conflicting states. It also acts as a Facade, hiding the complexity of the underlying rule engines and strategy selection from the client.
* **Key Methods:**
  * `evaluate(flagKey, context, defaultValue)`: The primary API for clients to evaluate a flag.
  * `updateFlag(flagKey, configuration)`: API for the control plane to push updates.
  * `subscribe(flagKey, observer)`: Registers an observer for a specific flag.

### 2. `EvaluationContext` (Data Transfer Object)
* **Responsibility:** Encapsulates all context attributes required for flag evaluation.
* **Structure:** Typically a map of key-value pairs (e.g., `Map<String, Object>`), containing attributes like `userId`, `country`, `appVersion`, `tenantId`, etc.

### 3. `EvaluationStrategy` (Strategy Pattern)
* **Responsibility:** Defines the contract for different types of flag evaluations.
* **Design Pattern:** **Strategy**. This allows adding new types of flag evaluation algorithms without modifying the core `FeatureFlagManager`.
* **Implementations:**
  * `BooleanStrategy`: Simply returns the hardcoded boolean value.
  * `PercentageRolloutStrategy`: Uses hashing (e.g., MD5/SHA-256 or MurmurHash on the `userId` + `flagKey`) to deterministically compute a value between 0-100 and compares it against the rollout percentage.
  * `AllowlistStrategy`: Checks if the user's ID exists in a predefined Set of allowed IDs.
  * `RuleBasedStrategy`: Defers evaluation to the Rule Engine based on complex context conditions.

### 4. `RuleEngine` (Composite / Rule Pattern)
* **Responsibility:** Evaluates a set of logical conditions against the `EvaluationContext`.
* **Design Pattern:** **Rule Engine / Composite**. A rule can consist of multiple conditions combined with logical operators (AND, OR).
* **Components:**
  * `Condition`: An interface with a method `isMet(context)`.
  * `NumericCondition` (e.g., GreaterThan, LessThan).
  * `StringCondition` (e.g., Equals, InList, MatchesRegex).
  * `LogicalCondition`: Combines multiple conditions (e.g., `AndCondition(cond1, cond2)`).

### 5. `ConfigurationStore` & Thread Safety
* **Responsibility:** Holds the current state of all feature flags in memory.
* **Concurrency:** To achieve high read throughput and safe updates, the store must be thread-safe.
  * **Java:** Use `ConcurrentHashMap` for storing the flags. If flag configurations are immutable, updates can simply replace the old configuration object reference with a new one in the map.
  * **Python:** Dictionaries are thread-safe for basic read/write operations due to the GIL, but complex update logic might require a `threading.Lock` or `threading.RLock` during the update process to prevent race conditions. Read operations should be lock-free where possible.

### 6. `FlagObserver` (Observer Pattern)
* **Responsibility:** Allows clients or background processes to react to configuration changes.
* **Design Pattern:** **Observer**.
* **Flow:** When `updateFlag` is called and the new configuration differs from the old one, the `FeatureFlagManager` iterates through the list of observers registered for that `flagKey` and triggers their `onUpdate` method.
