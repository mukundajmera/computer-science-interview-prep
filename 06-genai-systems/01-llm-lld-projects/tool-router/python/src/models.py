import uuid
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

class ParameterSchema:
    def __init__(self, parameters: Dict[str, dict]):
        self.parameters = parameters

    def validate(self, args: Dict[str, Any]) -> List[str]:
        errors = []
        for param_name, schema in self.parameters.items():
            if schema.get("required", False) and param_name not in args:
                errors.append(f"Missing required parameter: '{param_name}'")

        for arg_name, arg_value in args.items():
            if arg_name not in self.parameters:
                errors.append(f"Unknown parameter: '{arg_name}'")
                continue

            schema = self.parameters[arg_name]
            expected_type = schema.get("type")
            
            if expected_type == "string" and not isinstance(arg_value, str):
                errors.append(f"Parameter '{arg_name}' must be of type 'string'")
            elif expected_type == "integer" and (not isinstance(arg_value, int) or isinstance(arg_value, bool)):
                errors.append(f"Parameter '{arg_name}' must be of type 'integer'")
            elif expected_type == "float" and (not isinstance(arg_value, (float, int)) or isinstance(arg_value, bool)):
                errors.append(f"Parameter '{arg_name}' must be of type 'float'")
            elif expected_type == "boolean" and not isinstance(arg_value, bool):
                errors.append(f"Parameter '{arg_name}' must be of type 'boolean'")
            elif expected_type == "array" and not isinstance(arg_value, list):
                errors.append(f"Parameter '{arg_name}' must be of type 'array'")

            enum_values = schema.get("enum")
            if enum_values and arg_value not in enum_values:
                errors.append(f"Parameter '{arg_name}' value {arg_value} not in enum {enum_values}")

        return errors

    def get_parameter_names(self) -> List[str]:
        return list(self.parameters.keys())

    def get_required_parameters(self) -> List[str]:
        return [k for k, v in self.parameters.items() if v.get("required", False)]


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameter_schema: ParameterSchema
    handler: Callable[[Dict[str, Any]], Any]

@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class ToolResult:
    call_id: str
    tool_name: str
    success: bool
    result: Any
    error: Optional[str]
    duration_ms: float

class ToolMiddleware(ABC):
    @abstractmethod
    def before_call(self, call: ToolCall) -> ToolCall:
        pass

    @abstractmethod
    def after_call(self, call: ToolCall, result: ToolResult) -> ToolResult:
        pass

class LoggingMiddleware(ToolMiddleware):
    def __init__(self):
        self._log: List[str] = []

    def before_call(self, call: ToolCall) -> ToolCall:
        self._log.append(f"[BEFORE] tool={call.tool_name} args={call.arguments}")
        return call

    def after_call(self, call: ToolCall, result: ToolResult) -> ToolResult:
        if result.success:
            self._log.append(f"[AFTER] OK tool={call.tool_name} result={result.result} duration={result.duration_ms:.2f}ms")
        else:
            self._log.append(f"[AFTER] ERROR tool={call.tool_name} error={result.error} duration={result.duration_ms:.2f}ms")
        return result
        
    def get_log(self) -> List[str]:
        return list(self._log)
