# Tool Router - Follow-Up Questions

## Follow-up questions

1. **How would you handle long-running or hanging tools?**
   - *Expected answer*: Introduce timeouts at the dispatcher layer. If a tool exceeds the allowed duration, cancel the execution and return a timeout error `ToolResult`. We could implement this via threading/multiprocessing timeouts, or if using async, `asyncio.wait_for`.

2. **How do you prevent a malicious or poorly written tool from crashing the router?**
   - *Expected answer*: Isolate tool execution. Currently, `ToolRouter` wraps execution in a broad `try/except Exception` block, but tools can still block the event loop or crash the process (e.g., memory exhaustion, native segfaults). True isolation would require executing tools in separate processes or sandboxes (e.g., containers, WebAssembly).

3. **How would you support rate-limiting or quotas per tool?**
   - *Expected answer*: This can be implemented as a `RateLimitMiddleware`. The middleware would check a token bucket or distributed counter (like Redis) based on `call.tool_name` or a client identifier. If the limit is exceeded, it can short-circuit the execution and return a failure `ToolResult` without dispatching the handler.

4. **How do you securely handle authentication/authorization for specific tools?**
   - *Expected answer*: Add an `AuthMiddleware` that extracts credentials from the call context or arguments and validates them. The `ToolDefinition` could include an `allowed_roles` attribute that the middleware checks against the caller's role.

5. **LLMs often provide arguments as unstructured text or malformed JSON. How does the router handle this?**
   - *Expected answer*: The current `ParameterSchema` validation checks for type correctness and missing required fields. We could add a "Correction/Coercion" middleware that attempts to parse JSON strings into dicts, or coercing strings to numbers if the schema expects it, before hitting the strict validation layer.

## Variants and extensions

- **Async Support**: Extending the design to support `async def` handlers. This would require an `AsyncToolRouter` or `route_async` method that `await`s the handler and async middleware hooks.
- **Dynamic Tool Discovery**: Loading tools dynamically at runtime from plugins, REST APIs, or scanning a directory of scripts, rather than registering them all at startup.
- **OpenAPI / JSON Schema Integration**: Generating a standard JSON Schema from `ParameterSchema` to directly feed into an LLM's function-calling API (like OpenAI's `tools` parameter).

## Interviewer probes to prepare

- *Probe*: "What happens if a tool expects a float, but the user provides an integer?"
  - *Response*: The `ParameterSchema` `_check_type` logic is designed to accept `int` when `float` is expected, handling this auto-promotion gracefully.
- *Probe*: "If you have 1,000 tools, how does the router perform?"
  - *Response*: Tool lookup is O(1) via the `ToolRegistry` dictionary. However, sending 1,000 tool schemas to an LLM context is infeasible. We'd need an upstream semantic search/retriever layer to select the top-K relevant tools before presenting them to the LLM.
- *Probe*: "How do you ensure middleware doesn't break the system?"
  - *Response*: Middleware are executed in a deterministic chain. We must ensure middleware contracts are respected (e.g., `before_call` must return a `ToolCall`, `after_call` must return a `ToolResult`).

## Cross-links

- [Problem Statement](PROBLEM.md)
- [Architecture & Approach](APPROACH.md)
- [Design Details](DESIGN.md)
