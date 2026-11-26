import time
from typing import Dict, List, Any
from models import ToolCall, ToolResult, ToolMiddleware, LoggingMiddleware
from registry import ToolRegistry

class ToolRouter:
    def __init__(self, registry: ToolRegistry, middleware: List[ToolMiddleware] = None):
        self._registry = registry
        self._middleware = middleware or []
        self._stats: Dict[str, dict] = {}

    def _init_stats(self, tool_name: str):
        if tool_name not in self._stats:
            self._stats[tool_name] = {"calls": 0, "errors": 0, "total_ms": 0.0}

    def route(self, call: ToolCall) -> ToolResult:
        # Run before_call middleware in registration order
        current_call = call
        for mw in self._middleware:
            current_call = mw.before_call(current_call)

        tool_name = current_call.tool_name
        self._init_stats(tool_name)
        
        start_time = time.time()
        success = False
        result_value = None
        error_msg = None

        tool_def = self._registry.get(tool_name)
        
        if not tool_def:
            error_msg = f"Unknown tool: {tool_name}"
        else:
            validation_errors = tool_def.parameter_schema.validate(current_call.arguments)
            if validation_errors:
                error_msg = f"Validation failed: {', '.join(validation_errors)}"
            else:
                try:
                    result_value = tool_def.handler(current_call.arguments)
                    success = True
                except Exception as e:
                    error_msg = f"Handler error: {str(e)}"
        
        duration_ms = (time.time() - start_time) * 1000.0

        # Update stats
        self._stats[tool_name]["calls"] += 1
        self._stats[tool_name]["total_ms"] += duration_ms
        if not success:
            self._stats[tool_name]["errors"] += 1

        result = ToolResult(
            call_id=current_call.call_id,
            tool_name=tool_name,
            success=success,
            result=result_value,
            error=error_msg,
            duration_ms=duration_ms
        )

        # Run after_call middleware in reverse order
        current_result = result
        for mw in reversed(self._middleware):
            current_result = mw.after_call(current_call, current_result)

        return current_result

    def get_stats(self) -> Dict[str, dict]:
        # Return a deep copy to prevent external mutation
        return {k: v.copy() for k, v in self._stats.items()}
