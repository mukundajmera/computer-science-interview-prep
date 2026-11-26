# Follow-Up Questions: API Gateway

If a candidate finishes the core design quickly, use these follow-up questions to test the depth of their knowledge.

## 1. Dynamic Routing & Discovery
**Question**: "Currently, the routing table is static. How would you modify the system to dynamically route requests based on service discovery (e.g., integrating with a service registry like Consul or Eureka)?"
*   **What to look for**: Introduction of a `ServiceLocator` or `RoutingStrategy` interface. The `ApiGateway` would query this component rather than a static map. Discussion on caching the routing table locally and subscribing to updates to avoid hitting the registry on every request.

## 2. Global vs. Route-Specific Filters
**Question**: "Right now, every route executes the same filter chain. How would you design the system so that some filters apply globally (e.g., Logging), while others only apply to specific routes (e.g., Auth only on `/api/secure`)?"
*   **What to look for**: Splitting filter configuration. The `Route` object might contain a list of route-specific filters. The `FilterChain` builder would merge a list of global filters with the route-specific ones before execution.

## 3. Asynchronous / Non-Blocking Execution
**Question**: "This design uses blocking I/O (each request blocks a thread until the response is ready). How would you modify the filter chain to be fully asynchronous (reactive)?"
*   **What to look for**: Changing the return type of `doFilter` and target handlers from `void` (or `Response`) to `Future<Response>` (Java) or using `async/await` (Python). Discussing how threads are released back to the pool while waiting for backend I/O.

## 4. Retries and Timeouts
**Question**: "How would you implement a retry mechanism and request timeouts within this architecture?"
*   **What to look for**: A `RetryFilter` or `TimeoutFilter`. 
    *   **Retry**: The filter loops around `chain.doFilter()`, catching specific exceptions (like 503s or IO errors) and retrying the chain a set number of times.
    *   **Timeout**: Wrapping the `chain.doFilter()` execution in a construct that interrupts the thread or cancels the future if it takes longer than $X$ milliseconds.

## 5. Streaming Payloads
**Question**: "Currently, the `RequestContext` loads the entire body into memory. How would you handle uploading a 5GB file through the gateway?"
*   **What to look for**: Changing the `body` field from a `String` or `byte[]` to an `InputStream` (Java) or generator/iterator (Python). Recognizing that filters can no longer read the entire body without consuming the stream, requiring specific stream-cloning or chunk-based processing middleware.