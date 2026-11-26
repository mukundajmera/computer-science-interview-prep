# Evaluation Rubric: API Gateway & Middleware Pipeline

## Grading Criteria

Evaluate the candidate's design and implementation based on the following criteria.

### 1. Architecture & Design Patterns (30%)
*   **Excellent**: Correctly identifies and implements the **Chain of Responsibility** (or Interceptor) pattern. Clean separation between the engine (`FilterChain`) and behavior (`Filters`). Context objects are well-defined and framework-agnostic.
*   **Satisfactory**: Implements a pipeline, but it might be tightly coupled (e.g., hardcoding specific filters in a specific order within the gateway class). Context objects exist but might leak abstraction.
*   **Needs Improvement**: Fails to use a sequence pattern. Logic for auth, logging, and routing is tangled in a single massive method.

### 2. Core Functionality: Short-Circuiting & Post-Processing (25%)
*   **Excellent**: Clearly demonstrates how a filter can halt the chain (short-circuit) and return early (e.g., Auth failure). Also demonstrates how filters can act on the response *after* the handler executes (e.g., Logging latency).
*   **Satisfactory**: Handles short-circuiting correctly but struggles with post-processing, or vice-versa.
*   **Needs Improvement**: Filters only run one way. Cannot halt the chain early; target is always executed.

### 3. State Management & Thread Safety (20%)
*   **Excellent**: Understands that filters (like a Circuit Breaker or Rate Limiter) hold state. Uses appropriate thread-safe constructs (e.g., `AtomicInteger`, `ConcurrentHashMap`, or explicit locking) when implementing stateful filters.
*   **Satisfactory**: Acknowledges concurrency when prompted but might use non-thread-safe data structures in their implementation.
*   **Needs Improvement**: Ignores concurrency entirely; stateful filters would break under load.

### 4. Error Handling (15%)
*   **Excellent**: Pipeline execution is wrapped in global error handling. If any filter or the backend handler throws a runtime exception, it is caught, and a structured 500 error is returned to the client without crashing the gateway.
*   **Satisfactory**: Basic try-catch blocks exist, but errors might not be normalized into a consistent HTTP response format.
*   **Needs Improvement**: Unhandled exceptions bubble up and crash the process or return empty responses.

### 5. Code Quality & Extensibility (10%)
*   **Excellent**: Adding a new filter requires zero changes to the core routing or pipeline engine (Open/Closed Principle). Code is clean, DRY, and well-named.
*   **Satisfactory**: Adding a new filter requires minor modifications to a central configuration switch statement.
*   **Needs Improvement**: Highly coupled; adding a filter requires modifying multiple core classes.

## Red Flags
*   **Framework Dependency**: Candidate attempts to pull in Spring Boot, Express.js, or similar frameworks to solve the problem, rather than designing the low-level components themselves.
*   **Infinite Loops**: Poor implementation of the `FilterChain` iterator leads to infinite recursion or `StackOverflowError`.