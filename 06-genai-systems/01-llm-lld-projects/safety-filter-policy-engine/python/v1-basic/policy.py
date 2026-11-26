"""
Policy module — data classes for content moderation rules and decisions.

Defines Action/Severity enums, Rule, Policy, PolicySet, RuleViolation,
and ModerationResult used throughout the safety filter engine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional


class Action(IntEnum):
    """Moderation action ordered by strictness (higher = stricter)."""

    ALLOW = 0
    FLAG = 1
    BLOCK = 2


class Severity(IntEnum):
    """Rule severity ordered by importance (higher = more severe)."""

    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Rule:
    """A single pattern-action pair for content matching.

    Attributes:
        name: Unique identifier for the rule.
        pattern: Regex pattern string to match against content.
        action: Moderation action when the pattern matches.
        severity: How serious a match is.
        description: Human-readable explanation of what the rule detects.
    """

    name: str
    pattern: str
    action: Action
    severity: Severity
    description: str = ""

    def compile(self) -> re.Pattern:
        """Return a compiled regex pattern with case-insensitive matching."""
        return re.compile(self.pattern, re.IGNORECASE)


@dataclass
class Policy:
    """Named collection of rules with a default severity.

    Attributes:
        name: Policy identifier (e.g. 'profanity-filter').
        description: What the policy covers.
        rules: Ordered list of rules belonging to this policy.
        default_severity: Fallback severity when rules don't specify one.
    """

    name: str
    description: str
    rules: List[Rule] = field(default_factory=list)
    default_severity: Severity = Severity.MEDIUM

    def add_rule(self, rule: Rule) -> None:
        """Append a rule to this policy."""
        self.rules.append(rule)


class PolicySet:
    """Groups multiple policies for a specific use case.

    Attributes:
        name: Set identifier (e.g. 'medical-strict').
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._policies: Dict[str, Policy] = {}

    def add_policy(self, policy: Policy) -> None:
        """Register a policy in this set."""
        self._policies[policy.name] = policy

    def get_policy(self, name: str) -> Optional[Policy]:
        """Retrieve a policy by name, or None if not found."""
        return self._policies.get(name)

    def list_policies(self) -> List[str]:
        """Return all policy names in this set."""
        return list(self._policies.keys())

    def __len__(self) -> int:
        return len(self._policies)


@dataclass
class RuleViolation:
    """Records a single rule match with details.

    Attributes:
        filter_name: Which content filter detected the violation.
        rule_name: Which rule matched.
        action: Recommended moderation action.
        severity: Violation severity level.
        matched_text: The text fragment that matched the pattern.
        explanation: Human-readable description of the violation.
    """

    filter_name: str
    rule_name: str
    action: Action
    severity: Severity
    matched_text: str
    explanation: str


@dataclass
class ModerationResult:
    """Aggregate moderation decision with per-filter breakdown.

    Attributes:
        overall_action: Final decision (strictest of all violations).
        violations: All detected violations across all filters.
        explanation: Summary of the decision.
        input_text: Original text that was evaluated.
    """

    overall_action: Action
    violations: List[RuleViolation]
    explanation: str
    input_text: str

    @property
    def is_clean(self) -> bool:
        """Return True if no violations were found."""
        return len(self.violations) == 0

    @property
    def max_severity(self) -> Optional[Severity]:
        """Return the highest severity among violations, or None if clean."""
        if not self.violations:
            return None
        return max(v.severity for v in self.violations)
