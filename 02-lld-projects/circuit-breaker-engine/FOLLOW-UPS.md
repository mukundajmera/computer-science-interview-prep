# Follow-up Questions: Circuit Breaker Engine

Once a candidate has completed the core implementation, these follow-up questions can be used to probe their understanding of advanced resilience concepts and distributed systems.

## 1. Sliding Window vs. Consecutive Failures

*   **Question:** Right now, your circuit breaker trips based on *consecutive* failures. If a service succeeds 100 times, fails 4 times, succeeds 1 time, and fails 4 times, a breaker configured for 5 consecutive failures won't trip, even though the error rate is high. How would you modify your design to trip based on an *error rate* (e.g., > 50% failures in the last 10 seconds)?
*   **What to look for:** Look for discussions about sliding windows. A strong candidate will mention time-based sliding windows (using a circular array of buckets representing seconds) or count-based sliding windows. They should recognize that calculating percentages requires tracking both successes and failures within that window, and they must address the increased complexity of thread-safe counter aggregation across window buckets.

## 2. Dynamic Configuration

*   **Question:** In production, we don't want to restart the application just to change the `failureThreshold` or `resetTimeout`. How would you make these configurations dynamic so they can be updated at runtime?
*   **What to look for:** They should suggest making the `CircuitBreakerConfig` mutable (in a thread-safe way) or allowing the context to swap out the config object atomically (e.g., using `AtomicReference<CircuitBreakerConfig>`). They should discuss how a change to the config affects the *current* state (e.g., if the timeout is shortened while the circuit is OPEN, should it immediately transition to HALF-OPEN?).

## 3. The Bulkhead Pattern

*   **Question:** Even with a circuit breaker, if a service is slow (but not throwing errors), it can still tie up all our application's threads waiting for responses, causing a localized outage. How can we protect against this resource exhaustion?
*   **What to look for:** The candidate should identify the Bulkhead pattern. They should explain how limiting the number of concurrent executions allowed through the circuit breaker (e.g., using a `Semaphore` or a bounded thread pool) prevents one slow dependency from consuming all available system resources.

## 4. Exception Filtering (Ignore vs. Record)

*   **Question:** Not all exceptions mean the upstream service is failing. For example, if we call an API and get a `400 Bad Request` because we sent invalid data, that's our fault, not the upstream service's fault. How would you alter your design to only count certain exceptions (like timeouts or 500s) as failures?
*   **What to look for:** They should propose modifying the configuration to accept a predicate or a list of classes (`Predicate<Throwable> recordException`). In the execution loop, before calling `onError`, they would check if the thrown exception matches the predicate. If it doesn't, they might call `onSuccess` (since the service successfully responded, even if it was a 400) or simply ignore it for tracking purposes.

## 5. Distributed Circuit Breakers

*   **Question:** We have 50 instances of our application running. Each instance maintains its own in-memory circuit breaker. This means if a dependency goes down, all 50 instances have to hit it and fail independently before they all open their breakers. How would you design a *distributed* circuit breaker where the state is shared across all instances?
*   **What to look for:** This shifts the discussion to High Level Design (HLD). They should mention external storage (like Redis) for tracking failures. They must identify the massive latency and scalability issues of checking Redis *synchronously* on every request. A strong answer involves an asynchronous model: instances publish their metrics to a centralized service, which computes the state and broadcasts it back (or instances poll it asynchronously), sacrificing strict consistency for performance.