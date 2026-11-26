"""
Safe prompt template engine with named-placeholder interpolation.

Provides :class:`PromptTemplate` for rendering templates that contain
``{variable_name}`` placeholders.  Interpolation is purely textual — no
``eval``, ``exec``, or ``str.format()`` with untrusted input is ever used.

Supports:
- Required variables (strict mode raises on missing values)
- Non-strict mode (missing variables resolve to empty string)
- Conditional sections (included only when a variable is provided)
- List rendering (expand a list into formatted multi-line content)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
import typing
from typing import Dict, List, Optional, Set

# Matches {identifier} but NOT {{escaped}}
_PLACEHOLDER_RE = re.compile(r"(?<!\{)\{([A-Za-z_][A-Za-z0-9_]*)\}(?!\})")

# Matches {{literal_braces}} for escaping
_ESCAPED_BRACE_RE = re.compile(r"\{\{(.+?)\}\}")

# Matches conditional blocks: {?var_name}...content...{/?var_name}
_CONDITIONAL_RE = re.compile(
    r"\{\?([A-Za-z_][A-Za-z0-9_]*)\}(.*?)\{/\?\1\}",
    re.DOTALL,
)


@dataclass(frozen=True)
class TemplateVariable:
    """Metadata about a single template placeholder.

    Attributes:
        name:     Placeholder identifier (must match ``[A-Za-z_][A-Za-z0-9_]*``).
        required: If ``True``, omitting a value for this variable raises
                  :class:`ValueError` during rendering.
        default:  Fallback value when the variable is not supplied.
    """

    name: str
    required: bool = True
    default: str = ""
    expected_type: Optional[type] = None


class PromptTemplate:
    """A template string with safe named-placeholder interpolation.

    Placeholders use the syntax ``{variable_name}``.  Literal braces are
    written as ``{{text}}``.

    Conditional sections use ``{?var}...{/?var}`` and are included only
    when *var* has a non-empty value.

    Example::

        tpl = PromptTemplate("Hello, {name}!{?title} Title: {title}{/?title}")
        tpl.render({"name": "Alice", "title": "Dr."})
        # => "Hello, Alice! Title: Dr."

    Safety:
        Interpolation is implemented via :func:`re.sub` with a lookup
        callback.  Values are inserted verbatim — they are never parsed
        or evaluated.  A value containing ``{other}`` is **not**
        re-interpolated.
    """

    def __init__(
        self,
        template_str: str,
        *,
        strict: bool = True,
        variables: Optional[List[TemplateVariable]] = None,
    ) -> None:
        """Initialise a template.

        Args:
            template_str: Raw template text with ``{placeholder}`` syntax.
            strict:       If ``True`` (default), :meth:`render` raises on
                          missing required variables.  If ``False``, missing
                          variables are replaced with their default (empty
                          string if unset).
        """
        if not template_str:
            raise ValueError("Template string must not be empty")
        self._template_str: str = template_str
        self._strict: bool = strict
        self._variables: List[TemplateVariable] = variables if variables is not None else self._parse_placeholders()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, values: Optional[Dict[str, typing.Any]] = None) -> str:
        """Render the template with the supplied values.

        Args:
            values: Mapping of placeholder names to their string values.

        Returns:
            The rendered string.

        Raises:
            ValueError: If *strict* mode is on and a required variable is
                        missing from *values*.
        """
        values = dict(values) if values else {}
        self._validate(values)

        # 1. Resolve conditional sections first
        text = self._resolve_conditionals(self._template_str, values)

        # 2. Substitute placeholders
        text = self._safe_substitute(text, values)

        # 3. Unescape literal braces
        text = _ESCAPED_BRACE_RE.sub(r"{\1}", text)

        return text

    def get_variables(self) -> List[TemplateVariable]:
        """Return discovered placeholder variables."""
        return list(self._variables)

    def get_variable_names(self) -> Set[str]:
        """Return the set of placeholder names in this template."""
        return {v.name for v in self._variables}

    @staticmethod
    def render_list(name: str, items: List[str], *, bullet: str = "- ") -> str:
        """Render a list of items as a formatted multi-line string.

        This is a helper intended to prepare a value that will be passed
        into :meth:`render` as a single placeholder value.

        Args:
            name:   A label printed as a header line.
            items:  The list entries.
            bullet: Prefix for each item line.

        Returns:
            A formatted string ready for template substitution.
        """
        if not items:
            return ""
        header = f"{name}:"
        lines = [f"{bullet}{item}" for item in items]
        return header + "\n" + "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_placeholders(self) -> List[TemplateVariable]:
        """Discover all unique placeholders in the template string."""
        # Collect from plain placeholders and conditional blocks
        names: list[str] = _PLACEHOLDER_RE.findall(self._template_str)
        cond_names: list[str] = _CONDITIONAL_RE.findall(self._template_str)
        for cond_name, _ in cond_names:  # type: ignore[misc]
            if cond_name not in names:
                names.append(cond_name)

        seen: set[str] = set()
        variables: List[TemplateVariable] = []
        for name in names:
            if name not in seen:
                seen.add(name)
                variables.append(TemplateVariable(name=name))
        return variables

    def _validate(self, values: Dict[str, typing.Any]) -> None:
        """Raise if any required variable is missing (strict mode only)."""
        provided = set(values.keys())
        for var in self._variables:
            if var.name in provided:
                val = values[var.name]
                if var.expected_type is not None and not isinstance(val, var.expected_type):
                    raise TypeError(f"Variable '{var.name}' expected type {var.expected_type}, got {type(val)}")
            elif self._strict and var.required:
                raise ValueError(
                    f"Missing required template variable: '{var.name}'"
                )

    def _safe_substitute(self, text: str, values: Dict[str, typing.Any]) -> str:
        """Replace placeholders with values using regex callback."""

        def _replacer(match: re.Match) -> str:  # type: ignore[type-arg]
            name = match.group(1)
            if name in values:
                return str(values[name])
            # In non-strict mode fall back to default
            for var in self._variables:
                if var.name == name:
                    return var.default
            return match.group(0)  # leave unknown placeholders untouched

        return _PLACEHOLDER_RE.sub(_replacer, text)

    @staticmethod
    def _resolve_conditionals(text: str, values: Dict[str, typing.Any]) -> str:
        """Include or strip conditional sections based on provided values."""

        def _cond_replacer(match: re.Match) -> str:  # type: ignore[type-arg]
            var_name = match.group(1)
            body = match.group(2)
            if values.get(var_name):
                return body
            return ""

        return _CONDITIONAL_RE.sub(_cond_replacer, text)
