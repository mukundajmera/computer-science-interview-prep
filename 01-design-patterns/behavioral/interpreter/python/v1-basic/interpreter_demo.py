"""
Interpreter Pattern - Math Expression Evaluator
"""
from abc import ABC, abstractmethod
from typing import List


# Abstract Expression
class Expression(ABC):
    @abstractmethod
    def interpret(self) -> int:
        pass


# Terminal Expression
class NumberExpression(Expression):
    def __init__(self, number: int):
        self._number = number
    
    def interpret(self) -> int:
        return self._number


# Non-terminal Expressions
class AddExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right
    
    def interpret(self) -> int:
        return self._left.interpret() + self._right.interpret()


class SubtractExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right
    
    def interpret(self) -> int:
        return self._left.interpret() - self._right.interpret()


class MultiplyExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right
    
    def interpret(self) -> int:
        return self._left.interpret() * self._right.interpret()


# Parser (Client)
class ExpressionParser:
    OPERATORS = {'+', '-', '*'}
    
    def parse(self, expression: str) -> Expression:
        stack: List[Expression] = []
        tokens = expression.split()
        
        for token in tokens:
            if token in self.OPERATORS:
                right = stack.pop()
                left = stack.pop()
                stack.append(self._create_operation(token, left, right))
            else:
                stack.append(NumberExpression(int(token)))
        
        return stack.pop()
    
    def _create_operation(self, op: str, left: Expression, right: Expression) -> Expression:
        if op == '+':
            return AddExpression(left, right)
        elif op == '-':
            return SubtractExpression(left, right)
        elif op == '*':
            return MultiplyExpression(left, right)
        else:
            raise ValueError(f"Unknown operator: {op}")


if __name__ == "__main__":
    parser = ExpressionParser()
    
    # Postfix notation: "3 4 +" means 3 + 4
    expressions = [
        "3 4 +",           # 3 + 4 = 7
        "10 5 -",          # 10 - 5 = 5
        "6 7 *",           # 6 * 7 = 42
        "3 4 + 5 *",       # (3 + 4) * 5 = 35
        "10 2 3 + *"       # 10 * (2 + 3) = 50
    ]
    
    print("=== Expression Interpreter ===")
    for expr in expressions:
        parsed = parser.parse(expr)
        print(f"'{expr}' = {parsed.interpret()}")
