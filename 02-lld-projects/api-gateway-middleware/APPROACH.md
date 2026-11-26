# Approach: API Gateway & Middleware Pipeline

## How to Approach This Problem

When tackling the API Gateway middleware design in an interview, candidates should follow a structured approach, starting from the core abstractions and building outwards.

### Step 1: Define the Domain Models (The Context)
Start by defining the data that flows through the system.
*   **Action**: Create `Request` and `Response` objects.
*   **Why**: A gateway's primary job is to mutate or inspect requests and responses. Wrapping these in a context object (`HttpContext`) provides a clean, unified parameter to pass through the pipeline.
*   **Tip**: Avoid coupling to specific web frameworks (like ServletRequest). Define clean POJOs/dataclasses.

### Step 2: Establish the Pipeline Abstraction (The Pattern)
Recognize that middleware execution perfectly matches the **Chain of Responsibility** (or Interceptor) pattern.
*   **Action**: Define a `Filter` interface (or abstract class) with a signature like `doFilter(HttpContext ctx, FilterChain chain)`.
*   **Action**: Create the `FilterChain` interface/class to manage the sequence and iterator state.
*   **Why**: This is the core architectural decision. It decouples the gateway engine from the specific logic of individual filters (auth, logging, etc.).

### Step 3: Implement Core Middleware
Demonstrate understanding by implementing 2-3 practical filters.
*   **Action**: Implement an `AuthFilter` that demonstrates **short-circuiting** (halting the chain and returning early if authentication fails).
*   **Action**: Implement a `LoggingFilter` that demonstrates **post-processing** (executing logic *after* the `chain.doFilter()` call returns, allowing measurement of response times).
*   **Action**: Implement a `CircuitBreakerFilter` to demonstrate stateful middleware mapping a failure invariant (e.g. failing fast on OPEN state).

### Step 4: Build the Routing Engine
Connect the pipeline to backend targets.
*   **Action**: Define a simple routing table (e.g., a map of string paths to target handlers).
*   **Action**: Create the `ApiGateway` class that takes an incoming request, looks up the route, assembles the `FilterChain`, and executes it.

### Step 5: Address Edge Cases and Constraints
Show senior-level thinking by handling failures gracefully.
*   **Action**: Wrap the `FilterChain` execution in a try-catch block. If a filter or backend handler throws an unexpected exception, the gateway should catch it and return a structured 500 Internal Server Error rather than crashing.
*   **Action**: Discuss thread safety. Since filters might be singletons shared across requests, any state within a filter (like the failure count in a Circuit Breaker) must be thread-safe.

## Typical Interview Flow
1.  **Requirement Gathering (~5 mins)**: Clarify what types of middleware are needed. Ask if dynamic routing is required or if static configuration is acceptable.
2.  **Architecture & Interfaces (~15 mins)**: Sketch out `Filter`, `FilterChain`, and `HttpContext`. Get buy-in on the Chain of Responsibility pattern.
3.  **Implementation (~20 mins)**: Code the core loop of the `FilterChain` and implement 1-2 key filters (especially one that short-circuits).
4.  **Refinement (~5 mins)**: Add error handling and discuss concurrency.