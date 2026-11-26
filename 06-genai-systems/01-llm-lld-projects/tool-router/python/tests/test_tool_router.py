"""
Tests for Tool Router (v1-basic).
"""
import unittest
import sys
import os

# Add v1-basic to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))


class TestParameterSchema(unittest.TestCase):
    """Tests for ParameterSchema."""

    def setUp(self):
        from schema import ParameterSchema
        self.ParameterSchema = ParameterSchema

    def test_validate_required_present(self):
        """Required parameters present should produce no errors."""
        schema = self.ParameterSchema({
            "name": {"type": "string", "required": True},
        })
        errors = schema.validate({"name": "Alice"})
        self.assertEqual(errors, [])

    def test_validate_required_missing(self):
        """Missing required parameter should produce an error."""
        schema = self.ParameterSchema({
            "name": {"type": "string", "required": True},
        })
        errors = schema.validate({})
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing required parameter: name", errors[0])

    def test_validate_multiple_required_missing(self):
        """Multiple missing required parameters should produce multiple errors."""
        schema = self.ParameterSchema({
            "a": {"type": "string", "required": True},
            "b": {"type": "integer", "required": True},
        })
        errors = schema.validate({})
        self.assertEqual(len(errors), 2)

    def test_validate_optional_absent(self):
        """Optional parameters absent should produce no errors."""
        schema = self.ParameterSchema({
            "color": {"type": "string", "required": False},
        })
        errors = schema.validate({})
        self.assertEqual(errors, [])

    def test_validate_type_string(self):
        """String type should accept str values."""
        schema = self.ParameterSchema({"x": {"type": "string"}})
        self.assertEqual(schema.validate({"x": "hello"}), [])
        errors = schema.validate({"x": 42})
        self.assertEqual(len(errors), 1)

    def test_validate_type_integer(self):
        """Integer type should accept int, reject bool and float."""
        schema = self.ParameterSchema({"x": {"type": "integer"}})
        self.assertEqual(schema.validate({"x": 42}), [])
        errors = schema.validate({"x": 3.14})
        self.assertEqual(len(errors), 1)
        errors = schema.validate({"x": True})
        self.assertEqual(len(errors), 1)

    def test_validate_type_float(self):
        """Float type should accept float and int, reject bool."""
        schema = self.ParameterSchema({"x": {"type": "float"}})
        self.assertEqual(schema.validate({"x": 3.14}), [])
        self.assertEqual(schema.validate({"x": 42}), [])
        errors = schema.validate({"x": "text"})
        self.assertEqual(len(errors), 1)
        errors = schema.validate({"x": True})
        self.assertEqual(len(errors), 1)

    def test_validate_type_boolean(self):
        """Boolean type should accept bool, reject int."""
        schema = self.ParameterSchema({"x": {"type": "boolean"}})
        self.assertEqual(schema.validate({"x": True}), [])
        self.assertEqual(schema.validate({"x": False}), [])
        errors = schema.validate({"x": 1})
        self.assertEqual(len(errors), 1)

    def test_validate_type_array(self):
        """Array type should accept list."""
        schema = self.ParameterSchema({"x": {"type": "array"}})
        self.assertEqual(schema.validate({"x": [1, 2, 3]}), [])
        errors = schema.validate({"x": "not a list"})
        self.assertEqual(len(errors), 1)

    def test_validate_enum_valid(self):
        """Enum-constrained parameter with valid value should pass."""
        schema = self.ParameterSchema({
            "color": {"type": "string", "enum": ["red", "green", "blue"]},
        })
        self.assertEqual(schema.validate({"color": "red"}), [])

    def test_validate_enum_invalid(self):
        """Enum-constrained parameter with invalid value should fail."""
        schema = self.ParameterSchema({
            "color": {"type": "string", "enum": ["red", "green", "blue"]},
        })
        errors = schema.validate({"color": "purple"})
        self.assertEqual(len(errors), 1)
        self.assertIn("must be one of", errors[0])

    def test_validate_none_args(self):
        """None arguments should be treated as empty dict."""
        schema = self.ParameterSchema({
            "x": {"type": "string", "required": False},
        })
        self.assertEqual(schema.validate(None), [])

    def test_validate_none_args_with_required(self):
        """None arguments with required parameter should fail."""
        schema = self.ParameterSchema({
            "x": {"type": "string", "required": True},
        })
        errors = schema.validate(None)
        self.assertEqual(len(errors), 1)

    def test_extra_arguments_ignored(self):
        """Extra arguments not in schema should be silently accepted."""
        schema = self.ParameterSchema({"x": {"type": "string"}})
        errors = schema.validate({"x": "hello", "extra": 99})
        self.assertEqual(errors, [])

    def test_empty_schema(self):
        """Empty schema should accept any arguments."""
        schema = self.ParameterSchema({})
        self.assertEqual(schema.validate({"anything": "goes"}), [])

    def test_no_params_schema(self):
        """Schema with None parameters should accept any arguments."""
        schema = self.ParameterSchema(None)
        self.assertEqual(schema.validate({}), [])

    def test_get_parameter_names(self):
        """get_parameter_names should return all parameter names."""
        schema = self.ParameterSchema({"a": {}, "b": {}, "c": {}})
        self.assertEqual(sorted(schema.get_parameter_names()), ["a", "b", "c"])

    def test_get_required_parameters(self):
        """get_required_parameters should return only required names."""
        schema = self.ParameterSchema({
            "a": {"required": True},
            "b": {"required": False},
            "c": {"required": True},
        })
        self.assertEqual(sorted(schema.get_required_parameters()), ["a", "c"])

    def test_parameters_property(self):
        """parameters property should return a copy of the specs."""
        spec = {"x": {"type": "string"}}
        schema = self.ParameterSchema(spec)
        params = schema.parameters
        self.assertEqual(params, spec)
        # Modifying the copy should not affect the schema
        params["y"] = {"type": "integer"}
        self.assertNotIn("y", schema.parameters)


class TestToolDefinition(unittest.TestCase):
    """Tests for ToolDefinition dataclass."""

    def setUp(self):
        from tool import ToolDefinition
        from schema import ParameterSchema
        self.ToolDefinition = ToolDefinition
        self.ParameterSchema = ParameterSchema

    def test_create_tool_definition(self):
        """ToolDefinition should store name, description, schema, handler."""
        schema = self.ParameterSchema({})
        handler = lambda args: None
        td = self.ToolDefinition(
            name="test_tool",
            description="A test tool",
            parameter_schema=schema,
            handler=handler,
        )
        self.assertEqual(td.name, "test_tool")
        self.assertEqual(td.description, "A test tool")
        self.assertIs(td.parameter_schema, schema)
        self.assertIs(td.handler, handler)


class TestToolCall(unittest.TestCase):
    """Tests for ToolCall dataclass."""

    def setUp(self):
        from tool import ToolCall
        self.ToolCall = ToolCall

    def test_auto_generated_call_id(self):
        """ToolCall should auto-generate a UUID call_id."""
        call = self.ToolCall(tool_name="test")
        self.assertTrue(len(call.call_id) > 0)

    def test_unique_call_ids(self):
        """Each ToolCall should have a unique call_id."""
        c1 = self.ToolCall(tool_name="test")
        c2 = self.ToolCall(tool_name="test")
        self.assertNotEqual(c1.call_id, c2.call_id)

    def test_default_arguments(self):
        """Default arguments should be an empty dict."""
        call = self.ToolCall(tool_name="test")
        self.assertEqual(call.arguments, {})

    def test_custom_arguments(self):
        """Custom arguments should be stored."""
        call = self.ToolCall(tool_name="test", arguments={"k": "v"})
        self.assertEqual(call.arguments, {"k": "v"})

    def test_custom_call_id(self):
        """Explicit call_id should override auto-generation."""
        call = self.ToolCall(tool_name="test", call_id="my-id")
        self.assertEqual(call.call_id, "my-id")


class TestToolResult(unittest.TestCase):
    """Tests for ToolResult dataclass."""

    def setUp(self):
        from tool import ToolResult
        self.ToolResult = ToolResult

    def test_success_result(self):
        """Success result should have correct fields."""
        r = self.ToolResult(
            call_id="id1", tool_name="t", success=True, result=42,
        )
        self.assertTrue(r.success)
        self.assertEqual(r.result, 42)
        self.assertIsNone(r.error)

    def test_error_result(self):
        """Error result should have correct fields."""
        r = self.ToolResult(
            call_id="id1", tool_name="t", success=False, error="oops",
        )
        self.assertFalse(r.success)
        self.assertIsNone(r.result)
        self.assertEqual(r.error, "oops")

    def test_default_duration(self):
        """Default duration_ms should be 0.0."""
        r = self.ToolResult(call_id="id1", tool_name="t", success=True)
        self.assertEqual(r.duration_ms, 0.0)


class TestToolRegistry(unittest.TestCase):
    """Tests for ToolRegistry."""

    def setUp(self):
        from router import ToolRegistry
        from tool import ToolDefinition
        from schema import ParameterSchema
        self.ToolRegistry = ToolRegistry
        self.ToolDefinition = ToolDefinition
        self.ParameterSchema = ParameterSchema

    def _make_tool(self, name: str = "test_tool") -> "ToolDefinition":
        return self.ToolDefinition(
            name=name,
            description=f"Tool {name}",
            parameter_schema=self.ParameterSchema({}),
            handler=lambda args: None,
        )

    def test_register_and_get(self):
        """Registered tool should be retrievable by name."""
        reg = self.ToolRegistry()
        tool = self._make_tool("calc")
        reg.register(tool)
        self.assertIs(reg.get("calc"), tool)

    def test_get_missing(self):
        """Getting a non-existent tool should return None."""
        reg = self.ToolRegistry()
        self.assertIsNone(reg.get("missing"))

    def test_has(self):
        """has() should return True for registered tools, False otherwise."""
        reg = self.ToolRegistry()
        reg.register(self._make_tool("alpha"))
        self.assertTrue(reg.has("alpha"))
        self.assertFalse(reg.has("beta"))

    def test_list_tools(self):
        """list_tools should return all registered tools."""
        reg = self.ToolRegistry()
        reg.register(self._make_tool("a"))
        reg.register(self._make_tool("b"))
        names = sorted(t.name for t in reg.list_tools())
        self.assertEqual(names, ["a", "b"])

    def test_list_tools_empty(self):
        """list_tools on empty registry should return empty list."""
        reg = self.ToolRegistry()
        self.assertEqual(reg.list_tools(), [])

    def test_duplicate_registration_raises(self):
        """Registering the same tool name twice should raise ValueError."""
        reg = self.ToolRegistry()
        reg.register(self._make_tool("dup"))
        with self.assertRaises(ValueError):
            reg.register(self._make_tool("dup"))

    def test_empty_name_raises(self):
        """Registering a tool with empty name should raise ValueError."""
        reg = self.ToolRegistry()
        tool = self._make_tool("")
        tool.name = ""
        with self.assertRaises(ValueError):
            reg.register(tool)

    def test_whitespace_name_raises(self):
        """Registering a tool with whitespace-only name should raise ValueError."""
        reg = self.ToolRegistry()
        tool = self._make_tool("x")
        tool.name = "   "
        with self.assertRaises(ValueError):
            reg.register(tool)


class TestToolRouter(unittest.TestCase):
    """Tests for ToolRouter."""

    def setUp(self):
        from router import ToolRouter, ToolRegistry
        from tool import ToolCall, ToolDefinition
        from schema import ParameterSchema
        self.ToolRouter = ToolRouter
        self.ToolRegistry = ToolRegistry
        self.ToolCall = ToolCall
        self.ToolDefinition = ToolDefinition
        self.ParameterSchema = ParameterSchema

        # Set up a registry with a simple echo tool
        self.registry = ToolRegistry()
        echo_schema = ParameterSchema({
            "message": {"type": "string", "required": True},
        })
        echo_tool = ToolDefinition(
            name="echo",
            description="Echoes the message",
            parameter_schema=echo_schema,
            handler=lambda args: args["message"],
        )
        self.registry.register(echo_tool)

        # A tool that raises an exception
        fail_schema = ParameterSchema({})
        fail_tool = ToolDefinition(
            name="fail",
            description="Always fails",
            parameter_schema=fail_schema,
            handler=lambda args: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        self.registry.register(fail_tool)

        self.router = ToolRouter(registry=self.registry)

    def test_successful_dispatch(self):
        """Valid call should dispatch and return success result."""
        call = self.ToolCall(tool_name="echo", arguments={"message": "hi"})
        result = self.router.route(call)
        self.assertTrue(result.success)
        self.assertEqual(result.result, "hi")
        self.assertIsNone(result.error)
        self.assertEqual(result.call_id, call.call_id)
        self.assertEqual(result.tool_name, "echo")
        self.assertGreaterEqual(result.duration_ms, 0.0)

    def test_unknown_tool(self):
        """Call to unknown tool should return error result."""
        call = self.ToolCall(tool_name="nonexistent", arguments={})
        result = self.router.route(call)
        self.assertFalse(result.success)
        self.assertIn("Unknown tool", result.error)

    def test_validation_failure(self):
        """Call with missing required param should return validation error."""
        call = self.ToolCall(tool_name="echo", arguments={})
        result = self.router.route(call)
        self.assertFalse(result.success)
        self.assertIn("Validation failed", result.error)
        self.assertIn("message", result.error)

    def test_validation_type_error(self):
        """Call with wrong argument type should return validation error."""
        call = self.ToolCall(tool_name="echo", arguments={"message": 123})
        result = self.router.route(call)
        self.assertFalse(result.success)
        self.assertIn("Validation failed", result.error)

    def test_handler_exception(self):
        """Handler that raises should return error result, not crash."""
        call = self.ToolCall(tool_name="fail", arguments={})
        result = self.router.route(call)
        self.assertFalse(result.success)
        self.assertIn("Handler error", result.error)
        self.assertIn("boom", result.error)

    def test_handler_returns_none(self):
        """Handler returning None should produce success with None result."""
        self.registry.register(self.ToolDefinition(
            name="noop",
            description="Returns nothing",
            parameter_schema=self.ParameterSchema({}),
            handler=lambda args: None,
        ))
        call = self.ToolCall(tool_name="noop", arguments={})
        result = self.router.route(call)
        self.assertTrue(result.success)
        self.assertIsNone(result.result)

    def test_duration_is_positive(self):
        """Result duration_ms should be non-negative."""
        call = self.ToolCall(tool_name="echo", arguments={"message": "timing"})
        result = self.router.route(call)
        self.assertGreaterEqual(result.duration_ms, 0.0)

    def test_empty_arguments_dict(self):
        """Call with empty arguments to a tool with no required params should succeed."""
        self.registry.register(self.ToolDefinition(
            name="noparam",
            description="No params needed",
            parameter_schema=self.ParameterSchema({}),
            handler=lambda args: "ok",
        ))
        call = self.ToolCall(tool_name="noparam", arguments={})
        result = self.router.route(call)
        self.assertTrue(result.success)
        self.assertEqual(result.result, "ok")

    def test_none_arguments(self):
        """ToolCall with None-like empty arguments should be handled."""
        self.registry.register(self.ToolDefinition(
            name="lenient",
            description="Accepts anything",
            parameter_schema=self.ParameterSchema({}),
            handler=lambda args: "done",
        ))
        call = self.ToolCall(tool_name="lenient", arguments={})
        result = self.router.route(call)
        self.assertTrue(result.success)

    def test_special_characters_in_tool_name(self):
        """Tool names with special characters should work."""
        self.registry.register(self.ToolDefinition(
            name="my-tool_v2.1",
            description="Special name",
            parameter_schema=self.ParameterSchema({}),
            handler=lambda args: "special",
        ))
        call = self.ToolCall(tool_name="my-tool_v2.1", arguments={})
        result = self.router.route(call)
        self.assertTrue(result.success)
        self.assertEqual(result.result, "special")


class TestToolRouterMetrics(unittest.TestCase):
    """Tests for ToolRouter metrics tracking."""

    def setUp(self):
        from router import ToolRouter, ToolRegistry
        from tool import ToolCall, ToolDefinition
        from schema import ParameterSchema
        self.ToolRouter = ToolRouter
        self.ToolCall = ToolCall

        registry = ToolRegistry()
        registry.register(ToolDefinition(
            name="counter",
            description="Counts calls",
            parameter_schema=ParameterSchema({}),
            handler=lambda args: "counted",
        ))
        registry.register(ToolDefinition(
            name="broken",
            description="Always errors",
            parameter_schema=ParameterSchema({
                "x": {"type": "string", "required": True},
            }),
            handler=lambda args: args["x"],
        ))
        self.router = ToolRouter(registry=registry)

    def test_stats_after_calls(self):
        """Stats should track calls and errors per tool."""
        self.router.route(self.ToolCall(tool_name="counter", arguments={}))
        self.router.route(self.ToolCall(tool_name="counter", arguments={}))
        self.router.route(self.ToolCall(tool_name="counter", arguments={}))
        stats = self.router.get_stats()
        self.assertEqual(stats["counter"]["calls"], 3)
        self.assertEqual(stats["counter"]["errors"], 0)
        self.assertGreater(stats["counter"]["total_ms"], 0.0)

    def test_stats_error_counting(self):
        """Errors should be tracked separately in stats."""
        # Validation failure
        self.router.route(self.ToolCall(tool_name="broken", arguments={}))
        stats = self.router.get_stats()
        self.assertEqual(stats["broken"]["calls"], 1)
        self.assertEqual(stats["broken"]["errors"], 1)

    def test_stats_unknown_tool(self):
        """Unknown tool calls should appear in stats."""
        self.router.route(self.ToolCall(tool_name="ghost", arguments={}))
        stats = self.router.get_stats()
        self.assertEqual(stats["ghost"]["calls"], 1)
        self.assertEqual(stats["ghost"]["errors"], 1)

    def test_stats_empty_initially(self):
        """Stats should be empty before any calls."""
        stats = self.router.get_stats()
        self.assertEqual(stats, {})

    def test_stats_returns_copy(self):
        """get_stats should return a copy, not a reference."""
        self.router.route(self.ToolCall(tool_name="counter", arguments={}))
        stats = self.router.get_stats()
        stats["counter"]["calls"] = 999
        real_stats = self.router.get_stats()
        self.assertEqual(real_stats["counter"]["calls"], 1)


class TestMiddleware(unittest.TestCase):
    """Tests for ToolMiddleware and LoggingMiddleware."""

    def setUp(self):
        from router import ToolRouter, ToolRegistry, LoggingMiddleware
        from tool import ToolCall, ToolDefinition
        from schema import ParameterSchema
        self.ToolRouter = ToolRouter
        self.ToolCall = ToolCall
        self.LoggingMiddleware = LoggingMiddleware

        self.registry = ToolRegistry()
        self.registry.register(ToolDefinition(
            name="greet",
            description="Greeting tool",
            parameter_schema=ParameterSchema({
                "name": {"type": "string", "required": True},
            }),
            handler=lambda args: f"Hello, {args['name']}!",
        ))

    def test_logging_middleware_records(self):
        """LoggingMiddleware should record before and after messages."""
        logger = self.LoggingMiddleware()
        router = self.ToolRouter(registry=self.registry, middleware=[logger])
        call = self.ToolCall(tool_name="greet", arguments={"name": "Alice"})
        router.route(call)
        log = logger.get_log()
        self.assertEqual(len(log), 2)
        self.assertIn("[BEFORE]", log[0])
        self.assertIn("[AFTER]", log[1])
        self.assertIn("greet", log[0])
        self.assertIn("OK", log[1])

    def test_logging_middleware_error(self):
        """LoggingMiddleware should record errors."""
        logger = self.LoggingMiddleware()
        router = self.ToolRouter(registry=self.registry, middleware=[logger])
        call = self.ToolCall(tool_name="unknown", arguments={})
        router.route(call)
        log = logger.get_log()
        self.assertEqual(len(log), 2)
        self.assertIn("ERROR", log[1])

    def test_multiple_middleware_chaining(self):
        """Multiple middleware should be called in order (before) and reverse (after)."""
        from router import ToolMiddleware

        order = []

        class OrderMiddleware(ToolMiddleware):
            def __init__(self, tag):
                self.tag = tag

            def before_call(self, call):
                order.append(f"before-{self.tag}")
                return call

            def after_call(self, call, result):
                order.append(f"after-{self.tag}")
                return result

        mw1 = OrderMiddleware("A")
        mw2 = OrderMiddleware("B")
        router = self.ToolRouter(
            registry=self.registry, middleware=[mw1, mw2],
        )
        call = self.ToolCall(tool_name="greet", arguments={"name": "Test"})
        router.route(call)
        self.assertEqual(order, ["before-A", "before-B", "after-B", "after-A"])

    def test_no_middleware(self):
        """Router with no middleware should still work."""
        router = self.ToolRouter(registry=self.registry, middleware=[])
        call = self.ToolCall(tool_name="greet", arguments={"name": "No MW"})
        result = router.route(call)
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Hello, No MW!")

    def test_middleware_on_error_calls(self):
        """Middleware after_call should run even on failed calls."""
        logger = self.LoggingMiddleware()
        router = self.ToolRouter(registry=self.registry, middleware=[logger])
        # Missing required param
        call = self.ToolCall(tool_name="greet", arguments={})
        router.route(call)
        log = logger.get_log()
        self.assertEqual(len(log), 2)
        self.assertIn("ERROR", log[1])

    def test_logging_middleware_get_log_returns_copy(self):
        """get_log should return a copy of the log."""
        logger = self.LoggingMiddleware()
        router = self.ToolRouter(registry=self.registry, middleware=[logger])
        call = self.ToolCall(tool_name="greet", arguments={"name": "Copy"})
        router.route(call)
        log = logger.get_log()
        log.clear()
        self.assertEqual(len(logger.get_log()), 2)


if __name__ == "__main__":
    unittest.main()
