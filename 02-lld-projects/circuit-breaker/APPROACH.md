# Approach

## Analyzing the Requirements

A Circuit Breaker is essentially a state machine coupled with a sliding window metric aggregator. The primary challenge is efficiently tracking metrics (successes, failures, durations) in real-time and updating the state based on those metrics, while minimizing synchronization overhead in a concurrent environment.

The system must handle potentially high throughput without becoming a bottleneck. This means the metric aggregation and state evaluation must be extremely fast.

## Sliding Window Implementations

### Count-Based Sliding Window

A count-based sliding window tracks the outcome of the last N calls. This can be implemented using a circular buffer (ring buffer) or a simple array with a moving pointer. When a new call completes, its result overwrites the oldest result in the buffer, and the aggregate metrics are updated.

This approach is simple and memory-efficient. However, if the system has low traffic, old failures might remain in the buffer for a long time, preventing the circuit from closing.

### Time-Based Sliding Window

A time-based sliding window tracks calls within a rolling time frame (e.g., the last 10 seconds). This can be implemented by dividing the window into smaller, fixed-size time buckets (e.g., 10 buckets of 1 second each).

When a call completes, its metrics are added to the current bucket. Periodically, or on access, older buckets that fall outside the window are discarded, and the aggregate metrics are updated. This approach handles varying traffic patterns better but requires more memory and slightly more complex logic to manage the buckets.

## State Management and Concurrency

State transitions must be atomic. For example, when the failure threshold is breached, only one thread should transition the state from `CLOSED` to `OPEN` and schedule the timer for `HALF_OPEN`.

In Java, this can be achieved using `AtomicReference` for the state or by using `synchronized` blocks. However, updating metrics on every call using a global lock can create a bottleneck. Therefore, we should prefer lock-free data structures or fine-grained locking.

A common pattern is to use LongAdder for metric counters and update them concurrently. State evaluation can be done lazily when a new call arrives or synchronously after a metric update.

## Fallback Mechanism

A fallback mechanism allows the application to gracefully degrade when the circuit is open or a call fails. This is typically implemented as a decorator or wrapper around the target execution, catching exceptions (like `CircuitBreakerOpenException`) and invoking a provided fallback function.

## Bounded Behavior Constraints
To ensure deterministic behavior across implementations, the design enforces the following constraints:
- **Monotonic Time**: Injected monotonic time drives traces (e.g., closed→open→half-open→closed/open). Threshold/window semantics and allowed half-open probes are strictly exact.
- **Probe Bounds & Generations**: When multiple contenders attempt a half-open probe (e.g., eight contenders), they cannot exceed the configured half-open probe bound. Furthermore, stale success/failure callbacks from a previous breaker generation cannot overwrite a later breaker generation's state.
