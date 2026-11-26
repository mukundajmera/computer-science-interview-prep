import sys
import os

# Set up paths to import v1-basic modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from tool import ToolDefinition
from schema import ParameterSchema
from router import ToolRegistry

from dag_planner import ToolCallV3
from speculative_executor import SpeculativeExecutor

def add_handler(args):
    return args["a"] + args["b"]

def mul_handler(args):
    return args["a"] * args["b"]

def slow_handler(args):
    import time
    time.sleep(2)
    return args.get("val", 0)

def main():
    registry = ToolRegistry()

    registry.register(ToolDefinition(
        name="add",
        description="Adds two numbers",
        parameter_schema=ParameterSchema({
            "a": {"type": "integer", "required": True},
            "b": {"type": "integer", "required": True}
        }),
        handler=add_handler
    ))

    registry.register(ToolDefinition(
        name="mul",
        description="Multiplies two numbers",
        parameter_schema=ParameterSchema({
            "a": {"type": "integer", "required": True},
            "b": {"type": "integer", "required": True}
        }),
        handler=mul_handler
    ))

    registry.register(ToolDefinition(
        name="slow",
        description="A slow tool",
        parameter_schema=ParameterSchema({
            "val": {"type": "integer", "required": True}
        }),
        handler=slow_handler
    ))

    executor = SpeculativeExecutor(registry=registry)

    # Example 1: DAG Execution
    print("--- Example 1: DAG Execution with interdependent arguments ---")
    calls = [
        ToolCallV3(tool_name="add", arguments={"a": 1, "b": 2}, call_id="add1"),
        ToolCallV3(tool_name="add", arguments={"a": 3, "b": 4}, call_id="add2"),
        # Depends on add1 and add2
        ToolCallV3(tool_name="mul", arguments={"a": "$add1", "b": "$add2"}, dependencies=["add1", "add2"], call_id="mul1")
    ]

    results = executor.execute_plan(calls)
    for res in results:
        print(f"Tool: {res.tool_name}, Success: {res.success}, Result: {res.result}, Error: {res.error}, Duration: {res.duration_ms:.2f}ms")

    # Example 2: Timeout
    print("\n--- Example 2: Timeout Enforcement ---")
    calls = [
        ToolCallV3(tool_name="slow", arguments={"val": 10}, call_id="slow1")
    ]
    results = executor.execute_plan(calls, timeout_per_call=1.0)
    for res in results:
        print(f"Tool: {res.tool_name}, Success: {res.success}, Error: {res.error}")

if __name__ == "__main__":
    main()
