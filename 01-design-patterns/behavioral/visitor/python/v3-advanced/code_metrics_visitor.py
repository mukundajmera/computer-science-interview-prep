"""v3-advanced: AST Static Analysis and Code Metrics Visitor.

Traverses an Abstract Syntax Tree (FunctionDef, IfStatement, LoopStatement, Assignment, CallExpression)
to compute cyclomatic complexity, statement metrics, and security audit violations.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Set


class AstVisitor(ABC):
    @abstractmethod
    def visit_function_def(self, node: "FunctionDef") -> None:
        pass

    @abstractmethod
    def visit_if_statement(self, node: "IfStatement") -> None:
        pass

    @abstractmethod
    def visit_loop_statement(self, node: "LoopStatement") -> None:
        pass

    @abstractmethod
    def visit_assignment(self, node: "Assignment") -> None:
        pass

    @abstractmethod
    def visit_call_expression(self, node: "CallExpression") -> None:
        pass


class AstNode(ABC):
    @abstractmethod
    def accept(self, visitor: AstVisitor) -> None:
        pass


class FunctionDef(AstNode):
    def __init__(self, name: str, parameters: Optional[List[str]] = None, body: Optional[List[AstNode]] = None) -> None:
        self.name = name
        self.parameters = list(parameters) if parameters else []
        self.body = list(body) if body else []

    def accept(self, visitor: AstVisitor) -> None:
        visitor.visit_function_def(self)
        for stmt in self.body:
            stmt.accept(visitor)


class IfStatement(AstNode):
    def __init__(self, condition: str, then_branch: Optional[List[AstNode]] = None, else_branch: Optional[List[AstNode]] = None) -> None:
        self.condition = condition
        self.then_branch = list(then_branch) if then_branch else []
        self.else_branch = list(else_branch) if else_branch else []

    def accept(self, visitor: AstVisitor) -> None:
        visitor.visit_if_statement(self)
        for stmt in self.then_branch:
            stmt.accept(visitor)
        for stmt in self.else_branch:
            stmt.accept(visitor)


class LoopStatement(AstNode):
    def __init__(self, loop_type: str, body: Optional[List[AstNode]] = None) -> None:
        self.loop_type = loop_type
        self.body = list(body) if body else []

    def accept(self, visitor: AstVisitor) -> None:
        visitor.visit_loop_statement(self)
        for stmt in self.body:
            stmt.accept(visitor)


class Assignment(AstNode):
    def __init__(self, variable: str, expression: str) -> None:
        self.variable = variable
        self.expression = expression

    def accept(self, visitor: AstVisitor) -> None:
        visitor.visit_assignment(self)


class CallExpression(AstNode):
    def __init__(self, callee: str, arguments: Optional[List[str]] = None) -> None:
        self.callee = callee
        self.arguments = list(arguments) if arguments else []

    def accept(self, visitor: AstVisitor) -> None:
        visitor.visit_call_expression(self)


class MetricsVisitor(AstVisitor):
    def __init__(self) -> None:
        self.function_count: int = 0
        self.statement_count: int = 0
        self.cyclomatic_complexity: int = 0

    def visit_function_def(self, node: FunctionDef) -> None:
        self.function_count += 1
        self.cyclomatic_complexity += 1

    def visit_if_statement(self, node: IfStatement) -> None:
        self.statement_count += 1
        self.cyclomatic_complexity += 1

    def visit_loop_statement(self, node: LoopStatement) -> None:
        self.statement_count += 1
        self.cyclomatic_complexity += 1

    def visit_assignment(self, node: Assignment) -> None:
        self.statement_count += 1

    def visit_call_expression(self, node: CallExpression) -> None:
        self.statement_count += 1


class SecurityAuditVisitor(AstVisitor):
    DANGEROUS_CALLS: Set[str] = {"eval", "exec", "system", "popen"}

    def __init__(self) -> None:
        self.security_alerts: List[str] = []

    def visit_function_def(self, node: FunctionDef) -> None:
        pass

    def visit_if_statement(self, node: IfStatement) -> None:
        pass

    def visit_loop_statement(self, node: LoopStatement) -> None:
        pass

    def visit_assignment(self, node: Assignment) -> None:
        pass

    def visit_call_expression(self, node: CallExpression) -> None:
        if node.callee in self.DANGEROUS_CALLS:
            self.security_alerts.append(f"CRITICAL: Insecure call to '{node.callee}' with args {node.arguments}")
