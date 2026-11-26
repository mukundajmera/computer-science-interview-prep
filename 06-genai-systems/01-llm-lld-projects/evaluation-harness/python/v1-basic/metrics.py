"""
Evaluation metrics module.

Provides a Strategy-based framework for scoring LLM outputs against
expected answers.  Five built-in metrics are included: exact match,
n-gram overlap, keyword presence, length compliance, and custom scorer.

Design patterns:
    - Strategy — interchangeable scoring algorithms behind a uniform interface
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from typing import Callable, List


class Metric(ABC):
    """Abstract base class for evaluation metrics.

    Every metric produces a score in ``[0.0, 1.0]`` where 1.0 indicates
    a perfect match and 0.0 indicates no match.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this metric."""

    @abstractmethod
    def score(self, expected: str, actual: str) -> float:
        """Score the *actual* output against the *expected* answer.

        Args:
            expected: Ground-truth reference text.
            actual:   Model-generated output text.

        Returns:
            A float in ``[0.0, 1.0]``.
        """


class ExactMatchMetric(Metric):
    """Binary metric: 1.0 if expected equals actual, 0.0 otherwise.

    Args:
        case_sensitive: If ``False`` (default), comparison is case-insensitive.

    Complexity: O(n) where n = max(len(expected), len(actual)).
    """

    def __init__(self, case_sensitive: bool = False) -> None:
        self.case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        return "exact_match"

    def score(self, expected: str, actual: str) -> float:
        """Return 1.0 on exact match, 0.0 otherwise."""
        if self.case_sensitive:
            return 1.0 if expected == actual else 0.0
        return 1.0 if expected.lower() == actual.lower() else 0.0


class NGramOverlapMetric(Metric):
    """N-gram precision between expected and actual outputs.

    Computes the fraction of expected n-grams that appear in the actual
    output.  Tokenisation is whitespace-based and lowercased.

    Args:
        n: N-gram size (default ``1``, i.e. unigrams).

    Complexity: O(t) where t = number of tokens.
    """

    def __init__(self, n: int = 1) -> None:
        if n < 1:
            raise ValueError("n must be >= 1")
        self.n = n

    @property
    def name(self) -> str:
        return f"{self.n}gram_overlap"

    def score(self, expected: str, actual: str) -> float:
        """Return precision of expected n-grams found in actual."""
        expected_ngrams = self._ngrams(expected, self.n)
        if not expected_ngrams:
            return 1.0  # vacuously true
        actual_ngrams = self._ngrams(actual, self.n)
        overlap = expected_ngrams & actual_ngrams
        return sum(overlap.values()) / sum(expected_ngrams.values())

    @staticmethod
    def _ngrams(text: str, n: int) -> Counter:
        """Extract n-gram counts from whitespace-tokenised, lowercased text."""
        tokens = text.lower().split()
        if len(tokens) < n:
            return Counter()
        return Counter(
            tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)
        )


class KeywordPresenceMetric(Metric):
    """Fraction of required keywords found in the actual output.

    Matching is case-insensitive substring search.

    Args:
        keywords: List of keywords to look for.

    Complexity: O(k · m) where k = number of keywords, m = len(actual).
    """

    def __init__(self, keywords: List[str]) -> None:
        self.keywords = keywords

    @property
    def name(self) -> str:
        return "keyword_presence"

    def score(self, expected: str, actual: str) -> float:
        """Return fraction of keywords found in *actual*."""
        if not self.keywords:
            return 1.0  # vacuously true
        actual_lower = actual.lower()
        found = sum(1 for kw in self.keywords if kw.lower() in actual_lower)
        return found / len(self.keywords)


class LengthComplianceMetric(Metric):
    """Binary metric: 1.0 if actual output length is within bounds.

    Args:
        min_length: Minimum acceptable character count (default ``0``).
        max_length: Maximum acceptable character count (default ``10000``).

    Raises:
        ValueError: If *min_length* > *max_length* or either is negative.

    Complexity: O(1).
    """

    def __init__(self, min_length: int = 0, max_length: int = 10000) -> None:
        if min_length < 0 or max_length < 0:
            raise ValueError("Length bounds must be non-negative")
        if min_length > max_length:
            raise ValueError("min_length must be <= max_length")
        self.min_length = min_length
        self.max_length = max_length

    @property
    def name(self) -> str:
        return "length_compliance"

    def score(self, expected: str, actual: str) -> float:
        """Return 1.0 if len(actual) is within [min_length, max_length]."""
        length = len(actual)
        return 1.0 if self.min_length <= length <= self.max_length else 0.0


class CustomMetric(Metric):
    """Wraps a user-provided scoring function as a :class:`Metric`.

    The callable must accept ``(expected, actual)`` and return a float.
    The returned value is clamped to ``[0.0, 1.0]``.

    Args:
        name:    Caller-supplied metric name.
        fn:      Scoring function ``(expected: str, actual: str) → float``.

    Complexity: Depends on the caller-supplied function.
    """

    def __init__(self, name: str, fn: Callable[[str, str], float]) -> None:
        self._name = name
        self._fn = fn

    @property
    def name(self) -> str:
        return self._name

    def score(self, expected: str, actual: str) -> float:
        """Delegate to the wrapped function, clamping result to [0.0, 1.0]."""
        raw = self._fn(expected, actual)
        return max(0.0, min(1.0, raw))
