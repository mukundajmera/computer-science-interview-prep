# Tool Router

## Problem Statement

Design a tool router that manages a registry of callable tools and routes incoming tool-call requests to the appropriate handler functions. The router should validate tool arguments against a declared parameter schema before dispatching, handle errors gracefully (unknown tool, validation failure, handler exception), support tool discovery, track per-tool execution metrics, and allow middleware hooks for pre/post processing. The system should be extensible enough that new tools and middleware can be added without modifying existing code.

---

## Functional Requirements

1. **Tool Registration**: Register tools with a name, description, parameter schema, and handler function
2. **Tool Routing**: Route an incoming tool-call request (tool name + arguments) to the matching handler
3. **Schema Validation**: Validate tool arguments against the declared parameter schema before dispatching
4. **Error Handling**: Return structured errors for unknown tools, validation failures, and handler exceptions
5. **Tool Discovery**: List all available tools and retrieve the schema for a specific tool
6. **Execution Metrics**: Track per-tool call counts, error counts, and total execution time
7. **Middleware / Hooks**: Support before-call and after-call middleware for logging, auth, or transformation

---

## Non-Functional Requirements

1. **Extensibility**: Adding a new tool or middleware must not require changes to existing classes (Open/Closed Principle)
2. **Testability**: Every component must be independently unit-testable with deterministic stub handlers
3. **Safety**: A failing handler must never crash the router; errors are always captured in the result
4. **Standard Library Only**: No external dependencies — use Python's built-in modules exclusively
5. **Determinism**: Schema validation and routing logic must produce consistent, repeatable outcomes

---

## Constraints & Assumptions

- Handlers are synchronous callables (`Callable[[Dict], Any]`)
- Tool names are unique strings within a registry
- Parameter schemas support types: `"string"`, `"integer"`, `"float"`, `"boolean"`, `"array"`
- Schema validation checks required parameters, type correctness, and enum membership
- Execution duration is measured with `time.time()` for simplicity
- Middleware is executed in registration order (before) and reverse order (after)
- All operations are single-threaded in v1

---

## Sample Interactions

```
1. Define a ParameterSchema with required and optional parameters
2. Create ToolDefinition(name="calculator", description="...", schema=schema, handler=calc_fn)
3. Register the tool in a ToolRegistry
4. Create a ToolRouter(registry=registry, middleware=[LoggingMiddleware()])
5. call = ToolCall(tool_name="calculator", arguments={"operation": "add", "a": 1, "b": 2})
6. result = router.route(call)  → ToolResult(success=True, result=3, ...)
7. call2 = ToolCall(tool_name="unknown_tool", arguments={})
8. result2 = router.route(call2) → ToolResult(success=False, error="Unknown tool: unknown_tool", ...)
9. router.get_stats() → {"calculator": {"calls": 1, "errors": 0, "total_ms": 0.12}}
```

---

## Clarifying Questions to Ask

1. "Should tools be registered at startup only, or can tools be added/removed at runtime?"
2. "Do we need to support async handlers, or are synchronous handlers sufficient?"
3. "Should middleware be able to short-circuit execution (e.g., reject a call before dispatching)?"
4. "What is the expected number of registered tools — tens, hundreds, or thousands?"
5. "Should schema validation support nested object types, or are flat parameter maps sufficient?"
6. "Do we need tool versioning, or is one handler per tool name enough?"
7. "Should execution metrics persist across restarts, or is in-memory sufficient?"
8. "How should timeout/long-running handlers be handled?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| ParameterSchema | Defines expected parameters with types, required flags, defaults, and enum constraints |
| ToolDefinition | Bundles a tool's name, description, parameter schema, and handler function |
| ToolCall | Input data carrier: tool name, arguments dict, and unique call ID |
| ToolResult | Output data carrier: success/failure, result or error, duration, call metadata |
| ToolRegistry | Stores and retrieves registered tool definitions by name |
| ToolMiddleware | Abstract hook for pre/post processing of tool calls and results |
| LoggingMiddleware | Concrete middleware that logs call dispatch and results |
| ToolRouter | Orchestrator: validates, runs middleware, dispatches, captures errors and metrics |

---

## Cross-References

- [Prompting, Tools & Agents concept](../../00-concepts/prompting-tools-agents/) — how LLMs invoke tools
- [Model Routing & Orchestration concept](../../00-concepts/model-routing-orchestration/) — routing strategies
- [Agentic Workflow Orchestrator (HLD)](../../02-llm-hld-projects/agentic-workflow-orchestrator/) — system design that uses tool routing
- [API Gateway (classical HLD concept)](../../../03-hld-concepts/api-gateway/) — classical request routing and middleware

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Tool registry, schema validation (types, required, enum), routing with error capture, middleware (before/after hooks, logging), per-tool metrics, tool discovery |
| v2-extended | Async handler support, tool versioning, middleware short-circuiting, retry policies, JSON Schema compatibility, tool groups/namespaces |
| v3-optimized | Concurrent dispatch, handler timeout enforcement, schema caching, plugin-based tool loading, distributed metrics, rate limiting per tool |
