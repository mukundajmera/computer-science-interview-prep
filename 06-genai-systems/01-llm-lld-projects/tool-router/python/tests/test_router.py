import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from models import ParameterSchema, ToolDefinition, ToolCall, LoggingMiddleware, ToolResult
from registry import ToolRegistry
from router import ToolRouter

def test_tool_registration():
    schema = ParameterSchema({"arg1": {"type": "string"}})
    def dummy_handler(args): return "dummy"
    tool = ToolDefinition("dummy_tool", "A dummy tool", schema, dummy_handler)
    
    registry = ToolRegistry()
    registry.register(tool)
    
    assert registry.has("dummy_tool")
    assert registry.get("dummy_tool") == tool
    assert len(registry.list_tools()) == 1

    with pytest.raises(ValueError, match="already registered"):
        registry.register(tool)

def test_parameter_schema_validation():
    schema = ParameterSchema({
        "req_str": {"type": "string", "required": True},
        "opt_int": {"type": "integer"},
        "opt_enum": {"type": "string", "enum": ["A", "B"]}
    })
    
    # Valid
    errors = schema.validate({"req_str": "hello", "opt_int": 42, "opt_enum": "A"})
    assert len(errors) == 0
    
    # Missing required
    errors = schema.validate({"opt_int": 42})
    assert len(errors) == 1
    assert "Missing required parameter" in errors[0]
    
    # Unknown parameter
    errors = schema.validate({"req_str": "hello", "unknown": 1})
    assert len(errors) == 1
    assert "Unknown parameter" in errors[0]
    
    # Type mismatch (string expected, got int)
    errors = schema.validate({"req_str": 123})
    assert len(errors) == 1
    assert "type 'string'" in errors[0]
    
    # Type mismatch (int expected, got string)
    errors = schema.validate({"req_str": "hello", "opt_int": "not_an_int"})
    assert len(errors) == 1
    assert "type 'integer'" in errors[0]
    
    # Enum mismatch
    errors = schema.validate({"req_str": "hello", "opt_enum": "C"})
    assert len(errors) == 1
    assert "not in enum" in errors[0]

def test_successful_dispatch():
    schema = ParameterSchema({
        "a": {"type": "integer", "required": True},
        "b": {"type": "integer", "required": True}
    })
    def add_handler(args): return args["a"] + args["b"]
    tool = ToolDefinition("add", "Add two numbers", schema, add_handler)
    
    registry = ToolRegistry()
    registry.register(tool)
    router = ToolRouter(registry)
    
    call = ToolCall("add", {"a": 2, "b": 3})
    result = router.route(call)
    
    assert result.success is True
    assert result.result == 5
    assert result.error is None
    assert result.tool_name == "add"
    assert result.call_id == call.call_id
    assert result.duration_ms >= 0

def test_routing_errors():
    schema = ParameterSchema({"x": {"type": "integer", "required": True}})
    def error_handler(args): raise RuntimeError("handler failed")
    tool = ToolDefinition("err_tool", "Always fails", schema, error_handler)
    
    registry = ToolRegistry()
    registry.register(tool)
    router = ToolRouter(registry)
    
    # 1. Unknown tool
    call1 = ToolCall("unknown", {})
    res1 = router.route(call1)
    assert res1.success is False
    assert "Unknown tool" in res1.error
    assert res1.result is None
    
    # 2. Validation error
    call2 = ToolCall("err_tool", {"x": "not_an_int"})
    res2 = router.route(call2)
    assert res2.success is False
    assert "Validation failed" in res2.error
    
    # 3. Handler error
    call3 = ToolCall("err_tool", {"x": 10})
    res3 = router.route(call3)
    assert res3.success is False
    assert "Handler error: handler failed" in res3.error

def test_middleware_and_stats():
    schema = ParameterSchema({"x": {"type": "integer"}})
    def identity_handler(args): return args.get("x", 0)
    tool = ToolDefinition("id_tool", "Identity", schema, identity_handler)
    
    registry = ToolRegistry()
    registry.register(tool)
    
    logger = LoggingMiddleware()
    router = ToolRouter(registry, [logger])
    
    call1 = ToolCall("id_tool", {"x": 5})
    router.route(call1)
    
    call2 = ToolCall("unknown", {})
    router.route(call2)
    
    call3 = ToolCall("id_tool", {"x": "bad"}) # validation error
    router.route(call3)
    
    # Check stats
    stats = router.get_stats()
    assert stats["id_tool"]["calls"] == 2
    assert stats["id_tool"]["errors"] == 1 # the validation error
    assert stats["id_tool"]["total_ms"] >= 0
    
    assert stats["unknown"]["calls"] == 1
    assert stats["unknown"]["errors"] == 1
    
    # Check logs
    logs = logger.get_log()
    assert len(logs) == 6 # 3 calls * 2 logs (before and after)
    assert any("[BEFORE] tool=id_tool" in log for log in logs)
    assert any("OK tool=id_tool" in log for log in logs)
    assert any("ERROR tool=unknown" in log for log in logs)
    assert any("ERROR tool=id_tool" in log for log in logs)
