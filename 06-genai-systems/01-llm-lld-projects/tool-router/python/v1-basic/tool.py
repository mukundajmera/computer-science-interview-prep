"""
Tool data carriers.

Lightweight dataclasses for the three core value objects:

* :class:`ToolDefinition` — bundles a tool's name, description, schema, and handler.
* :class:`ToolCall` — encapsulates an incoming tool-call request.
* :class:`ToolResult` — encapsulates the outcome of a dispatched call.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from schema import ParameterSchema


# ---------------------------------------------------------------------------
# Data carriers
# ---------------------------------------------------------------------------

@dataclass
class ToolDefinition:
    """A registered tool with its metadata, schema, and handler.

    Attributes:
        name: Unique tool identifier.
        description: Human-readable purpose of the tool.
        parameter_schema: Schema declaring expected parameters.
        handler: Callable that executes the tool logic.
                 Signature: ``(args: Dict[str, Any]) -> Any``.
    """

    name: str
    description: str
    parameter_schema: ParameterSchema
    handler: Callable[[Dict[str, Any]], Any]


@dataclass
class ToolCall:
    """An incoming request to invoke a tool.

    Attributes:
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the handler.
        call_id: Unique identifier for this call (auto-generated UUID).
    """

    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ToolResult:
    """Outcome of a dispatched tool call.

    Attributes:
        call_id: Matches the originating :class:`ToolCall`.
        tool_name: Which tool was invoked.
        success: ``True`` if the handler completed without error.
        result: Handler return value (``None`` on failure).
        error: Error message (``None`` on success).
        duration_ms: Wall-clock execution time in milliseconds.
    """

    call_id: str
    tool_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
