# Low-Level Design: API Gateway & Middleware Pipeline

## Problem Statement

Design a simple, extensible API Gateway module focusing on its middleware pipeline (Filter Chain) processing capabilities. 
The system should intercept incoming HTTP requests, process them sequentially through a series of configurable middleware filters, and route the request to a backend handler, returning the response back through the same filters.

The design must map the Filter Chain model and support common gateway functionality such as rate limiting, authentication, payload transformation, and circuit breaking. It should elegantly manage request/response mutation and short-circuiting logic.

## Key Requirements

1. **Middleware Pipeline Execution**: Implement a filter chain (Chain of Responsibility) that can sequentially execute logic before (pre-processing) and after (post-processing) a target handler.
2. **Short-Circuiting**: Middleware must be able to stop the execution chain early (e.g., return a 401 Unauthorized or 429 Too Many Requests) without invoking the downstream backend handler.
3. **Request/Response Objects**: A standardized context/object must be passed through the pipeline allowing filters to read and modify headers, body, or status codes.
4. **Target Routing**: The gateway should route the request to a simulated backend endpoint based on a defined mapping.
5. **Configurability**: Handlers and their associated filters should be dynamic and configurable.

## Constraints & Considerations

* **Architecture Patterns**: Expect to utilize the **Chain of Responsibility**, **Interceptor**, **Proxy**, and **Decorator** design patterns.
* **Extensibility**: It must be easy to add new middleware types (e.g., logging, caching) without altering the core pipeline engine.
* **Exception Handling**: The gateway must catch exceptions thrown in filters or backend handlers and return a structured 500 error rather than crashing.
* **Standard Libraries Only**: The simulation must be implemented purely using built-in standard libraries (Java 11+ / Python 3.8+). Do not use Spring, Flask, Node/Express, etc.
