# Design Document: API Gateway & Middleware Pipeline

## Core Architecture

The system utilizes the **Chain of Responsibility** (or **Interceptor**) pattern heavily to create a modular, sequential processing pipeline. The design separates the core pipeline engine from the specific business logic residing in each middleware component.

### Components and Class Structure

#### 1. Context Models
*   `RequestContext`: Encapsulates an HTTP request's details (method, path, headers, query parameters, body).
*   `ResponseContext`: Encapsulates the HTTP response details (status code, headers, body).
*   `HttpContext`: A wrapper containing both the `RequestContext` and `ResponseContext`. This context object is passed along the chain, allowing middleware to inspect the request and mutate the response.

#### 2. The Filter Chain (Chain of Responsibility)
*   `Filter` (Interface): Declares a `doFilter(HttpContext context, FilterChain chain)` method.
*   `FilterChain`: Manages the ordered list of `Filter` implementations. It tracks the current index of execution and exposes a `doFilter(HttpContext context)` method. When called, it invokes the next filter in the sequence, or, if at the end of the chain, executes the target handler.

#### 3. Specific Filters (Concrete Implementations)
*   `AuthenticationFilter`: Validates tokens (e.g., checks for an "Authorization" header). If invalid, sets a 401 response and halts the chain.
*   `RateLimitingFilter`: Checks request frequency against a limit. If exceeded, sets a 429 response and halts the chain.
*   `LoggingFilter`: Logs the incoming request details, calls `chain.doFilter()`, and upon return, logs the outgoing response details and latency.
*   `CircuitBreakerFilter`: Monitors target failures. If failures cross a threshold, transitions to an OPEN state, failing fast with a 503 response. It maps a named failure invariant (Circuit Breaker OPEN state) to both a Java and Python bounded simulator.

#### 4. The Dispatcher / Gateway Engine
*   `BackendHandler` (Interface): Represents a target endpoint containing business logic (e.g., `execute(HttpContext context)`).
*   `Route`: Associates a specific path pattern with a `FilterChain` and a target `BackendHandler`.
*   `ApiGateway`: The main entry point. It receives a raw request, maps it to a `Route`, constructs the initial `HttpContext`, and kicks off the `FilterChain`.

## Data Flow (Request / Response Lifecycle)

1.  **Ingestion**: `ApiGateway` receives an incoming request.
2.  **Routing**: The Gateway identifies the correct `Route` and associated `BackendHandler`.
3.  **Filter Chain Initialization**: A `FilterChain` is assembled for this specific route.
4.  **Pre-Processing**: The chain starts. Each `Filter` executes its pre-processing logic.
    *   *Short-Circuit*: If a filter (e.g., Auth) fails, it modifies the response and returns immediately, bypassing the rest of the chain and the handler.
5.  **Execution**: If all filters pass, the `FilterChain` invokes the `BackendHandler`.
6.  **Post-Processing**: As the call stack unwinds, each `Filter` can execute post-processing logic (e.g., adding headers, logging response time).
7.  **Egress**: The Gateway extracts the final `ResponseContext` and returns it to the client.

## Design Patterns utilized

1.  **Chain of Responsibility / Interceptor**: Core to the `FilterChain` and `Filter` execution model. Each filter decides whether to process the request, pass it along, or short-circuit.
2.  **Proxy / Decorator**: The gateway acts as a proxy for backend services. Filters decorate the core request/response handling with additional behaviors (logging, auth).
3.  **Command (loose variant)**: The `BackendHandler` encapsulates the executable action for a specific route.