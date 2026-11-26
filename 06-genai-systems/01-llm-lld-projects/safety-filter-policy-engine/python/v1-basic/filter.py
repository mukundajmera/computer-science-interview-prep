"""
Filter module — abstract base and concrete content filters.

Provides the ContentFilter ABC and three built-in implementations:
KeywordFilter, PIIFilter, and PromptInjectionFilter.  Each filter
evaluates text and returns a list of RuleViolation objects.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import List, Tuple

from policy import Action, RuleViolation, Severity


class ContentFilter(ABC):
    """Abstract base class for all content filters (Strategy interface).

    Subclasses implement ``check()`` to evaluate text against their
    specific set of rules and return any violations found.
    """

    def __init__(self, name: str) -> None:
        self._name = name

    @abstractmethod
    def check(self, text: str) -> List[RuleViolation]:
        """Evaluate *text* and return a list of violations."""

    def get_name(self) -> str:
        """Return the filter's identifier."""
        return self._name


class KeywordFilter(ContentFilter):
    """Regex-based blocked-word detector.

    Each blocked word is compiled into a word-boundary pattern so that
    partial matches inside larger words are avoided.
    """

    def __init__(self, blocked_words: List[str] | None = None) -> None:
        super().__init__("keyword_filter")
        self._compiled_patterns: List[Tuple[str, re.Pattern]] = []
        for word in (blocked_words or []):
            self.add_blocked_word(word)

    def add_blocked_word(self, word: str) -> None:
        """Add a blocked word (compiled as a word-boundary regex)."""
        pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
        self._compiled_patterns.append((word, pattern))

    def check(self, text: str) -> List[RuleViolation]:
        """Scan *text* for blocked keywords."""
        violations: List[RuleViolation] = []
        for word, pattern in self._compiled_patterns:
            match = pattern.search(text)
            if match:
                violations.append(
                    RuleViolation(
                        filter_name=self._name,
                        rule_name=f"blocked_word_{word}",
                        action=Action.BLOCK,
                        severity=Severity.HIGH,
                        matched_text=match.group(),
                        explanation=f"Blocked keyword detected: '{word}'",
                    )
                )
        return violations


class PIIFilter(ContentFilter):
    """Detects common PII patterns: email addresses, phone numbers, SSNs."""

    _PII_PATTERNS: List[Tuple[str, str, Severity]] = [
        ("email", r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", Severity.HIGH),
        ("phone", r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", Severity.HIGH),
        ("ssn", r"\b\d{3}-\d{2}-\d{4}\b", Severity.CRITICAL),
        ("credit_card", r"\b(?:\d[ -]*?){13,16}\b", Severity.CRITICAL),
    ]

    def __init__(self) -> None:
        super().__init__("pii_filter")
        self._compiled: List[Tuple[str, re.Pattern, Severity]] = [
            (name, re.compile(pattern), sev)
            for name, pattern, sev in self._PII_PATTERNS
        ]

    def check(self, text: str) -> List[RuleViolation]:
        """Detect PII patterns in *text*."""
        violations: List[RuleViolation] = []
        for pii_type, pattern, severity in self._compiled:
            match = pattern.search(text)
            if match:
                violations.append(
                    RuleViolation(
                        filter_name=self._name,
                        rule_name=f"pii_{pii_type}",
                        action=Action.BLOCK,
                        severity=severity,
                        matched_text=match.group(),
                        explanation=f"PII detected: {pii_type}",
                    )
                )
        return violations

    def redact(self, text: str, replacement: str = "[REDACTED]") -> str:
        """Redact detected PII patterns with the replacement string."""
        redacted_text = text
        for _, pattern, _ in self._compiled:
            redacted_text = pattern.sub(replacement, redacted_text)
        return redacted_text


class PromptInjectionFilter(ContentFilter):
    """Detects common prompt-injection phrases.

    Matches patterns such as "ignore previous instructions",
    "disregard above", and "you are now" role-switching attempts.
    """

    _INJECTION_PATTERNS: List[Tuple[str, str]] = [
        ("ignore_instructions", r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)"),
        ("disregard", r"disregard\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions|prompts|context)"),
        ("role_switch", r"you\s+are\s+now\s+(?:a|an|the)\s+\w+"),
        ("system_override", r"system\s*:\s*override"),
        ("jailbreak_attempt", r"(?:do\s+not|don'?t)\s+follow\s+(your|the|any)\s+(rules|guidelines|instructions)"),

        ("override_delimiters", r"(?:<<<|>>>|\[INST\]|</INST>|<SYS>|</SYS>)"),
        ("system_leak_probe", r"(?:repeat|output|show|reveal|print|display).*(?:system prompt|initial instructions|core directives)"),

    ]

    def __init__(self) -> None:
        super().__init__("prompt_injection_filter")
        self._compiled: List[Tuple[str, re.Pattern]] = [
            (name, re.compile(pattern, re.IGNORECASE))
            for name, pattern in self._INJECTION_PATTERNS
        ]

    def check(self, text: str) -> List[RuleViolation]:
        """Detect prompt-injection patterns in *text*."""
        violations: List[RuleViolation] = []
        for inj_name, pattern in self._compiled:
            match = pattern.search(text)
            if match:
                violations.append(
                    RuleViolation(
                        filter_name=self._name,
                        rule_name=f"injection_{inj_name}",
                        action=Action.BLOCK,
                        severity=Severity.CRITICAL,
                        matched_text=match.group(),
                        explanation=f"Prompt injection detected: {inj_name}",
                    )
                )
        return violations


class ToxicityFilter(KeywordFilter):
    """Detects toxic or prohibited topic keywords."""

    _TOXIC_WORDS = [
        "hate", "kill", "murder", "terrorist", "bomb", "suicide", "harm"
    ]

    def __init__(self, blocked_words: List[str] | None = None) -> None:
        words = blocked_words or self._TOXIC_WORDS
        super().__init__(words)
        self._name = "toxicity_filter"
        
    def check(self, text: str) -> List[RuleViolation]:
        """Scan text for toxic keywords."""
        violations = super().check(text)
        for v in violations:
            v.rule_name = f"toxic_word_{v.matched_text}"
            v.explanation = f"Toxic keyword detected: '{v.matched_text}'"
        return violations
