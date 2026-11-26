"""
Tool router, registry, and middleware.

Provides the core orchestration layer:

* :class:`ToolMiddleware` — abstract hook for pre/post processing.
* :class:`LoggingMiddleware` — concrete middleware that records log messages.
* :class:`ToolRegistry` — stores and retrieves :class:`ToolDefinition` objects.
* :class:`ToolRouter` — validates, dispatches, and captures errors for tool calls.

Design patterns:
    - Registry   — ToolRegistry for O(1) tool lookup
    - Command    — ToolCall encapsulates a request
    - Chain of Responsibility — middleware chain for before/after hooks
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from schema import ParameterSchema
from tool import ToolCall, ToolDefinition, ToolResult


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

class ToolMiddleware(ABC):
    """Abstract hook for pre/post processing of tool calls.

    Subclasses implement :meth:`before_call` and :meth:`after_call` to
    inspect or transform the call and its result.  Middleware instances
    are chained by the :class:`ToolRouter` in registration order.
    """

    @abstractmethod
    def before_call(self, call: ToolCall) -> ToolCall:
        """Invoked before the tool handler is dispatched.

        Args:
            call: The incoming tool call.

        Returns:
            The (potentially modified) tool call.
        """

    @abstractmethod
    def after_call(self, call: ToolCall, result: ToolResult) -> ToolResult:
        """Invoked after the tool handler has been dispatched.

        Args:
            call: The tool call that was dispatched.
            result: The result produced by the handler (or error).

        Returns:
            The (potentially modified) result.
        """


class LoggingMiddleware(ToolMiddleware):
    """Middleware that records log messages for debugging and auditing.

    Each ``before_call`` and ``after_call`` appends a human-readable
    message to an internal log that can be retrieved via :meth:`get_log`.
    """

    def __init__(self) -> None:
        self._log: List[str] = []

    def before_call(self, call: ToolCall) -> ToolCall:
        """Log the dispatch intent and return the call unchanged."""
        self._log.append(
            f"[BEFORE] call_id={call.call_id} tool={call.tool_name} "
            f"args={call.arguments}"
        )
        return call

    def after_call(self, call: ToolCall, result: ToolResult) -> ToolResult:
        """Log the outcome and return the result unchanged."""
        status = "OK" if result.success else f"ERROR: {result.error}"
        self._log.append(
            f"[AFTER]  call_id={call.call_id} tool={call.tool_name} "
            f"status={status} duration_ms={result.duration_ms:.2f}"
        )
        return result

    def get_log(self) -> List[str]:
        """Return all recorded log messages."""
        return list(self._log)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """In-memory registry of tool definitions.

    Tools are stored by name and retrieved in O(1).  Duplicate
    registration raises :class:`ValueError`.

    Design patterns:
        - Registry — centralised tool storage with name-based lookup
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool definition.

        Args:
            tool: The tool to register.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if not tool.name or not tool.name.strip():
            raise ValueError("Tool name must be a non-empty string")
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Return the tool definition for *name*, or ``None``."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        """Return all registered tool definitions."""
        return list(self._tools.values())

    def has(self, name: str) -> bool:
        """Return ``True`` if a tool named *name* is registered."""
        return name in self._tools


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

class ToolRouter:
    """Orchestrator that validates, dispatches, and tracks tool calls.

    The routing flow for each :class:`ToolCall`:

    1. Run ``before_call`` on each middleware (in registration order).
    2. Look up the tool in the registry.
    3. Validate arguments against the tool's :class:`ParameterSchema`.
    4. Invoke the handler, capturing any exceptions.
    5. Run ``after_call`` on each middleware (in reverse order).
    6. Update per-tool metrics.
    7. Return the :class:`ToolResult`.

    Args:
        registry: The tool registry to look up tools from.
        middleware: Optional ordered list of middleware hooks.

    Design patterns:
        - Command   — ToolCall encapsulates a request
        - Chain of Responsibility — middleware before/after hooks
        - Strategy  — handler dispatch via registered callables
    """

    def __init__(
        self,
        registry: ToolRegistry,
        middleware: Optional[List[ToolMiddleware]] = None,
    ) -> None:
        self._registry = registry
        self._middleware: List[ToolMiddleware] = list(middleware) if middleware else []
        self._stats: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(self, call: ToolCall) -> ToolResult:
        """Route a tool call to the appropriate handler.

        Always returns a :class:`ToolResult` — never raises.

        Args:
            call: The tool call to dispatch.

        Returns:
            A :class:`ToolResult` with success/failure, result or error,
            and execution duration.
        """
        start = time.time()

        # --- Middleware: before_call ---
        for mw in self._middleware:
            call = mw.before_call(call)

        # --- Look up tool ---
        tool_def = self._registry.get(call.tool_name)
        if tool_def is None:
            result = ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error=f"Unknown tool: {call.tool_name}",
                duration_ms=self._elapsed_ms(start),
            )
            result = self._run_after_middleware(call, result)
            self._record(call.tool_name, success=False, duration_ms=result.duration_ms)
            return result

        # --- Validate arguments ---
        errors = tool_def.parameter_schema.validate(call.arguments)
        if errors:
            result = ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error="Validation failed: " + "; ".join(errors),
                duration_ms=self._elapsed_ms(start),
            )
            result = self._run_after_middleware(call, result)
            self._record(call.tool_name, success=False, duration_ms=result.duration_ms)
            return result

        # --- Dispatch handler ---
        try:
            handler_result = tool_def.handler(call.arguments)
            result = ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=True,
                result=handler_result,
                duration_ms=self._elapsed_ms(start),
            )
        except Exception as exc:
            result = ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error=f"Handler error: {exc}",
                duration_ms=self._elapsed_ms(start),
            )

        # --- Middleware: after_call ---
        result = self._run_after_middleware(call, result)

        # --- Record metrics ---
        self._record(
            call.tool_name,
            success=result.success,
            duration_ms=result.duration_ms,
        )
        return result

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Return a copy of per-tool execution metrics.

        Returns:
            Dict mapping tool name → ``{"calls": int, "errors": int, "total_ms": float}``.
        """
        return {name: dict(data) for name, data in self._stats.items()}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_after_middleware(
        self, call: ToolCall, result: ToolResult
    ) -> ToolResult:
        """Run after_call hooks in reverse middleware order."""
        for mw in reversed(self._middleware):
            result = mw.after_call(call, result)
        return result

    def _record(self, tool_name: str, *, success: bool, duration_ms: float) -> None:
        """Update per-tool metrics."""
        if tool_name not in self._stats:
            self._stats[tool_name] = {"calls": 0, "errors": 0, "total_ms": 0.0}
        self._stats[tool_name]["calls"] += 1
        if not success:
            self._stats[tool_name]["errors"] += 1
        self._stats[tool_name]["total_ms"] += duration_ms

    @staticmethod
    def _elapsed_ms(start: float) -> float:
        """Return milliseconds elapsed since *start*."""
        return (time.time() - start) * 1000.0
