import pytest
import sys
import os
import time

# Add required paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from tool import ToolDefinition
from schema import ParameterSchema
from router import ToolRegistry

from dag_planner import DAGPlanner, ToolCallV3, CyclicDependencyError, DAGPlannerError
from speculative_executor import SpeculativeExecutor, ExecutorResult

# Helper tools for testing

def add_handler(args):
    return args["a"] + args["b"]

def throw_handler(args):
    raise ValueError("Intentional error")

def slow_handler(args):
    time.sleep(1)
    return True

@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(ToolDefinition(
        name="add",
        description="add",
        parameter_schema=ParameterSchema({
            "a": {"type": "integer"},
            "b": {"type": "integer"}
        }),
        handler=add_handler
    ))
    reg.register(ToolDefinition(
        name="throw",
        description="throws",
        parameter_schema=ParameterSchema({}),
        handler=throw_handler
    ))
    reg.register(ToolDefinition(
        name="slow",
        description="sleeps",
        parameter_schema=ParameterSchema({}),
        handler=slow_handler
    ))
    return reg

def test_dag_planner_valid_stages():
    planner = DAGPlanner()
    calls = [
        ToolCallV3(tool_name="add", call_id="a1"),
        ToolCallV3(tool_name="add", call_id="a2"),
        ToolCallV3(tool_name="add", dependencies=["a1", "a2"], call_id="a3"),
        ToolCallV3(tool_name="add", dependencies=["a3"], call_id="a4"),
    ]

    stages = planner.plan_stages(calls)
    assert len(stages) == 3
    assert {c.call_id for c in stages[0]} == {"a1", "a2"}
    assert {c.call_id for c in stages[1]} == {"a3"}
    assert {c.call_id for c in stages[2]} == {"a4"}

def test_dag_planner_cyclic_dependency():
    planner = DAGPlanner()
    calls = [
        ToolCallV3(tool_name="add", dependencies=["c2"], call_id="c1"),
        ToolCallV3(tool_name="add", dependencies=["c1"], call_id="c2"),
    ]
    with pytest.raises(CyclicDependencyError):
        planner.plan_stages(calls)

def test_dag_planner_missing_dependency():
    planner = DAGPlanner()
    calls = [
        ToolCallV3(tool_name="add", dependencies=["missing"], call_id="c1"),
    ]
    with pytest.raises(DAGPlannerError):
        planner.plan_stages(calls)

def test_dag_planner_resolve_arguments():
    planner = DAGPlanner()
    call = ToolCallV3(tool_name="add", arguments={"a": "$c1", "b": "$c2.val"})
    prev_results = {
        "c1": 10,
        "c2": {"val": 20}
    }
    resolved = planner.resolve_arguments(call, prev_results)
    assert resolved == {"a": 10, "b": 20}

def test_executor_basic_dag(registry):
    executor = SpeculativeExecutor(registry)
    calls = [
        ToolCallV3(tool_name="add", arguments={"a": 1, "b": 2}, call_id="c1"),
        ToolCallV3(tool_name="add", arguments={"a": "$c1", "b": 3}, dependencies=["c1"], call_id="c2"),
    ]
    results = executor.execute_plan(calls)
    assert len(results) == 2
    assert results[0].success is True
    assert results[0].result == 3
    assert results[1].success is True
    assert results[1].result == 6

def test_executor_timeout(registry):
    executor = SpeculativeExecutor(registry)
    calls = [
        ToolCallV3(tool_name="slow", call_id="s1")
    ]
    results = executor.execute_plan(calls, timeout_per_call=0.1)
    assert len(results) == 1
    assert results[0].success is False
    assert "timed out" in results[0].error

def test_executor_error_isolation(registry):
    executor = SpeculativeExecutor(registry)
    calls = [
        ToolCallV3(tool_name="throw", call_id="t1"),
        ToolCallV3(tool_name="add", arguments={"a": 1, "b": 2}, call_id="c1"),
        ToolCallV3(tool_name="add", dependencies=["t1"], call_id="dep_t1")
    ]
    results = executor.execute_plan(calls)

    # order corresponds to original list
    t1_res = results[0]
    c1_res = results[1]
    dep_res = results[2]

    assert t1_res.success is False
    assert "Intentional error" in t1_res.error

    assert c1_res.success is True
    assert c1_res.result == 3

    assert dep_res.success is False
    assert "Dependency failed" in dep_res.error

def test_executor_rollback(registry):
    executor = SpeculativeExecutor(registry)

    # We will simulate a rollback handler being called
    rollback_called = []

    def my_rollback(args, result):
        rollback_called.append((args, result))

    tool_def = registry.get("add")
    tool_def.rollback_handler = my_rollback

    calls = [
        ToolCallV3(tool_name="add", arguments={"a": 1, "b": 2}, call_id="a1")
    ]

    # For testing rollback, we just call it directly on the results
    # since execute_plan doesn't automatically trigger rollback in our implementation
    results = executor.execute_plan(calls)
    assert results[0].success is True

    executor.rollback(successful_calls=[calls[0]], results=results)

    assert len(rollback_called) == 1
    assert rollback_called[0][0] == {"a": 1, "b": 2}
    assert rollback_called[0][1] == 3
