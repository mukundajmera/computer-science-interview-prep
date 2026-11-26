"""
Engine module — orchestrates filter evaluation and audit logging.

PolicyEngine registers content filters, evaluates text through the
filter chain, aggregates violations, and logs every decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from filter import ContentFilter
from policy import Action, ModerationResult, RuleViolation, Severity


@dataclass
class AuditEntry:
    """A single audit log record for a moderation decision.

    Attributes:
        timestamp: ISO-format UTC timestamp of the evaluation.
        input_text: The text that was evaluated.
        action: Final moderation action taken.
        violations: All violations detected during evaluation.
        explanation: Human-readable summary of the decision.
    """

    timestamp: str
    input_text: str
    action: Action
    violations: List[RuleViolation]
    explanation: str


class AuditLogger:
    """In-memory audit log for moderation decisions."""

    def __init__(self) -> None:
        self._entries: List[AuditEntry] = []

    def log(self, entry: AuditEntry) -> None:
        """Append an audit entry."""
        self._entries.append(entry)

    def get_entries(self) -> List[AuditEntry]:
        """Return all audit entries."""
        return list(self._entries)

    def get_entries_by_action(self, action: Action) -> List[AuditEntry]:
        """Return entries filtered by moderation action."""
        return [e for e in self._entries if e.action == action]

    def clear(self) -> None:
        """Remove all entries from the log."""
        self._entries.clear()

    def size(self) -> int:
        """Return the number of entries in the log."""
        return len(self._entries)


class PolicyEngine:
    """Orchestrates content filter evaluation and produces moderation results.

    Filters are evaluated in registration order.  All violations are
    collected and the strictest action determines the overall decision.
    Every evaluation is recorded in the audit log.
    """

    def __init__(self) -> None:
        self._filters: List[ContentFilter] = []
        self._audit_logger = AuditLogger()

    # -- Filter management ---------------------------------------------------

    def add_filter(self, content_filter: ContentFilter) -> None:
        """Register a content filter at the end of the evaluation chain."""
        self._filters.append(content_filter)

    def remove_filter(self, name: str) -> bool:
        """Remove a filter by name. Returns True if found and removed."""
        for i, f in enumerate(self._filters):
            if f.get_name() == name:
                self._filters.pop(i)
                return True
        return False

    def get_filters(self) -> List[str]:
        """Return the names of all registered filters in order."""
        return [f.get_name() for f in self._filters]

    # -- Evaluation ----------------------------------------------------------

    def evaluate(self, text: str) -> ModerationResult:
        """Run *text* through all registered filters and return a result.

        The overall action is the strictest action among all violations.
        If no violations are found the result action is ALLOW.
        """
        all_violations: List[RuleViolation] = []

        for content_filter in self._filters:
            violations = content_filter.check(text)
            all_violations.extend(violations)

        if all_violations:
            overall_action = max(v.action for v in all_violations)
            explanations = sorted(
                {v.explanation for v in all_violations}
            )
            explanation = "; ".join(explanations)
        else:
            overall_action = Action.ALLOW
            explanation = "No violations found"

        result = ModerationResult(
            overall_action=overall_action,
            violations=all_violations,
            explanation=explanation,
            input_text=text,
        )

        # Record in audit log
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            input_text=text,
            action=overall_action,
            violations=all_violations,
            explanation=explanation,
        )
        self._audit_logger.log(entry)

        return result

    # -- Audit ---------------------------------------------------------------

    def get_audit_log(self) -> List[AuditEntry]:
        """Return all audit log entries."""
        return self._audit_logger.get_entries()

    def get_audit_logger(self) -> AuditLogger:
        """Return the underlying audit logger instance."""
        return self._audit_logger
