"""v2-variant: Boolean Filtering Rule AST Interpreter.

Evaluates composite boolean expressions against record dictionaries (e.g., query filters, rules engines)
using terminal field comparisons (Equals, GreaterThan, Contains) and non-terminal logical combinators (And, Or, Not).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class FilterExpression(ABC):
    @abstractmethod
    def interpret(self, record: Dict[str, Any]) -> bool:
        pass


class EqualsExpression(FilterExpression):
    def __init__(self, field: str, expected: Any) -> None:
        self.field = field
        self.expected = expected

    def interpret(self, record: Dict[str, Any]) -> bool:
        if record is None:
            return False
        return record.get(self.field) == self.expected


class GreaterThanExpression(FilterExpression):
    def __init__(self, field: str, threshold: float) -> None:
        self.field = field
        self.threshold = threshold

    def interpret(self, record: Dict[str, Any]) -> bool:
        if record is None or self.field not in record:
            return False
        val = record.get(self.field)
        if isinstance(val, (int, float)):
            return float(val) > self.threshold
        return False


class ContainsExpression(FilterExpression):
    def __init__(self, field: str, substring: str) -> None:
        self.field = field
        self.substring = substring

    def interpret(self, record: Dict[str, Any]) -> bool:
        if record is None or self.field not in record:
            return False
        val = record.get(self.field)
        return val is not None and self.substring in str(val)


class AndExpression(FilterExpression):
    def __init__(self, left: FilterExpression, right: FilterExpression) -> None:
        self.left = left
        self.right = right

    def interpret(self, record: Dict[str, Any]) -> bool:
        return self.left.interpret(record) and self.right.interpret(record)


class OrExpression(FilterExpression):
    def __init__(self, left: FilterExpression, right: FilterExpression) -> None:
        self.left = left
        self.right = right

    def interpret(self, record: Dict[str, Any]) -> bool:
        return self.left.interpret(record) or self.right.interpret(record)


class NotExpression(FilterExpression):
    def __init__(self, expression: FilterExpression) -> None:
        self.expression = expression

    def interpret(self, record: Dict[str, Any]) -> bool:
        return not self.expression.interpret(record)


def filter_records(records: List[Dict[str, Any]], rule: FilterExpression) -> List[Dict[str, Any]]:
    return [r for r in records if rule.interpret(r)]
