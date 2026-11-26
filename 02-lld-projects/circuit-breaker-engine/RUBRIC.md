# Interview Evaluation Rubric: Circuit Breaker Engine

This rubric is designed to help interviewers evaluate a candidate's design and implementation of the Circuit Breaker Engine.

## 1. Core State Machine Logic (30%)

| Level | Description |
| :--- | :--- |
| **Fail** | Fails to implement the three core states (Closed, Open, Half-Open). Transitions are missing or fundamentally flawed (e.g., gets stuck in Open state permanently). |
| **Pass** | Implements the basic states. Transitions occur correctly based on failure thresholds and timeouts. May have minor bugs in edge cases (e.g., timer logic in Open state is slightly off). |
| **Strong** | Cleanly separates states using the State design pattern. Transitions are robust. Correctly handles the single test request logic in Half-Open state and transitions appropriately on its success or failure. |

## 2. Concurrency and Thread Safety (30%)

| Level | Description |
| :--- | :--- |
| **Fail** | Completely ignores thread safety. Uses standard variables for counters and state without synchronization, leading to guaranteed race conditions and incorrect failure counts in a multi-threaded environment. |
| **Pass** | Attempts thread safety using basic locks (e.g., `synchronized` methods, `ReentrantLock`), which makes the implementation correct but potentially creates a significant performance bottleneck under high load. |
| **Strong** | Employs fine-grained concurrency controls. Uses Atomic variables (like `AtomicInteger` for counts, `AtomicReference` for state) or highly optimized locking mechanisms to ensure safety with minimal performance overhead. Handles transition race conditions gracefully. |

## 3. Extensibility and Pattern Usage (20%)

| Level | Description |
| :--- | :--- |
| **Fail** | Monolithic class with heavy `if/else` or `switch` statements for state logic. Hard to read and impossible to extend without modifying core code. |
| **Pass** | Uses basic object-oriented principles. Might use a State pattern but mixes concerns (e.g., the State classes also contain retry logic or business logic). |
| **Strong** | Excellent use of patterns. Uses State pattern cleanly for circuit logic. Uses Proxy/Decorator for the execution wrapper. Uses Strategy pattern for fallbacks or retries, demonstrating how new resilience features can be added without modifying the core breaker. |

## 4. Execution API and Error Handling (10%)

| Level | Description |
| :--- | :--- |
| **Fail** | API is cumbersome to use. Fails to propagate underlying exceptions correctly or swallows errors unintentionally. |
| **Pass** | API works but might be rigid (e.g., only accepts `Runnable` and not `Callable`). Basic exception handling is present. |
| **Strong** | Provides a clean, flexible API (e.g., using generics to return values). Distinct custom exceptions (like `CircuitBreakerOpenException`) are used to differentiate circuit breaker rejections from underlying service failures. |

## 5. Testing and Validation (10%)

| Level | Description |
| :--- | :--- |
| **Fail** | No tests provided, or tests only cover the trivial happy path (staying in Closed state). |
| **Pass** | Basic unit tests cover the primary transitions (Closed -> Open -> Half-Open -> Closed). |
| **Strong** | Comprehensive test suite including unit tests for individual states, integration tests for the full lifecycle, and specifically, concurrency tests demonstrating the thread safety of the implementation under load.