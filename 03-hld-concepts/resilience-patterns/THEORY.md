# Resilience & Fault Tolerance Patterns

## 1. Anatomy of Cascading Failures
Cascading failures occur when a failure in one part of a distributed system causes failures in other parts, leading to a system-wide outage. This typically starts with a localized issue (e.g., a slow database query or a network partition) that increases latency.
- **Thread Pool Exhaustion**: As upstream services wait for the slow downstream service, their thread pools fill up with blocked threads. Once the thread pool is exhausted, the upstream service becomes unresponsive to its own clients, spreading the failure upwards.
- **Resource Starvation**: Increased latency ties up memory, file descriptors, and connections, causing otherwise healthy nodes to crash under the accumulated load.

## 2. Circuit Breaker Pattern
The Circuit Breaker pattern prevents an application from repeatedly trying to execute an operation that is likely to fail. It is modeled as a Finite State Machine with three states:
- **CLOSED**: Requests flow freely. The circuit breaker monitors the failure rate (using a sliding window, e.g., last $N$ requests or last $T$ seconds). If the failure rate exceeds a configured threshold, the state transitions to OPEN.
- **OPEN**: All requests are immediately rejected (fast failure) for a configured reset timeout period. This gives the failing downstream service time to recover.
- **HALF_OPEN**: After the reset timeout expires, the circuit breaker allows a limited number of "probe" requests to pass through. If these probes succeed, the service is deemed healthy, and the state transitions back to CLOSED. If any probe fails, it transitions back to OPEN, and the reset timeout is restarted.

## 3. Bulkhead Isolation Pattern
Inspired by the watertight compartments (bulkheads) of a ship, this pattern isolates components so that a failure in one does not take down the entire system.
- **Semaphore Bulkhead**: Limits the number of concurrent requests to a downstream dependency using a semaphore. It is lightweight but does not protect against thread blocking.
- **Thread Pool Bulkhead**: Assigns a dedicated thread pool and queue for each downstream dependency. If one dependency is slow, only its specific thread pool is exhausted, leaving other pools healthy.
- **Queue Overflow Policies**: When a bulkhead is full, requests can be rejected immediately (fast failure), queued (up to a limit), or routed to a fallback mechanism.

## 4. Exponential Backoff with Jitter
When a request fails, retrying immediately can overwhelm the downstream service (the "thundering herd" problem). Adding delays between retries is essential.
- **Standard Exponential Backoff**: $delay = base\_delay \times 2^{retry\_count}$. While this spaces out retries, multiple clients can still synchronize and retry at the same time.
- **Full Jitter**: $delay = \text{random}(0, base\_delay \times 2^{retry\_count})$. This is often the best approach as it spreads out the load evenly and prevents spikes, mitigating the thundering herd problem.
- **Equal Jitter**: $delay = \frac{1}{2} \times (base\_delay \times 2^{retry\_count}) + \text{random}(0, \frac{1}{2} \times (base\_delay \times 2^{retry\_count}))$. Keeps some backoff while still adding randomness.
- **Decorrelated Jitter**: $delay = \text{random}(base\_delay, delay_{prev} \times 3)$.

## 5. Graceful Fallbacks, Load Shedding, and Dead Letter Queues (DLQ)
- **Graceful Fallbacks**: When a service fails, it may be appropriate to return a fallback response (e.g., a cached value or an empty list). However, this is not a blanket policy. Safe, stale reads require explicit freshness boundaries and permission checks. Conversely, financial or authentication mutations must strictly fail closed to prevent inconsistent states.
- **Load Shedding**: Dropping requests at the server level when the system is near capacity to preserve stability for a subset of users, rather than degrading performance for everyone.
- **Dead Letter Queues (DLQ)**: For asynchronous processing, failed messages that cannot be processed after multiple retries are moved to a DLQ for manual inspection or later reprocessing.
- **Retry Budgets & Deadline/Cancellation Propagation**: Simple retries can amplify load. Retry budgets (e.g., only 10% of requests may be retries) limit the overall retry volume. Deadline propagation ensures that upstream timeouts cancel downstream processing, avoiding wasted work on requests the client has already abandoned.

## 6. Cell-Based Architecture (Staff/Principal Extension)
For massive scale, traditional bulkheads are extended into bounded cell architectures:
- **Stable Tenant-to-Cell Routing**: Users/tenants are mapped to specific cells, ensuring data locality and bounded impact.
- **Per-Cell Capacity & Queue Quotas**: Each cell operates independently with its own strict capacity limits and queues.
- **Blast Radius Example**: If you have 10 equal-load cells, an isolated cell outage affects only 10% of your users.
- **Shared-Dependency Counterexample**: The 10% blast radius assumption is invalidated if all cells rely on a shared router or control plane. If that shared component fails, 100% of the system fails. Thus, truly independent data and control dependencies are critical. Cross-cell operations must be strictly limited.
- **Hot Tenant Migration**: Hot tenants can overload a cell. Migration must be bounded: move specific hot tenants to different cells in a staged rollout, retaining clear resource ownership, rather than indiscriminately moving all tenants at once.

## 7. Interview Scoring Rubric

| Score | Signal | Description |
|-------|--------|-------------|
| 1 | Weak | Fails to identify the root cause of cascading failures. Cannot explain Circuit Breaker states or just mentions "retry". |
| 3 | Solid | Understands Circuit Breaker (CLOSED/OPEN/HALF_OPEN), basic bulkheads, and the need for exponential backoff. Can identify thread pool exhaustion as a risk. |
| 5 | Strong | Deeply understands Full Jitter vs Decorrelated Jitter. Discusses sliding window failure calculations, thread pool vs semaphore bulkheads, and implements robust fallback strategies. |
| 7 | Staff | Explains cell-based architecture, independent data/control dependencies, and tenant migration. Articulates how retry budgets and deadline propagation prevent retry amplification without relying on "service mesh/eBPF" as a crutch. Quantifies blast radius with equal-load and shared-dependency counterexamples. |

## 8. Common Pitfalls
- **Missing Jitter**: Implementing exponential backoff without jitter, causing thundering herds.
- **Infinite Retries**: Failing to cap the maximum number of retries or maximum backoff delay.
- **Improper Circuit Breaker Thresholds**: Setting the failure threshold too low (flapping) or too high (failing to protect the system).
- **Silent Failures**: Falling back to default values without logging or alerting, hiding systemic issues.
- **Blanket Fallbacks for Mutations**: Applying "fallback is always better" logic indiscriminately, causing financial or authorization mutations to incorrectly proceed when they should fail closed.
- **Missing Deadline Propagation**: Failing to cancel downstream work when the upstream client has timed out, causing systems to waste resources processing abandoned requests and amplifying overload.

## 9. Follow-up Questions
1. How do you choose between a thread pool bulkhead and a semaphore bulkhead?
2. Explain how a sliding window calculates the failure rate in a Circuit Breaker.
3. Why is Full Jitter often preferred over Decorrelated Jitter in highly concurrent systems?
4. How do you implement distributed circuit breakers across multiple instances of a microservice?
5. Describe the interaction between a Circuit Breaker and a Load Balancer.
