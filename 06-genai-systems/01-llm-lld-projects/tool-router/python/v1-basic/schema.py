"""
Parameter schema definition and validation.

:class:`ParameterSchema` declares the expected parameters for a tool,
including type constraints, required flags, default values, and enum
membership.  The :meth:`validate` method returns a list of human-readable
error messages (empty list means the arguments are valid).

Supported types:
    - ``"string"``   — ``str``
    - ``"integer"``  — ``int`` (but not ``bool``)
    - ``"float"``    — ``float`` or ``int``
    - ``"boolean"``  — ``bool``
    - ``"array"``    — ``list``
"""

from __future__ import annotations

from typing import Any, Dict, List


# Type string → Python type(s) accepted
_TYPE_MAP: Dict[str, type] = {
    "string": str,
    "integer": int,
    "float": float,
    "boolean": bool,
    "array": list,
}


class ParameterSchema:
    """Schema describing the expected parameters for a tool.

    Each parameter is a dict entry keyed by name with the following
    optional fields:

    - ``type`` (str): one of the supported type names.
    - ``required`` (bool): whether the parameter must be present (default False).
    - ``description`` (str): human-readable explanation.
    - ``default``: value to assume when the parameter is absent.
    - ``enum`` (list): allowed values for the parameter.

    Args:
        parameters: Mapping of parameter name → specification dict.

    Raises:
        ValueError: If *parameters* is not a dict.
    """

    def __init__(self, parameters: Dict[str, dict] | None = None) -> None:
        if parameters is not None and not isinstance(parameters, dict):
            raise ValueError("parameters must be a dict")
        self._parameters: Dict[str, dict] = dict(parameters) if parameters else {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, args: Dict[str, Any] | None) -> List[str]:
        """Validate *args* against this schema.

        Args:
            args: The arguments dict to validate. ``None`` is treated as
                an empty dict.

        Returns:
            A list of error message strings.  An empty list means the
            arguments are valid.
        """
        if args is None:
            args = {}
        errors: List[str] = []

        # Check required parameters
        for name, spec in self._parameters.items():
            if spec.get("required", False) and name not in args:
                errors.append(f"Missing required parameter: {name}")

        # Check each supplied argument
        for name, value in args.items():
            if name not in self._parameters:
                continue  # extra arguments are silently accepted
            spec = self._parameters[name]
            # Type check
            expected_type = spec.get("type")
            if expected_type is not None and value is not None:
                type_error = self._check_type(name, value, expected_type)
                if type_error:
                    errors.append(type_error)
                    continue  # skip enum check if type is wrong
            # Enum check
            allowed = spec.get("enum")
            if allowed is not None and value not in allowed:
                errors.append(
                    f"Parameter '{name}' must be one of {allowed}, got {value!r}"
                )

        return errors

    def get_parameter_names(self) -> List[str]:
        """Return all parameter names in this schema."""
        return list(self._parameters.keys())

    def get_required_parameters(self) -> List[str]:
        """Return parameter names that are marked as required."""
        return [
            name
            for name, spec in self._parameters.items()
            if spec.get("required", False)
        ]

    @property
    def parameters(self) -> Dict[str, dict]:
        """Return a copy of the raw parameter specifications."""
        return dict(self._parameters)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_type(name: str, value: Any, expected_type: str) -> str | None:
        """Return an error message if *value* does not match *expected_type*.

        Returns ``None`` when the value is acceptable.
        """
        if expected_type not in _TYPE_MAP:
            return f"Unknown type '{expected_type}' for parameter '{name}'"

        if expected_type == "integer":
            # bool is a subclass of int in Python — reject it explicitly
            if isinstance(value, bool) or not isinstance(value, int):
                return (
                    f"Parameter '{name}' expected type 'integer', "
                    f"got {type(value).__name__}"
                )
        elif expected_type == "float":
            # Accept both float and int (auto-promotion)
            if not isinstance(value, (float, int)) or isinstance(value, bool):
                return (
                    f"Parameter '{name}' expected type 'float', "
                    f"got {type(value).__name__}"
                )
        elif expected_type == "boolean":
            if not isinstance(value, bool):
                return (
                    f"Parameter '{name}' expected type 'boolean', "
                    f"got {type(value).__name__}"
                )
        else:
            py_type = _TYPE_MAP[expected_type]
            if not isinstance(value, py_type):
                return (
                    f"Parameter '{name}' expected type '{expected_type}', "
                    f"got {type(value).__name__}"
                )
        return None
