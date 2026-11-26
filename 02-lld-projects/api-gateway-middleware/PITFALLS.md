# Common Pitfalls: API Gateway & Middleware

When designing an API Gateway middleware pipeline, candidates frequently make the following mistakes.

## 1. Tight Coupling in the Gateway
Instead of building a flexible chain, candidates might hardcode the middleware logic directly into the gateway's routing loop.
*   **Anti-Pattern**:
    ```java
    public void routeRequest(Request req) {
        if (!auth(req)) return 401;
        if (!rateLimit(req)) return 429;
        log(req);
        Response res = target.execute(req);
        return res;
    }
    ```
*   **Why it's bad**: This violates the Open/Closed Principle. Every time a new middleware is needed, or the order needs to change, the core gateway code must be modified and redeployed.

## 2. One-Way Filters (No Post-Processing)
Candidates often design filters that can only act *before* the backend handler executes.
*   **Anti-Pattern**: The `FilterChain` iterates through all filters, and only *then* calls the handler. The filters cannot inspect the final response.
*   **Correction**: The `doFilter` method should pass the `chain` itself. The filter calls `chain.doFilter()`, waits for it to return, and then executes its post-processing logic.

## 3. Ignoring State and Concurrency
Middleware like Rate Limiters and Circuit Breakers must maintain state (e.g., token buckets, failure counts) across multiple concurrent requests.
*   **Anti-Pattern**: Using standard `int` counters or `HashMap` in a multi-threaded environment.
*   **Correction**: State within singleton filters must use concurrency primitives (e.g., `ConcurrentHashMap`, `AtomicInteger`, or `threading.Lock`).

## 4. Poor Context Abstraction
Tying the system too closely to a specific transport protocol or framework implementation.
*   **Anti-Pattern**: Passing a raw socket or a mock `HttpServletRequest` through the chain.
*   **Correction**: Create a clean, framework-agnostic `HttpContext` object that encapsulates only the necessary data (headers, body, URI, status code).

## 5. Unhandled Exceptions Breaking the Chain
If a filter or the target handler throws an unexpected exception, it might crash the thread or the entire gateway if not caught properly.
*   **Correction**: The gateway engine (or a specialized top-level Error Filter) must wrap the execution chain in a `try/catch` and translate exceptions into standard 500 HTTP responses.