# Resilience & Fault Tolerance Patterns - Interview Q&A

1. **Q: How does a circuit breaker prevent cascading failures?**
   **A:** By stopping requests to a failing downstream service before they are sent. This prevents upstream services from wasting resources (threads, connections, memory) waiting for timeouts, which would otherwise lead to thread pool exhaustion and systemic failure.

2. **Q: Explain the states of a Circuit Breaker.**
   **A:** 
   - **CLOSED:** Normal operation; requests pass through. The failure rate is monitored.
   - **OPEN:** The failure rate exceeded the threshold. All requests are immediately rejected (fast failure).
   - **HALF_OPEN:** After a timeout period, a limited number of test requests (probes) are allowed through. If they succeed, the state returns to CLOSED; if they fail, it goes back to OPEN.

3. **Q: What is the difference between a Semaphore Bulkhead and a Thread Pool Bulkhead?**
   **A:** A Semaphore Bulkhead limits concurrent requests using a counter (semaphore) but executes them on the calling thread, meaning blocked requests still tie up the caller's thread. A Thread Pool Bulkhead uses a dedicated pool and queue, completely isolating the caller's threads from the downstream latency, at the cost of higher overhead (context switching).

4. **Q: Why is exponential backoff alone insufficient for retries?**
   **A:** Exponential backoff alone spaces out retries, but if multiple clients experience a failure simultaneously, they will all wait for the exact same exponential delays and retry at the same time, causing a "thundering herd" that overwhelms the recovering service. Jitter (randomness) must be added.

5. **Q: What is "Full Jitter" and why is it effective?**
   **A:** Full Jitter calculates the delay as a random value between 0 and the exponential backoff value: `random(0, base * 2^retry)`. It is highly effective because it distributes the retry load uniformly across the time window, minimizing spikes and preventing synchronized retry bursts.

6. **Q: How do you calculate the failure rate in a Circuit Breaker?**
   **A:** Using a sliding window, typically either count-based (e.g., the last 100 requests) or time-based (e.g., requests in the last 10 seconds). The failure rate is the number of failed requests divided by the total requests in the window. A minimum number of requests must usually be processed before evaluating the threshold.

7. **Q: What is "Load Shedding" and when should it be used?**
   **A:** Load shedding is a server-side pattern where a system intentionally rejects incoming requests when it reaches capacity. It is used to protect the system from crashing under excessive load, ensuring that it remains stable and responsive for at least a subset of traffic rather than degrading completely.

8. **Q: How do timeouts relate to resilience patterns?**
   **A:** Timeouts are the foundational resilience pattern. Without timeouts, threads will block indefinitely waiting for a response, leading to thread pool exhaustion. Circuit breakers often treat a timeout as a failure when calculating the failure rate.

9. **Q: What is a graceful fallback? Give an example.**
   **A:** A graceful fallback provides an alternative response when a primary operation fails. For example, if a recommendation engine fails to return personalized results for a user, the fallback could be to return a pre-computed list of globally popular items instead of throwing an error (safe stale read). However, graceful fallbacks are not appropriate for mutations—financial or authentication transactions must fail closed to prevent inconsistent states.

10. **Q: How would you handle a distributed circuit breaker scenario?**
    **A:** In a cluster of microservices, each instance usually maintains its own local circuit breaker state. While a centralized distributed state (e.g., using Redis) is possible, it adds latency and a single point of failure. It is generally better to rely on local circuit breakers and let the load balancer route traffic away from failing nodes.

11. **Q: Explain cell-based architecture and its blast radius assumptions.**
    **A:** Cell-based architecture partitions users (stable tenant-to-cell routing) into bounded cells with independent capacity and queue quotas. For example, if there are 10 equal-load cells, an isolated cell outage affects exactly 10% of users. However, this assumption is broken by shared dependencies—if all 10 cells rely on a single shared router or control plane and it fails, 100% of the system fails. Thus, cells must have independent data and control dependencies and strictly limited cross-cell operations.

12. **Q: How should you handle a "hot tenant" that is overwhelming a cell?**
    **A:** Rather than moving all tenants at once (which breaks bounded resources and causes thundering herds), you use bounded hot tenant migration: you remap the specific hot tenant to a new or less-loaded cell using a staged rollout while keeping the resource ownership clear.

13. **Q: What is retry amplification and how do you prevent it?**
    **A:** Retry amplification occurs when overloaded systems cause timeouts, triggering clients to retry requests, thereby multiplying the load and worsening the overload. To prevent it, you use a **Retry Budget** (capping the ratio of retries to normal requests, e.g., 10%) and **Deadline/Cancellation Propagation** (passing the remaining time to downstream services so they can cancel processing if the client has already timed out and abandoned the request).
