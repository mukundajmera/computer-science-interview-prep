# Approach: Dynamic Configuration & Feature Flag Service

## Step-by-Step Implementation

### Step 1: Define the Data Models
1.  **`FeatureFlag` Entity:** Create an immutable class/struct representing a flag. It should contain:
    *   `key` (String): Unique identifier for the flag.
    *   `strategyType` (Enum): E.g., BOOLEAN, PERCENTAGE, ALLOWLIST, RULE_BASED.
    *   `configuration` (Object): The specific configuration for the strategy (e.g., a boolean value, a rollout percentage, a list of user IDs, or a set of rules).
2.  **`EvaluationContext`:** A simple wrapper around a Dictionary or Map, providing methods to safely retrieve typed values (e.g., `getString(key)`, `getInteger(key)`).

### Step 2: Implement Evaluation Strategies
Implement the Strategy interface for each evaluation type.

1.  **Boolean:** trivial. Return the configured boolean value.
2.  **Allowlist:** Check if `context.getUserId()` is present in a `Set` of allowed user IDs. Using a `Set` ensures O(1) lookups.
3.  **Percentage Rollout:**
    *   Crucially, this *must* be deterministic. If User A evaluates to 'True' today, they must evaluate to 'True' tomorrow (unless the rollout percentage changes).
    *   **Hashing:** Use a fast hashing algorithm (like MD5 from standard libraries, or a built-in fast string hash if it guarantees cross-process stability—note that Python's `hash()` is salted per-process and *not* stable across restarts, so `hashlib.md5` is required).
    *   **Algorithm:**
        1. Combine `flagKey` and `userId` (e.g., `hashInput = flagKey + ":" + userId`).
        2. Hash the input to get a numerical value.
        3. Modulo the value by 100 to get a bucket between 0-99 (or 1-100).
        4. If `bucket < rolloutPercentage`, return `true`, else `false`.

### Step 3: Implement the Rule Engine
1.  Define the `Condition` interface.
2.  Implement concrete conditions:
    *   `NumericCondition`: Takes a `contextKey`, an `Operator` (==, !=, <, >, <=, >=), and a target value.
    *   `StringCondition`: Takes a `contextKey`, an `Operator` (==, !=, IN, NOT_IN), and a target value.
3.  Implement a `Rule` which aggregates multiple conditions using AND/OR logic. Short-circuit evaluation should be used (e.g., if the first condition of an AND block is false, don't evaluate the rest).

### Step 4: Build the FeatureFlagManager (Singleton)
1.  **Storage:** Initialize a thread-safe map (`ConcurrentHashMap` in Java) to store `Map<String, FeatureFlag>`.
2.  **Evaluation Logic (`evaluate` method):**
    *   Lookup the flag by key.
    *   If not found, return `defaultValue`.
    *   Identify the `strategyType` of the flag.
    *   Delegate to the appropriate `EvaluationStrategy`, passing the flag's specific configuration and the user's `context`.
3.  **Update Logic (`updateFlag` method):**
    *   Accept a new `FeatureFlag` object.
    *   Replace the old flag object in the concurrent map. Because the `FeatureFlag` objects themselves should be immutable, this simple reference swap is thread-safe and atomic.
    *   Trigger notifications to observers.

### Step 5: Implement Observers
1.  Maintain a `Map<String, List<Observer>>` in the manager to track which observers care about which flags.
2.  Use standard thread-safe list implementations (e.g., `CopyOnWriteArrayList` in Java) to avoid `ConcurrentModificationException` if an observer subscribes/unsubscribes during an active notification broadcast.

### Step 6: Testing
*   Write unit tests for each strategy, particularly verifying the determinism and even distribution of the Percentage Rollout using `hashlib`/`MessageDigest`.
*   Write multi-threaded tests to ensure read operations during concurrent updates do not throw exceptions or return inconsistent state.
