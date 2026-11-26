import pytest
import sys
import os
import time

# Add v1-basic and v2-extended to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from tool import ToolDefinition
from schema import ParameterSchema
from router import ToolRegistry

from parallel_router import ParallelRouter, ToolCallV2
from schema_validator import SchemaValidator
from rate_limited_executor import RateLimitedExecutor

@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(ToolDefinition(
        name="echo",
        description="Echoes input",
        parameter_schema=ParameterSchema({"msg": {"type": "string", "required": True}}),
        handler=lambda args: args["msg"]
    ))
    reg.register(ToolDefinition(
        name="slow_echo",
        description="Echoes input slowly",
        parameter_schema=ParameterSchema({"msg": {"type": "string", "required": True}}),
        handler=lambda args: _sleep_and_return(0.1, args["msg"])
    ))
    reg.register(ToolDefinition(
        name="fail_tool",
        description="Always fails",
        parameter_schema=ParameterSchema({}),
        handler=lambda args: _raise_exception()
    ))
    return reg

def _sleep_and_return(duration, val):
    time.sleep(duration)
    return val

def _raise_exception():
    raise Exception("Intentional failure")

def test_schema_repair_integer():
    validator = SchemaValidator({
        "count": {"type": "integer", "required": True}
    })

    # Valid
    success, repaired, errors = validator.validate_and_repair({"count": 5})
    assert success
    assert repaired["count"] == 5

    # Coerce from string
    success, repaired, errors = validator.validate_and_repair({"count": "10"})
    assert success
    assert repaired["count"] == 10

    # Fail invalid string
    success, repaired, errors = validator.validate_and_repair({"count": "abc"})
    assert not success
    assert "Cannot coerce string" in errors[0]

def test_schema_repair_boolean():
    validator = SchemaValidator({
        "flag": {"type": "boolean", "required": True}
    })

    # Coerce from string
    success, repaired, errors = validator.validate_and_repair({"flag": "true"})
    assert success
    assert repaired["flag"] is True

    success, repaired, errors = validator.validate_and_repair({"flag": "0"})
    assert success
    assert repaired["flag"] is False

def test_rate_limiter_exceed():
    # 2 tokens capacity, refills very slowly
    limiter = RateLimitedExecutor(capacity=2, fill_rate=0.01)

    # Consume 2 tokens
    assert limiter._consume_tokens(1) is True
    assert limiter._consume_tokens(1) is True

    # 3rd should fail immediately
    assert limiter._consume_tokens(1) is False

def test_parallel_router_dag_resolution(registry):
    router = ParallelRouter(registry=registry, max_workers=2)

    # c2 depends on c1
    c1 = ToolCallV2("slow_echo", {"msg": "first"}, call_id="c1")
    c2 = ToolCallV2("echo", {"msg": "second"}, dependencies=["c1"], call_id="c2")

    start = time.time()
    results = router.route_parallel([c1, c2])
    duration = time.time() - start

    assert len(results) == 2
    assert results[0].call_id == "c1"
    assert results[1].call_id == "c2"
    assert results[0].success
    assert results[1].success
    assert results[0].result == "first"
    assert results[1].result == "second"

    # Should take at least 0.1s due to slow_echo
    assert duration >= 0.1

def test_parallel_router_dag_failure_propagation(registry):
    router = ParallelRouter(registry=registry, max_workers=2)

    # c1 fails, c2 depends on c1, c2 should also fail
    c1 = ToolCallV2("fail_tool", {}, call_id="c1")
    c2 = ToolCallV2("echo", {"msg": "second"}, dependencies=["c1"], call_id="c2")

    results = router.route_parallel([c1, c2])

    assert len(results) == 2
    assert not results[0].success
    assert "Handler error" in results[0].error

    assert not results[1].success
    assert "Dependency failed: c1" in results[1].error

def test_parallel_router_cyclic_dependency(registry):
    router = ParallelRouter(registry=registry, max_workers=2)

    c1 = ToolCallV2("echo", {"msg": "1"}, dependencies=["c2"], call_id="c1")
    c2 = ToolCallV2("echo", {"msg": "2"}, dependencies=["c1"], call_id="c2")

    results = router.route_parallel([c1, c2])

    assert len(results) == 2
    assert not results[0].success
    assert not results[1].success
    assert "cyclic dependency" in results[0].error or "cyclic dependency" in results[1].error

def test_parallel_router_rate_limit(registry):
    limiter = RateLimitedExecutor(capacity=1, fill_rate=0.01)
    router = ParallelRouter(registry=registry, max_workers=2, rate_limiter=limiter)

    # Run two fast calls concurrently. First one gets token, second fails.
    c1 = ToolCallV2("echo", {"msg": "1"}, call_id="c1")
    c2 = ToolCallV2("echo", {"msg": "2"}, call_id="c2")

    results = router.route_parallel([c1, c2])

    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]

    assert len(successes) == 1
    assert len(failures) == 1
    assert "Rate limit error" in failures[0].error
