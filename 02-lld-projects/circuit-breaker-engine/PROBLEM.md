# Problem Statement: Circuit Breaker & Resilience Engine

## Background
In modern distributed systems, remote calls (like HTTP requests to microservices, database connections, or 3rd-party API integrations) can fail or experience significant latency due to network issues, service degradation, or outages. If a service repeatedly tries to call a failing upstream service, it can lead to resource exhaustion (like thread pool depletion), cascading failures across the system, and a poor user experience. 

To prevent this, the **Circuit Breaker** pattern is used. It acts like an electrical circuit breaker: when consecutive failures cross a threshold, the breaker "trips" (opens), preventing further calls to the failing service and immediately returning an error or a fallback response. After a timeout, it allows a limited number of test requests to see if the service has recovered.

## Task
Design and implement an in-memory Circuit Breaker and Resilience Engine. This engine should wrap arbitrary callable actions (like remote procedure calls) and protect the system by failing fast when the underlying service is unhealthy.

Your implementation must support the following core states and transitions:
1.  **CLOSED**: The circuit is closed, and requests are allowed to pass through to the underlying service.
    *   If a request succeeds, the failure count is reset.
    *   If a request fails, the failure count is incremented.
    *   If the failure count reaches a configured `failureThreshold`, the circuit transitions to the **OPEN** state.
2.  **OPEN**: The circuit is open. Requests are *not* allowed to pass through and immediately fail (e.g., throwing a `CircuitBreakerOpenException`) or return a fallback response.
    *   A timer is started when transitioning to this state.
    *   After a configured `resetTimeout` has elapsed, the circuit transitions to the **HALF-OPEN** state.
3.  **HALF-OPEN**: The circuit is testing the waters. A limited number of requests are allowed to pass through to check if the underlying service has recovered.
    *   If a request succeeds, the circuit transitions back to the **CLOSED** state.
    *   If a request fails, the circuit immediately transitions back to the **OPEN** state, and the `resetTimeout` timer restarts.

## Functional Requirements
1.  **Execution Wrapper**: The engine should provide a way to execute an action (e.g., a function or a callable object) through the circuit breaker.
2.  **Configurability**: Users should be able to configure:
    *   `failureThreshold`: The number of consecutive failures before opening the circuit.
    *   `resetTimeout`: The time to wait in the OPEN state before transitioning to HALF-OPEN.
    *   (Optional but recommended) The number of permitted calls in the HALF-OPEN state.
3.  **Fallback Mechanism**: Support registering a fallback action that is executed when the circuit is OPEN or when the primary action fails.
4.  **Resilience Strategies**: Implement at least one additional resilience pattern (e.g., simple retries before recording a failure against the circuit breaker).

## Non-Functional Requirements
1.  **Thread Safety**: The circuit breaker will be used in a highly concurrent environment. State transitions and metric tracking (failure counts) must be thread-safe to prevent race conditions.
2.  **Performance**: The overhead of passing a call through the circuit breaker should be minimal. Avoid excessive locking that could become a bottleneck.
3.  **Standard Libraries Only**: Do not use external libraries like Resilience4j, Hystrix, or Polly. Implement the logic using language standard libraries (Java 11+ or Python 3.8+).

## Architectural Patterns
You are expected to utilize appropriate design patterns. Consider:
*   **State Pattern**: To manage the behavior of the circuit breaker depending on its current state (Closed, Open, Half-Open).
*   **Proxy or Decorator Pattern**: To wrap the target function and intercept calls to manage success/failure recording and circuit state.
*   **Strategy Pattern**: To define different failure handling or fallback strategies.