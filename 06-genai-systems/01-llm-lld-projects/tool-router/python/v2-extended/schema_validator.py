import json
from typing import Any, Dict, List, Tuple, Optional

_TYPE_MAP: Dict[str, type] = {
    "string": str,
    "integer": int,
    "float": float,
    "boolean": bool,
    "array": list,
}

class SchemaValidator:
    """Strict JSON Schema argument validator with repair fallback."""

    def __init__(self, parameters: Optional[Dict[str, dict]] = None) -> None:
        if parameters is not None and not isinstance(parameters, dict):
            raise ValueError("parameters must be a dict")
        self._parameters: Dict[str, dict] = dict(parameters) if parameters else {}

    def validate_and_repair(self, args: Any) -> Tuple[bool, Any, List[str]]:
        """
        Validates arguments against the schema. If validation fails, attempts to repair.
        Returns: (success, repaired_arguments, errors)
        """
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                return False, args, ["Failed to parse JSON string"]

        if args is None:
            args = {}

        if not isinstance(args, dict):
            return False, args, ["Arguments must be a dictionary"]

        repaired_args = {}
        errors = []

        # Check required parameters
        for name, spec in self._parameters.items():
            if spec.get("required", False) and name not in args:
                errors.append(f"Missing required parameter: {name}")

        # Check each supplied argument
        for name, value in args.items():
            if name not in self._parameters:
                # extra arguments are silently accepted
                continue

            spec = self._parameters[name]
            expected_type = spec.get("type")

            # Repair logic
            if expected_type is not None and value is not None:
                repaired_value, err = self._repair_type(name, value, expected_type)
                if err:
                    errors.append(err)
                else:
                    repaired_args[name] = repaired_value
            else:
                repaired_args[name] = value

            # Enum check
            allowed = spec.get("enum")
            if allowed is not None and repaired_args.get(name) not in allowed:
                errors.append(
                    f"Parameter '{name}' must be one of {allowed}, got {repaired_args.get(name)!r}"
                )

        if errors:
            return False, args, errors

        return True, repaired_args, []

    def _repair_type(self, name: str, value: Any, expected_type: str) -> Tuple[Any, Optional[str]]:
        if expected_type not in _TYPE_MAP:
            return value, f"Unknown type '{expected_type}' for parameter '{name}'"

        if expected_type == "integer":
            if isinstance(value, str):
                try:
                    return int(value), None
                except ValueError:
                    return value, f"Cannot coerce string '{value}' to integer for '{name}'"
            elif isinstance(value, float):
                return int(value), None
            elif isinstance(value, bool):
                return value, f"Parameter '{name}' expected type 'integer', got bool"
            elif not isinstance(value, int):
                return value, f"Parameter '{name}' expected type 'integer', got {type(value).__name__}"

        elif expected_type == "float":
            if isinstance(value, str):
                try:
                    return float(value), None
                except ValueError:
                    return value, f"Cannot coerce string '{value}' to float for '{name}'"
            elif isinstance(value, int) and not isinstance(value, bool):
                return float(value), None
            elif isinstance(value, bool):
                return value, f"Parameter '{name}' expected type 'float', got bool"
            elif not isinstance(value, float):
                return value, f"Parameter '{name}' expected type 'float', got {type(value).__name__}"

        elif expected_type == "boolean":
            if isinstance(value, str):
                lower_val = value.lower()
                if lower_val in ('true', '1', 'yes'):
                    return True, None
                elif lower_val in ('false', '0', 'no'):
                    return False, None
                else:
                    return value, f"Cannot coerce string '{value}' to boolean for '{name}'"
            elif not isinstance(value, bool):
                return value, f"Parameter '{name}' expected type 'boolean', got {type(value).__name__}"

        elif expected_type == "array":
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed, None
                    else:
                        return value, f"Parsed JSON is not an array for '{name}'"
                except json.JSONDecodeError:
                    return value, f"Cannot coerce string to array for '{name}'"
            elif not isinstance(value, list):
                return value, f"Parameter '{name}' expected type 'array', got {type(value).__name__}"

        elif expected_type == "string":
            if isinstance(value, (int, float, bool)):
                return str(value), None
            elif isinstance(value, (dict, list)):
                return json.dumps(value), None
            elif not isinstance(value, str):
                return value, f"Parameter '{name}' expected type 'string', got {type(value).__name__}"

        return value, None
