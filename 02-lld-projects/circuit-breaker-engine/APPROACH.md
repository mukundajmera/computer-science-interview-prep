# Implementation Approach: Circuit Breaker Engine

This document outlines the step-by-step approach to implementing the Circuit Breaker Engine, focusing on core functionality, state management, thread safety, and extensibility.

## Phase 1: Core Domain and Configuration

1.  **Define the Configuration:**
    *   Create a `CircuitBreakerConfig` class (or data class/named tuple in Python, record in Java) to hold the core settings:
        *   `failureThreshold`: Number of consecutive failures before opening.
        *   `resetTimeout`: Time (in ms) to wait in OPEN state before transitioning to HALF-OPEN.
        *   `permittedNumberOfCallsInHalfOpenState`: (Optional) How many test calls to allow. Defaults to 1 for simplicity.

2.  **Define the Engine Interface:**
    *   Create a `CircuitBreaker` interface or abstract class defining the main API:
        *   `execute(callable)`: Executes the given callable if the circuit allows it.
        *   `getState()`: Returns the current state (useful for monitoring/testing).

## Phase 2: Implementing the State Pattern

This is the most critical part. We need to implement the three states and manage transitions cleanly.

1.  **Define the State Interface:**
    *   Create a `CircuitBreakerState` interface. It needs methods to interact with the execution flow:
        *   `canExecute()` (or `acquirePermission()`): Returns a boolean indicating if a call is currently allowed.
        *   `onSuccess(circuitBreakerContext)`: Called when an execution succeeds.
        *   `onError(exception, circuitBreakerContext)`: Called when an execution fails.

2.  **Implement Closed State:**
    *   Maintains a counter for consecutive failures.
    *   `canExecute()` always returns `true`.
    *   `onSuccess()` resets the failure counter to 0.
    *   `onError()` increments the failure counter. If the counter reaches `config.failureThreshold`, it triggers a transition on the context to `OpenState`.

3.  **Implement Open State:**
    *   Records the time it was entered (timestamp).
    *   `canExecute()` checks if the current time is greater than `enterTime + config.resetTimeout`.
        *   If no, returns `false`.
        *   If yes, triggers a transition on the context to `HalfOpenState` and returns `true` (allowing the first test request).
    *   `onSuccess()` / `onError()` generally shouldn't be called directly while in Open state unless it's transitioning.

4.  **Implement Half-Open State:**
    *   Maintains a counter for test requests (if allowing more than 1). For simplicity, we can just track a single test request.
    *   `canExecute()` returns `true` for a limited number of calls, then `false`.
    *   `onSuccess()` immediately transitions the context to `ClosedState`.
    *   `onError()` immediately transitions the context back to `OpenState`.

## Phase 3: The Context and Execution Wrapper

1.  **Implement the Circuit Breaker Context:**
    *   Create the main `CircuitBreakerImpl` class.
    *   It holds a reference to the `CircuitBreakerConfig` and the current `CircuitBreakerState`.
    *   **Crucial:** Ensure the reference to the current state is thread-safe (e.g., `AtomicReference` in Java).

2.  **Implement the Execution Logic (`execute` method):**
    *   The `execute(callable)` method handles the flow:
        ```python
        # Conceptual Python-like pseudocode
        if not currentState.canExecute():
            # Handle rejection (throw exception or invoke fallback)
            raise CircuitBreakerOpenException()
            
        try:
            result = callable()
            currentState.onSuccess(self)
            return result
        except Exception as e:
            # Optionally check if exception should be ignored
            currentState.onError(e, self)
            raise e
        ```

## Phase 4: Concurrency and Thread Safety Refinement

1.  **Atomic Counters:** Ensure that failure counters in `ClosedState` use atomic operations (e.g., `AtomicInteger` in Java, or carefully synchronized blocks/locks if standard library lacks simple atomics for the specific use case) to prevent lost updates under high load.
2.  **State Transition Races:** Handle the scenario where multiple threads try to transition the state simultaneously (e.g., two threads hit the failure threshold at the exact same time). Using `AtomicReference.compareAndSet()` (Java) or explicit locks during transition logic ensures only one thread actually performs the transition and setups the new state correctly.

## Phase 5: Adding Resilience Strategies (Decorator/Proxy)

1.  **Fallback Strategy:**
    *   Create a mechanism to wrap the `execute` call. If a `CircuitBreakerOpenException` or the underlying call fails, invoke a registered fallback function instead of propagating the error.

2.  **Retry Strategy:**
    *   Create a wrapper that attempts to execute the callable multiple times before finally letting the error propagate to the Circuit Breaker to be counted as a failure. 
    *   *Note on ordering:* Typically, Retry is placed *inside* the Circuit Breaker (Retry attempts the call; if all retries fail, the CB records 1 failure) or *outside* (CB wraps the call; if CB is open or call fails, Retry tries again later). For this engine, wrapping the raw call with retry *before* the CB evaluates it is a common approach.

## Phase 6: Testing

1.  **Unit Tests:** Thoroughly test each state independently.
2.  **Integration Tests:** Test the full flow:
    *   Start Closed -> Fail N times -> Verify Open.
    *   Verify Open rejects calls immediately.
    *   Wait timeout -> Verify Half-Open allows test call.
    *   Test call succeeds -> Verify Closed.
    *   Test call fails -> Verify Open again.
3.  **Concurrency Tests:** Spawn multiple threads simulating concurrent requests to ensure failure counts are accurate and state transitions happen exactly once under contention.