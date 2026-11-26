"""v3-advanced: Priority-Ordered Interceptor Chain with Context and Metrics.

Demonstrates priority-driven filter execution, context sharing, audit trail accumulation,
and early circuit-breaking upon critical policy violations.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional


class FilterResult(Enum):
    PROCEED = "PROCEED"
    BLOCK = "BLOCK"


class SecurityContext:
    def __init__(self, user_id: str, roles: List[str]) -> None:
        self.user_id: str = user_id
        self.roles: List[str] = list(roles)
        self.attributes: Dict[str, Any] = {}
        self.audit_trail: List[str] = []

    def add_audit(self, message: str) -> None:
        self.audit_trail.append(message)


class SecurityFilter(ABC):
    @property
    @abstractmethod
    def order(self) -> int:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def filter(self, context: SecurityContext) -> FilterResult:
        pass


class BlacklistFilter(SecurityFilter):
    _BLOCKED = {"banned_user_1", "bot_99"}

    @property
    def order(self) -> int:
        return 10

    @property
    def name(self) -> str:
        return "BlacklistFilter"

    def filter(self, context: SecurityContext) -> FilterResult:
        if context.user_id in self._BLOCKED:
            context.add_audit("BLOCKED: User is blacklisted")
            return FilterResult.BLOCK
        context.add_audit("PASSED: User not in blacklist")
        return FilterResult.PROCEED


class RoleValidationFilter(SecurityFilter):
    def __init__(self, required_role: str) -> None:
        self._role = required_role

    @property
    def order(self) -> int:
        return 20

    @property
    def name(self) -> str:
        return "RoleValidationFilter"

    def filter(self, context: SecurityContext) -> FilterResult:
        if self._role not in context.roles:
            context.add_audit(f"BLOCKED: Missing required role: {self._role}")
            return FilterResult.BLOCK
        context.add_audit(f"PASSED: Role verified: {self._role}")
        return FilterResult.PROCEED


class SecurityFilterChain:
    def __init__(self) -> None:
        self._filters: List[SecurityFilter] = []

    def add_filter(self, filter_item: SecurityFilter) -> "SecurityFilterChain":
        self._filters.append(filter_item)
        self._filters.sort(key=lambda f: f.order)
        return self

    def execute(self, context: SecurityContext) -> bool:
        for f in self._filters:
            res = f.filter(context)
            if res == FilterResult.BLOCK:
                return False
        return True
