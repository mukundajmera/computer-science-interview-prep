"""
Token-budget management for context-length guarding.

Provides :class:`TokenBudget` which estimates token counts using a
pluggable heuristic (default: ``words × 1.3``), tracks per-section
allocations, and truncates content at word boundaries when the budget
is exceeded.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional


def default_token_estimator(text: str) -> int:
    """Estimate token count with a word-based heuristic.

    Uses ``ceil(word_count × 1.3)`` which is a widely cited approximation
    for English text processed by BPE tokenizers.

    Args:
        text: The text to estimate.

    Returns:
        Estimated number of tokens (always ≥ 0).
    """
    if not text or not text.strip():
        return 0
    return math.ceil(len(text.split()) * 1.3)


@dataclass
class BudgetAllocation:
    """Tracks the token budget for a single prompt section.

    Attributes:
        section_name: Identifier of the section (e.g. ``"system"``).
        max_tokens:   Maximum tokens allowed for this section.
        used_tokens:  Tokens currently consumed by the section's content.
    """

    section_name: str
    max_tokens: int
    used_tokens: int = 0

    def remaining(self) -> int:
        """Return tokens still available in this allocation."""
        return max(0, self.max_tokens - self.used_tokens)


class TokenBudget:
    """Context-length budget tracker with per-section allocations.

    Example::

        budget = TokenBudget(max_tokens=4096)
        budget.allocate("system", 512)
        budget.allocate("context", 2048)
        budget.allocate("user", 1024)

        tokens = budget.estimate_tokens("Hello world")
        fits = budget.fits("system", "You are a helpful assistant.")
        trimmed = budget.truncate_to_fit("very long text ...", max_tokens=100)

    The estimator is pluggable — pass a custom callable to the constructor
    to use a real tokenizer (e.g. tiktoken) instead of the default heuristic.
    """

    def __init__(
        self,
        max_tokens: int,
        *,
        token_estimator: Optional[Callable[[str], int]] = None,
    ) -> None:
        """Initialise a token budget.

        Args:
            max_tokens:      Total context-length ceiling.
            token_estimator: Optional callable ``(str) → int`` that returns
                             an estimated token count. Defaults to
                             :func:`default_token_estimator`.

        Raises:
            ValueError: If *max_tokens* is not positive.
        """
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        self._max_tokens: int = max_tokens
        self._allocations: Dict[str, BudgetAllocation] = {}
        self._token_estimator: Callable[[str], int] = (
            token_estimator or default_token_estimator
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def max_tokens(self) -> int:
        """Total budget ceiling."""
        return self._max_tokens

    def estimate_tokens(self, text: str) -> int:
        """Estimate the token count of *text*.

        Args:
            text: Input text.

        Returns:
            Estimated number of tokens.
        """
        return self._token_estimator(text)

    def allocate(self, section_name: str, max_tokens: int) -> None:
        """Register or update a per-section token budget.

        Args:
            section_name: Section identifier.
            max_tokens:   Maximum tokens for this section.

        Raises:
            ValueError: If *max_tokens* is negative.
        """
        if max_tokens < 0:
            raise ValueError("Section max_tokens must not be negative")
        self._allocations[section_name] = BudgetAllocation(
            section_name=section_name,
            max_tokens=max_tokens,
        )

    def record_usage(self, section_name: str, text: str) -> int:
        """Estimate tokens for *text* and record usage against the section.

        Args:
            section_name: Section whose allocation is charged.
            text:         Content whose tokens are counted.

        Returns:
            The estimated token count.
        """
        tokens = self.estimate_tokens(text)
        if section_name in self._allocations:
            self._allocations[section_name].used_tokens = tokens
        return tokens

    def fits(self, section_name: str, text: str) -> bool:
        """Check whether *text* fits within the section's allocation.

        If the section has no explicit allocation, checks against the
        overall remaining budget.

        Args:
            section_name: Section identifier.
            text:         Content to check.

        Returns:
            ``True`` if the text fits within the budget.
        """
        tokens = self.estimate_tokens(text)
        if section_name in self._allocations:
            return tokens <= self._allocations[section_name].max_tokens
        return tokens <= self.total_remaining()

    def truncate_to_fit(self, text: str, max_tokens: int) -> str:
        """Truncate *text* at word boundaries to fit within *max_tokens*.

        Args:
            text:       The text to truncate.
            max_tokens: Token ceiling for the returned text.

        Returns:
            A truncated copy of *text* whose estimated token count is
            ≤ *max_tokens*.  If *text* already fits, it is returned
            unchanged.
        """
        if self.estimate_tokens(text) <= max_tokens:
            return text
        words = text.split()
        # Binary-search for the longest prefix that fits
        lo, hi = 0, len(words)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            candidate = " ".join(words[:mid])
            if self.estimate_tokens(candidate) <= max_tokens:
                lo = mid
            else:
                hi = mid - 1
        if lo == 0:
            return ""
        return " ".join(words[:lo])

    def total_used(self) -> int:
        """Return the sum of tokens used across all allocations."""
        return sum(a.used_tokens for a in self._allocations.values())

    def total_remaining(self) -> int:
        """Return total budget minus total usage."""
        return max(0, self._max_tokens - self.total_used())

    def get_allocation(self, section_name: str) -> Optional[BudgetAllocation]:
        """Return the allocation for *section_name*, or ``None``."""
        return self._allocations.get(section_name)
