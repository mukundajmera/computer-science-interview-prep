# Code Walkthrough

This document outlines the verified version progression for the Circuit Breaker implementation.

## Version Delta Table

| Version | Description | Key Additions | Performance Complexity |
|---|---|---|---|
| `v1-basic` | Simple count-based sliding window | Basic State Machine (`CLOSED`, `OPEN`, `HALF_OPEN`), count-based metric aggregation. | `O(1)` per call |
| `v2-extended` | Time-based sliding window | Circular array of time buckets, timestamp-based shifting. | `O(N)` window shift where N is bucket count; `O(1)` execution |
| `v3-optimized` | Slow calls, Fallbacks, Concurrency | Atomic state transitions (`AtomicReference`), concurrent metrics (`AtomicInteger`), fallback execution. | Lock-free reads, low-contention writes |

## Entry APIs

The core entry point for the Circuit Breaker is the `execute` method in the `CircuitBreaker` class.

**Java Signature (`v3-optimized`):**
```java
public <T> T execute(Callable<T> callable, Fallback<T> fallback) throws Exception;
```

**Python Signature (`v3-optimized`):**
```python
def execute(self, callable_func: Callable, fallback: Optional[Callable] = None) -> Any:
```

## Correctness Invariants
1. **Self-Rejection Exclusion:** When the state is `OPEN`, the circuit breaker throws a `CircuitBreakerOpenException` (or similar fast-fail exception). This exception is explicitly excluded from the metrics aggregator.
2. **Atomic Transitions:** State transitions (e.g., `CLOSED` to `OPEN`) occur exactly once. If multiple threads concurrently detect a threshold breach, only one thread successfully updates the `AtomicReference` (Java) or acquires the `Lock` (Python).
3. **Half-Open Permit Limits:** In the `HALF_OPEN` state, a strict atomic counter limits the number of permitted test calls to prevent stampeding a recovering backend.
4. **Window Memory Bound:** The time-based sliding window uses a pre-allocated fixed-size array of buckets, preventing unbounded memory growth.

## Complexity
- **Time Complexity:** The critical path of checking state and updating metrics in a single bucket is `O(1)`. Shifting the time-based window requires iterating over the buckets, which is bounded by the fixed window size `O(W)`.
- **Space Complexity:** The memory footprint is `O(W)`, where `W` is the number of buckets in the sliding window. Memory allocation is localized to initialization, preventing garbage collection spikes.

## 45-Minute Interview Pacing
- **0-10m:** Problem clarification, state machine definition (`CLOSED`, `OPEN`, `HALF_OPEN`), and API design.
- **10-25m:** Implementing the core state machine and the sliding window metrics (focusing on count-based or a simplified time-based approach).
- **25-35m:** Concurrency handling: identifying critical sections, applying atomic variables or fine-grained locks to prevent race conditions without serializing throughput.
- **35-45m:** Edge cases (self-rejection exclusion, half-open stampedes) and optional features (fallbacks, slow call tracking).
