# Follow-Up Questions

## 1. How would you distribute the Circuit Breaker state across a cluster?

In a distributed environment, each application instance typically maintains its own local circuit breaker state. This is because the circuit breaker protects the local resource pool and network connection.

However, if you want a global view, you could use a centralized store like Redis to aggregate metrics. This introduces latency and a single point of failure. A hybrid approach is to maintain local state but asynchronously gossip or push metrics to a central coordinator that can optionally force local circuit breakers to open if the global failure rate is high. *(Note: This is an unimplemented extension in this codebase).*

## 2. How can we optimize the time-based window for extremely high throughput?

Instead of using a bucket-based sliding window which requires synchronization to shift buckets, we can use an exponentially decaying reservoir or probabilistic data structures.

Alternatively, we can use thread-local accumulators. Each thread aggregates its own successes and failures, and a background thread periodically sweeps and aggregates these thread-local counters into the global state. This eliminates contention entirely during the critical path of execution. *(Note: Thread-local accumulation is an unimplemented extension).*

## 3. How do you handle different types of exceptions?

Not all exceptions should trigger the circuit breaker. For example, a `400 Bad Request` indicates a client error, not a backend failure. A `503 Service Unavailable` or an `IOException` indicates a backend issue.

We can enhance the configuration to accept a list of exceptions to ignore or a custom predicate (e.g., `Predicate<Throwable>`) to evaluate whether an exception should be counted as a failure. *(Note: Advanced exception filtering beyond `CircuitBreakerOpenException` is an unimplemented extension).*
