"""v3-advanced: Extensible Math & DSL Script AST Interpreter.

Evaluates mathematical and formula expressions with dynamic variable scopes,
pluggable functions (min, max, abs), operator precedence/binary operations,
and context memoization for repeated evaluations.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
import math


class ExecutionContext:
    def __init__(self) -> None:
        self._variables: Dict[str, float] = {}
        self._functions: Dict[str, Callable[[List[float]], float]] = {}
        self._memo_cache: Dict[str, float] = {}
        self.evaluation_count: int = 0
        self._register_default_functions()

    def _register_default_functions(self) -> None:
        self._functions["abs"] = lambda args: abs(args[0]) if args else 0.0
        self._functions["max"] = lambda args: max(args) if args else 0.0
        self._functions["min"] = lambda args: min(args) if args else 0.0

    def set_variable(self, name: str, value: float) -> None:
        self._variables[name] = float(value)
        self._memo_cache.clear()

    def get_variable(self, name: str) -> float:
        if name not in self._variables:
            raise ValueError(f"Undefined variable: {name}")
        return self._variables[name]

    def register_function(self, name: str, func: Callable[[List[float]], float]) -> None:
        self._functions[name] = func

    def get_function(self, name: str) -> Callable[[List[float]], float]:
        if name not in self._functions:
            raise ValueError(f"Unknown function: {name}")
        return self._functions[name]

    def increment_eval_count(self) -> None:
        self.evaluation_count += 1

    @property
    def memo_cache(self) -> Dict[str, float]:
        return self._memo_cache


class ScriptExpression(ABC):
    @abstractmethod
    def evaluate(self, context: ExecutionContext) -> float:
        pass

    @abstractmethod
    def to_formula_string(self) -> str:
        pass


class NumberLiteral(ScriptExpression):
    def __init__(self, value: float) -> None:
        self.value = float(value)

    def evaluate(self, context: ExecutionContext) -> float:
        context.increment_eval_count()
        return self.value

    def to_formula_string(self) -> str:
        return str(self.value)


class VariableReference(ScriptExpression):
    def __init__(self, name: str) -> None:
        self.name = name

    def evaluate(self, context: ExecutionContext) -> float:
        context.increment_eval_count()
        return context.get_variable(self.name)

    def to_formula_string(self) -> str:
        return self.name


class BinaryOperation(ScriptExpression):
    def __init__(self, left: ScriptExpression, operator: str, right: ScriptExpression) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def evaluate(self, context: ExecutionContext) -> float:
        context.increment_eval_count()
        l = self.left.evaluate(context)
        r = self.right.evaluate(context)

        if self.operator == "+":
            return l + r
        elif self.operator == "-":
            return l - r
        elif self.operator == "*":
            return l * r
        elif self.operator == "/":
            if r == 0.0:
                raise ZeroDivisionError("Division by zero")
            return l / r
        elif self.operator == "^":
            return math.pow(l, r)
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

    def to_formula_string(self) -> str:
        return f"({self.left.to_formula_string()} {self.operator} {self.right.to_formula_string()})"


class FunctionCall(ScriptExpression):
    def __init__(self, function_name: str, arguments: List[ScriptExpression]) -> None:
        self.function_name = function_name
        self.arguments = list(arguments)

    def evaluate(self, context: ExecutionContext) -> float:
        context.increment_eval_count()
        func = context.get_function(self.function_name)
        evaluated_args = [arg.evaluate(context) for arg in self.arguments]
        return func(evaluated_args)

    def to_formula_string(self) -> str:
        args_str = ", ".join(arg.to_formula_string() for arg in self.arguments)
        return f"{self.function_name}({args_str})"


class MemoizedExpression(ScriptExpression):
    def __init__(self, inner: ScriptExpression) -> None:
        self.inner = inner
        self.cache_key = inner.to_formula_string()

    def evaluate(self, context: ExecutionContext) -> float:
        if self.cache_key in context.memo_cache:
            return context.memo_cache[self.cache_key]
        val = self.inner.evaluate(context)
        context.memo_cache[self.cache_key] = val
        return val

    def to_formula_string(self) -> str:
        return self.inner.to_formula_string()
