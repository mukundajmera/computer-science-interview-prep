"""
Tool Router demo — v1 basic.

Walks through the full tool-routing pipeline:
    1. Define tools with schemas and handlers
    2. Register tools in a registry
    3. Route valid and invalid calls
    4. Observe middleware logging
    5. Display per-tool metrics

Run:
    python demo.py
"""

from schema import ParameterSchema
from tool import ToolCall, ToolDefinition
from router import LoggingMiddleware, ToolRegistry, ToolRouter


# ---------------------------------------------------------------------------
# Example handlers
# ---------------------------------------------------------------------------

def calculator_handler(args: dict) -> float:
    """Simple arithmetic calculator."""
    op = args["operation"]
    a = args["a"]
    b = args["b"]
    if op == "add":
        return a + b
    elif op == "subtract":
        return a - b
    elif op == "multiply":
        return a * b
    elif op == "divide":
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    raise ValueError(f"Unknown operation: {op}")


def string_utils_handler(args: dict) -> str:
    """String manipulation utilities."""
    action = args["action"]
    text = args["text"]
    if action == "upper":
        return text.upper()
    elif action == "lower":
        return text.lower()
    elif action == "reverse":
        return text[::-1]
    raise ValueError(f"Unknown action: {action}")


def weather_lookup_handler(args: dict) -> dict:
    """Stub weather lookup — returns fake data."""
    city = args["city"]
    return {
        "city": city,
        "temperature_c": 22,
        "condition": "Partly cloudy",
        "humidity_pct": 65,
    }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("TOOL ROUTER DEMO (v1-basic)")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Define tools
    # ------------------------------------------------------------------
    calc_schema = ParameterSchema({
        "operation": {
            "type": "string",
            "required": True,
            "description": "Arithmetic operation",
            "enum": ["add", "subtract", "multiply", "divide"],
        },
        "a": {"type": "float", "required": True, "description": "First operand"},
        "b": {"type": "float", "required": True, "description": "Second operand"},
    })
    calc_tool = ToolDefinition(
        name="calculator",
        description="Performs basic arithmetic operations",
        parameter_schema=calc_schema,
        handler=calculator_handler,
    )

    string_schema = ParameterSchema({
        "action": {
            "type": "string",
            "required": True,
            "enum": ["upper", "lower", "reverse"],
        },
        "text": {"type": "string", "required": True},
    })
    string_tool = ToolDefinition(
        name="string_utils",
        description="String manipulation utilities",
        parameter_schema=string_schema,
        handler=string_utils_handler,
    )

    weather_schema = ParameterSchema({
        "city": {"type": "string", "required": True, "description": "City name"},
    })
    weather_tool = ToolDefinition(
        name="weather_lookup",
        description="Look up current weather for a city (stub)",
        parameter_schema=weather_schema,
        handler=weather_lookup_handler,
    )

    # ------------------------------------------------------------------
    # 2. Register tools
    # ------------------------------------------------------------------
    registry = ToolRegistry()
    registry.register(calc_tool)
    registry.register(string_tool)
    registry.register(weather_tool)

    print(f"\nRegistered tools: {[t.name for t in registry.list_tools()]}")

    # ------------------------------------------------------------------
    # 3. Create router with logging middleware
    # ------------------------------------------------------------------
    logger = LoggingMiddleware()
    router = ToolRouter(registry=registry, middleware=[logger])

    # ------------------------------------------------------------------
    # 4. Successful call
    # ------------------------------------------------------------------
    print("\n--- Successful Calculator Call ---")
    call = ToolCall(tool_name="calculator", arguments={
        "operation": "add", "a": 10, "b": 5,
    })
    result = router.route(call)
    print(f"  Success: {result.success}")
    print(f"  Result:  {result.result}")
    print(f"  Duration: {result.duration_ms:.2f} ms")

    # ------------------------------------------------------------------
    # 5. Unknown tool
    # ------------------------------------------------------------------
    print("\n--- Unknown Tool ---")
    call = ToolCall(tool_name="nonexistent", arguments={})
    result = router.route(call)
    print(f"  Success: {result.success}")
    print(f"  Error:   {result.error}")

    # ------------------------------------------------------------------
    # 6. Validation failure
    # ------------------------------------------------------------------
    print("\n--- Validation Failure (missing required param) ---")
    call = ToolCall(tool_name="calculator", arguments={"operation": "add", "a": 1})
    result = router.route(call)
    print(f"  Success: {result.success}")
    print(f"  Error:   {result.error}")

    # ------------------------------------------------------------------
    # 7. Handler exception
    # ------------------------------------------------------------------
    print("\n--- Handler Exception (division by zero) ---")
    call = ToolCall(tool_name="calculator", arguments={
        "operation": "divide", "a": 10, "b": 0,
    })
    result = router.route(call)
    print(f"  Success: {result.success}")
    print(f"  Error:   {result.error}")

    # ------------------------------------------------------------------
    # 8. String utils
    # ------------------------------------------------------------------
    print("\n--- String Utils ---")
    call = ToolCall(tool_name="string_utils", arguments={
        "action": "reverse", "text": "Hello, World!",
    })
    result = router.route(call)
    print(f"  Result: {result.result}")

    # ------------------------------------------------------------------
    # 9. Weather lookup
    # ------------------------------------------------------------------
    print("\n--- Weather Lookup (stub) ---")
    call = ToolCall(tool_name="weather_lookup", arguments={"city": "Tokyo"})
    result = router.route(call)
    print(f"  Result: {result.result}")

    # ------------------------------------------------------------------
    # 10. Metrics
    # ------------------------------------------------------------------
    print("\n--- Per-Tool Metrics ---")
    stats = router.get_stats()
    for tool_name, data in stats.items():
        print(f"  {tool_name}: calls={data['calls']}  "
              f"errors={data['errors']}  total_ms={data['total_ms']:.2f}")

    # ------------------------------------------------------------------
    # 11. Middleware log
    # ------------------------------------------------------------------
    print("\n--- Middleware Log ---")
    for entry in logger.get_log():
        print(f"  {entry}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
