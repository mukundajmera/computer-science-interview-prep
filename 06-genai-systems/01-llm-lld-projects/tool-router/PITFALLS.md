# Tool Router - Common Pitfalls

## Common pitfalls

1. **Tight Coupling Between Router and Tools**
   - Directly importing and hardcoding tool implementations within the router class.
   - Using a massive switch/if-else block to route requests instead of a dynamic registry.

2. **Inadequate Error Handling**
   - Letting exceptions from a tool handler crash the entire router or application.
   - Returning raw stack traces to the caller instead of structured, safe error responses.
   - Failing to handle unknown tool names gracefully.

3. **Missing or Weak Schema Validation**
   - Blindly passing the input arguments `dict` to the tool without verifying required fields, types, or constraints.
   - Implementing custom, ad-hoc validation logic inside every single tool handler instead of a centralized schema validation step in the router.

4. **Poor Extensibility for Pre/Post Processing**
   - Hardcoding logging, authentication, or metric-tracking directly into the core routing loop.
   - Not using a middleware or hook pattern, making it difficult to add cross-cutting concerns later without modifying the router code.

5. **Lack of Observability**
   - Failing to track basic execution metrics (e.g., call counts, error rates, duration) per tool.
   - Making it impossible to inspect which tools are registered or what their schemas are at runtime.

## Why these fail interviews

- **Violation of SOLID Principles:** Hardcoding tools violates the Open/Closed Principle (OCP). The router should be open for extension (adding new tools) but closed for modification (no need to change the router's code).
- **Fragility:** If a single poorly written tool can crash the whole system, the design is not robust. In a GenAI context, LLMs can and will hallucinate bad tool inputs.
- **Duplication of Effort:** Forcing every tool author to write their own argument validation leads to boilerplate, bugs, and inconsistent error messages.
- **Inflexibility:** An inability to cleanly inject middleware shows a lack of foresight into production requirements like logging, tracing, and access control.

## Mitigations

1. **Use a Registry Pattern:** Implement a `ToolRegistry` to decouple the router from the tools. Tools should be registered dynamically (e.g., at startup).
2. **Implement the Command/Strategy Pattern:** Treat each tool as an independent handler that implements a common interface or signature, and look them up dynamically.
3. **Centralize Validation:** Build a robust `ParameterSchema` class and perform validation in the router *before* dispatching the call to the handler.
4. **Wrap Executions Safely:** Use `try-catch` (or `try-except`) blocks around the handler execution. Catch broad exceptions and wrap them into a standardized `ToolResult` object with `success=False`.
5. **Apply the Middleware/Chain of Responsibility Pattern:** Allow registering an array of `ToolMiddleware` objects that can intercept calls before they reach the tool and after the tool returns.

## Cross-links

- [Problem Statement](./PROBLEM.md)
- [System Design Approach](./APPROACH.md)
- [Detailed Design](./DESIGN.md)
