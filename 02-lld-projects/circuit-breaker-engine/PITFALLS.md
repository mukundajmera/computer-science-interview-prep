# Common Pitfalls: Circuit Breaker Engine

When implementing a Circuit Breaker, developers frequently encounter several specific challenges and traps.

## 1. Concurrency Bugs in State Transitions

The most common failure point is handling state transitions under heavy concurrent load.

*   **The "Thundering Herd" in Half-Open:** When the timeout expires in the `OpenState`, the next request should transition the breaker to `HalfOpenState`. However, if 100 threads are waiting and they all check `hasTimeoutExpired()` simultaneously, they might all evaluate it as true before the state is updated. If the implementation doesn't use atomic operations (like compare-and-swap) to change the state to Half-Open, *all 100* threads might be allowed through as "test" requests, defeating the purpose of the Half-Open state.
*   **Lost Updates on Counters:** In the `ClosedState`, using `failures++` without synchronization in Java/C++ (or equivalent non-atomic increments) will lead to lost updates under load. The threshold might be 10, but 15 failures might pass through before the breaker trips because threads overwrote each other's increments.

## 2. Blocking Calls in the Circuit Breaker Logic

The Circuit Breaker is meant to *prevent* resource exhaustion, so its internal logic must be exceptionally fast and non-blocking.

*   **Using `Thread.sleep()` in Open State:** A critical mistake is making the `OpenState` actively wait (e.g., sleeping the thread) until the timeout expires. The `OpenState` must fail *immediately* (fail-fast) if the timeout hasn't expired. It should only check a timestamp, not block the calling thread.
*   **Heavy Locking:** Wrapping the entire `execute()` method in a giant `synchronized` block ensures safety but serializes all requests. If the underlying service takes 50ms, a synchronized circuit breaker will only process 20 requests per second across the entire application, creating a massive artificial bottleneck.

## 3. Swallowing Exceptions

When the Circuit Breaker wraps a call, it must be careful about how it handles exceptions thrown by the underlying service.

*   **Losing the Original Error:** If the underlying service throws an `IOException` (e.g., Connection Refused), the circuit breaker needs to record the failure but must *re-throw* that `IOException` to the caller. If the wrapper catches it and throws a generic `RuntimeException` without preserving the original cause, debugging the upstream issue becomes impossible.
*   **Not Differentiating Failure Types:** In a real-world scenario (though often outside the scope of a basic interview implementation), not all exceptions should trip the breaker. A `400 Bad Request` (client error) usually shouldn't count towards the failure threshold, whereas a `500 Internal Server Error` or a Timeout should.

## 4. Tight Coupling

*   **Hardcoding Fallbacks:** Hardcoding the fallback logic directly inside the `execute` method makes the circuit breaker useful for only one specific use case. The fallback logic should be injected (Strategy Pattern) so the breaker remains generic.
*   **Mixing State Logic:** Putting all the logic for counting, timeouts, and execution inside a single monolithic `CircuitBreaker` class makes the code complex and brittle. Failing to use the State pattern makes adding new states or modifying transition logic very difficult.