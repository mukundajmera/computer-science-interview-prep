# Follow-Ups: API Gateway

## Potential Interview Extensions (Unimplemented Extensions)

*Note: The following topics represent unimplemented extensions and are not present in the baseline implementation.*

1. **Distributed Rate Limiting (Unimplemented):**
   - *Question:* How would you extend the rate limiter to work across multiple gateway instances?
   - *Answer:* Introduce a distributed cache like Redis. Use a Lua script to evaluate the rate limit atomically across all gateway nodes, changing the state from in-memory maps to Redis keys (e.g., using a leaky bucket or token bucket algorithm to save space compared to sliding window logs).

2. **Dynamic Configuration (Unimplemented):**
   - *Question:* How would you handle adding new routes or changing rate limit thresholds without restarting the gateway?
   - *Answer:* Use a configuration management system (like Consul or ZooKeeper) or a background thread that periodically polls a database. We would update the internal `routes` and `filters` structures dynamically. We would use `CopyOnWriteArrayList` or swap references atomically to ensure current requests aren't disrupted during the update.

3. **Request Payload Transformation (Unimplemented):**
   - *Question:* A client sends XML but the backend expects JSON. How would you handle this?
   - *Answer:* Implement a specific Pre-Filter for transformation. It would read the request body, convert the payload, update the `Content-Type` header, and pass the mutated request down the chain.

4. **Retry Mechanisms (Unimplemented):**
   - *Question:* How would you implement a retry logic for transient backend failures?
   - *Answer:* Implement a Retry Filter that wraps the dispatch call. It would catch exceptions or 5xx responses and retry the dispatch loop, ideally using an exponential backoff strategy. The retry filter needs to coordinate with the circuit breaker to ensure it doesn't bypass an OPEN state.

5. **Timeout Handling (Unimplemented):**
   - *Question:* How do you ensure the gateway doesn't hang indefinitely if a backend is slow?
   - *Answer:* Use asynchronous non-blocking I/O (like Netty) or configure strict timeouts on the HTTP client used for dispatching. If a timeout occurs, the gateway catches the timeout exception, increments the circuit breaker failure count, and returns a 504 Gateway Timeout response.
