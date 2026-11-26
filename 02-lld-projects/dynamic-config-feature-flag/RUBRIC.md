# Rubric: Dynamic Configuration & Feature Flag Service

## 1. Feature Flag Evaluation (30%)
*   **Excellent:** Implements all strategies (Boolean, Percentage, Allowlist, Rule-based) correctly. Rule engine supports complex nested conditions with correct short-circuiting. Percentage rollout is provably deterministic and uses a stable hashing algorithm. Defaults are handled gracefully.
*   **Good:** Implements Boolean, Allowlist, and Percentage correctly, but Rule-based evaluation is basic or missing. Percentage rollout might use a standard `Random` seeded by userId rather than a proper string hash, which can lead to clustering issues.
*   **Needs Improvement:** Fails to implement percentage rollouts deterministically. Does not handle default fallbacks.

## 2. Dynamic Updates & Concurrency (25%)
*   **Excellent:** Updates are applied atomically without blocking reads. Uses thread-safe data structures (`ConcurrentHashMap`, `CopyOnWriteArrayList`, etc.) appropriately. Strong test cases demonstrate thread safety under heavy read/write load.
*   **Good:** Uses basic synchronization (locks/mutexes) that might bottleneck read performance during updates, but is thread-safe.
*   **Needs Improvement:** Standard collections are used without locking, leading to `ConcurrentModificationException` or race conditions in a multi-threaded environment.

## 3. Design Patterns & Architecture (20%)
*   **Excellent:** Clean separation of concerns. Properly utilizes Strategy for evaluation, Observer for updates, and Singleton for the manager. Code is highly extensible; adding a new strategy requires zero changes to the core manager.
*   **Good:** Uses most patterns, but might have tight coupling (e.g., a massive `switch` statement in the manager instead of polymorphic strategies).
*   **Needs Improvement:** Monolithic design. Manager handles parsing, evaluation, and storage in a single class.

## 4. Code Quality & Testing (15%)
*   **Excellent:** Code is clean, well-documented, and follows language conventions. Comprehensive unit tests cover edge cases (missing attributes, malformed rules). Determinism tests for percentage rollouts are present.
*   **Good:** Code is readable. Basic tests exist but miss edge cases or concurrent testing.
*   **Needs Improvement:** Sparse documentation, messy code, missing or failing tests.

## 5. Standard Library Compliance (10%)
*   **Excellent:** Strictly uses Java 11+ / Python 3.8+ standard libraries. No external dependencies (e.g., no Guava, no third-party rule engines).
*   **Needs Improvement:** Injects external libraries for core functionality (hashing, collections, rules).
