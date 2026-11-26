import os
import sys
from pathlib import Path
import importlib.util
import pytest

PATTERN_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, PATTERN_DIR / rel_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


interp_v1 = load_module("interp_v1", "python/v1-basic/interpreter_demo.py")
filter_rule = load_module("filter_rule", "python/v2-variant/boolean_filter_interpreter.py")
script_eval = load_module("script_eval", "python/v3-advanced/script_evaluator.py")


def test_individual_expressions():
    n4 = interp_v1.NumberExpression(4)
    n2 = interp_v1.NumberExpression(2)

    assert n4.interpret() == 4
    assert interp_v1.AddExpression(n4, n2).interpret() == 6
    assert interp_v1.SubtractExpression(n4, n2).interpret() == 2
    assert interp_v1.MultiplyExpression(n4, n2).interpret() == 8


def test_expression_parser_evaluation():
    parser = interp_v1.ExpressionParser()

    assert parser.parse("3 4 +").interpret() == 7
    assert parser.parse("10 5 -").interpret() == 5
    assert parser.parse("6 7 *").interpret() == 42
    assert parser.parse("3 4 + 5 *").interpret() == 35
    assert parser.parse("10 2 3 + *").interpret() == 50


def test_parser_raises_on_invalid_operator():
    parser = interp_v1.ExpressionParser()
    with pytest.raises(ValueError):
        parser.parse("3 4 /")


# --- v2-variant Tests ---

def test_boolean_filter_interpreter():
    records = [
        {"id": 1, "role": "admin", "age": 35, "email": "alice@corp.com"},
        {"id": 2, "role": "developer", "age": 28, "email": "bob@contractor.org"},
        {"id": 3, "role": "admin", "age": 22, "email": "carol@corp.com"},
    ]

    # Rule: role == 'admin' AND age > 30
    rule = filter_rule.AndExpression(
        filter_rule.EqualsExpression("role", "admin"),
        filter_rule.GreaterThanExpression("age", 30)
    )
    res = filter_rule.filter_records(records, rule)
    assert len(res) == 1
    assert res[0]["id"] == 1

    # Rule: email contains '@corp.com' AND NOT (role == 'developer')
    corp_non_dev = filter_rule.AndExpression(
        filter_rule.ContainsExpression("email", "@corp.com"),
        filter_rule.NotExpression(filter_rule.EqualsExpression("role", "developer"))
    )
    assert len(filter_rule.filter_records(records, corp_non_dev)) == 2


# --- v3-advanced Tests ---

def test_script_evaluator_ast_and_memoization():
    ctx = script_eval.ExecutionContext()
    ctx.set_variable("x", 10.0)
    ctx.set_variable("y", 4.0)

    # Formula: max(x * 2, y + 20) -> max(20, 24) = 24.0
    formula = script_eval.FunctionCall("max", [
        script_eval.BinaryOperation(script_eval.VariableReference("x"), "*", script_eval.NumberLiteral(2.0)),
        script_eval.BinaryOperation(script_eval.VariableReference("y"), "+", script_eval.NumberLiteral(20.0))
    ])

    val = formula.evaluate(ctx)
    assert val == 24.0

    # Memoized expression caching test
    memo_expr = script_eval.MemoizedExpression(formula)
    count_before = ctx.evaluation_count
    v1 = memo_expr.evaluate(ctx)
    count_after_first = ctx.evaluation_count
    assert count_after_first > count_before

    v2 = memo_expr.evaluate(ctx)
    assert v1 == 24.0
    assert v2 == 24.0
    # Second evaluation used memo cache, no additional node evaluations
    assert ctx.evaluation_count == count_after_first

    # Division by zero
    div_zero = script_eval.BinaryOperation(script_eval.NumberLiteral(10.0), "/", script_eval.NumberLiteral(0.0))
    with pytest.raises(ZeroDivisionError):
        div_zero.evaluate(ctx)
