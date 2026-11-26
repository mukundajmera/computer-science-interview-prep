# Design Approach for Tool Router

A step-by-step thought process for designing the tool router.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Tool | ❌ No | Abstract concept — represented by ToolDefinition |
| Tool name | ❌ No | Primitive string attribute of ToolDefinition |
| Description | ❌ No | Primitive string attribute of ToolDefinition |
| Parameter schema | ✅ Yes | Encapsulates validation rules for tool arguments |
| Handler | ❌ No | A callable — stored as an attribute of ToolDefinition |
| Tool definition | ✅ Yes | Bundles name, description, schema, and handler |
| Tool call | ✅ Yes | Input data carrier with tool name, arguments, and call ID |
| Tool result | ✅ Yes | Output data carrier with success/failure, result, error, duration |
| Registry | ✅ Yes | Stores and retrieves tool definitions |
| Router | ✅ Yes | Orchestrator that validates, dispatches, and captures errors |
| Middleware | ✅ Yes | Abstract hook for pre/post processing |
| Metrics | ❌ No | Derived from router state — not a standalone entity |

**Final Entities (v1)**: ParameterSchema, ToolDefinition, ToolCall, ToolResult, ToolRegistry, ToolRouter, ToolMiddleware, LoggingMiddleware

---

## Step 2: Define Relationships

```
ToolDefinition (1) ──has──> (1) ParameterSchema
ToolRegistry (1) ──stores──> (n) ToolDefinition
ToolRouter (1) ──uses──> (1) ToolRegistry
ToolRouter (1) ──uses──> (n) ToolMiddleware
ToolRouter (1) ──accepts──> (n) ToolCall
ToolRouter (1) ──produces──> (n) ToolResult
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| ToolDefinition → ParameterSchema | Composition | Schema belongs to the tool definition |
| ToolRouter → ToolRegistry | Composition | Registry injected at construction |
| ToolRouter → ToolMiddleware | Association | Optional middleware chain injected at construction |
| ToolRouter → ToolCall | Derivation | Calls are consumed as input |
| ToolRouter → ToolResult | Derivation | Results are produced as output |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Registry** | ✅ Yes | Store and retrieve tools by name with O(1) lookup |
| **Command** | ✅ Yes | Encapsulate tool-call requests as objects for routing and logging |
| **Chain of Responsibility** | ✅ Yes | Compose middleware hooks for pre/post processing |
| **Strategy** | ✅ Yes | Each tool handler is a swappable strategy behind a uniform interface |
| **Factory** | 🔄 v2 | Create tools from configuration or plugin definitions |
| **Observer** | 🔄 v2 | Notify listeners on tool registration or execution events |
| **Singleton** | ❌ No | No global state — prefer dependency injection |
| **Decorator** | 🔄 v3 | Wrap handlers with retry, timeout, or caching decorators |

### Pattern Application:

1. **Registry Pattern** — ToolRegistry
   - Tools are registered by name and retrieved in O(1) via a dict
   - Duplicate registration is rejected to prevent silent overwrites
   - Decouples tool definition from routing logic

2. **Command Pattern** — ToolCall
   - Each request is an immutable object with tool name, arguments, and a unique ID
   - Enables logging, middleware transformation, and potential replay
   - Clean separation between request construction and dispatch

3. **Chain of Responsibility** — ToolMiddleware
   - Before-call hooks run in registration order; after-call hooks run in reverse
   - Each middleware can transform the call or result without knowing about others
   - Easy to add logging, auth, rate-limiting independently

---

## Step 4: Design Classes

### Core Classes:

#### ParameterSchema
- **Attributes**:
  - `parameters: Dict[str, dict]` — name → `{type, required, description, default, enum}`
- **Methods**:
  - `validate(args)` — check required params, type correctness, enum membership
  - `get_parameter_names()` — all parameter names
  - `get_required_parameters()` — names where required is True
- **Supported Types**: `"string"`, `"integer"`, `"float"`, `"boolean"`, `"array"`

#### ToolDefinition (dataclass)
- **Attributes**: name, description, parameter_schema, handler
- **Methods**: None (pure data carrier)

#### ToolCall (dataclass)
- **Attributes**: tool_name, arguments, call_id (UUID auto-generated)
- **Methods**: None (pure data carrier)

#### ToolResult (dataclass)
- **Attributes**: call_id, tool_name, success, result, error, duration_ms
- **Methods**: None (pure data carrier)

#### ToolMiddleware (ABC)
- **Methods**:
  - `before_call(call) → ToolCall` — transform or inspect the call
  - `after_call(call, result) → ToolResult` — transform or inspect the result

#### LoggingMiddleware
- **Attributes**: `_log: List[str]` — recorded messages
- **Methods**:
  - `before_call(call)` — log dispatch intent, return call unchanged
  - `after_call(call, result)` — log outcome, return result unchanged
  - `get_log()` — return recorded messages

#### ToolRegistry
- **Attributes**: `_tools: Dict[str, ToolDefinition]`
- **Methods**:
  - `register(tool)` — add tool, raise ValueError on duplicate
  - `get(name)` — return ToolDefinition or None
  - `list_tools()` — return all registered definitions
  - `has(name)` — check existence

#### ToolRouter
- **Attributes**:
  - `_registry: ToolRegistry`
  - `_middleware: List[ToolMiddleware]`
  - `_stats: Dict[str, dict]`
- **Methods**:
  - `route(call)` — middleware → validate → dispatch → capture errors → track metrics → middleware → return
  - `get_stats()` — return per-tool metrics

---

## Step 5: Handle Edge Cases

### Input Validation:
- Unknown tool name → structured error result
- Missing required arguments → list of validation errors
- Wrong argument type (e.g., string where integer expected) → type error message
- Invalid enum value → enum membership error
- None as arguments dict → treat as empty dict
- Empty tool name → error result

### Business Logic:
- Handler raises an exception → caught, wrapped in error result
- Handler returns None → success with None result
- Middleware transforms call arguments → downstream sees modified call
- Multiple middleware → chained in order (before) / reverse (after)
- Tool registered twice → ValueError on second registration

### Boundary Conditions:
- Zero middleware (router works without any)
- Tool with no parameters (empty schema, any arguments ignored)
- Tool with all optional parameters (empty arguments valid)
- Very long argument values (accepted but may be slow)
- Special characters in tool names (accepted as-is)

---

## Step 6: Optimization Opportunities

### Data Structures:

| Operation | v1 Basic | v3 Optimized |
|-----------|----------|--------------|
| Tool lookup | O(1) dict | O(1) dict |
| Schema validation | O(p) linear | O(p) compiled validators |
| Middleware chain | O(m) iteration | O(m) iteration |
| Metrics update | O(1) | O(1) atomic counters |

*p = number of parameters, m = number of middleware*

### Caching:
- Compiled type-check functions per schema (avoid repeated dispatch)
- Pre-validate common argument patterns

### Concurrency:
- v1: Single-threaded, synchronous handlers
- v3: Thread pool for concurrent dispatch, async handler support

---

## Step 7: Version Progression

### v1-basic
- ParameterSchema with type, required, default, and enum validation
- ToolDefinition, ToolCall, ToolResult dataclasses
- ToolRegistry with register, get, list, has
- ToolRouter with middleware chain, error capture, and per-tool metrics
- LoggingMiddleware for debugging

### v2-extended
- Async handler support (`route_async`)
- Tool versioning and version-based routing
- Middleware short-circuiting (reject calls before dispatch)
- Retry policies as middleware
- JSON Schema compatibility layer

### v3-optimized
- Concurrent dispatch with thread pool
- Handler timeout enforcement
- Schema compilation and caching
- Plugin-based tool loading from config
- Distributed metrics collection
- Per-tool rate limiting

---

## Code Organization

```
tool-router/
├── PROBLEM.md                  # Requirements and constraints
├── APPROACH.md                 # This design walkthrough
├── DESIGN.md                   # Class diagrams and decisions
├── python/
│   ├── v1-basic/
│   │   ├── __init__.py         # Package marker
│   │   ├── schema.py           # ParameterSchema validation
│   │   ├── tool.py             # ToolDefinition, ToolCall, ToolResult dataclasses
│   │   ├── router.py           # ToolMiddleware, LoggingMiddleware, ToolRegistry, ToolRouter
│   │   └── demo.py             # Runnable end-to-end example
│   └── tests/
│       ├── __init__.py         # Package marker
│       └── test_tool_router.py # Unit tests for all components
```

---

## Interview Discussion Points

1. **Why Registry instead of a simple dict?**
   - Encapsulates validation (duplicate check, name constraints)
   - Provides a discoverable API (list_tools, has)
   - Easy to extend with namespaces or versioning

2. **Why Command pattern for ToolCall?**
   - Middleware needs to inspect and transform requests as objects
   - Call IDs enable correlation with results for logging and tracing
   - Supports potential replay and audit trails

3. **Why structured ToolResult instead of raising exceptions?**
   - LLM consumers expect a uniform response format
   - The router must never crash — every call produces a result
   - Consistent interface simplifies agent loops

4. **How would you add authentication?**
   - Implement an `AuthMiddleware` that checks credentials in `before_call`
   - No changes to ToolRouter or ToolRegistry
   - Chain it before LoggingMiddleware so rejected calls are not logged as dispatched

5. **How would you scale this for production?**
   - Replace in-memory registry with a service discovery backend
   - Add async handler support for I/O-bound tools
   - Use distributed metrics (Prometheus, StatsD) instead of in-memory counters
   - Add circuit breakers and timeouts per tool
