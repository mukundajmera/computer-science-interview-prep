"""
Domain-specific metric helpers for applied ML evaluation.

This module extends the basic metric strategy set with reusable helpers for:
- Classification metrics (precision, recall, F1)
- Ranking metrics (MRR, NDCG)
- Generation metric hooks (faithfulness/relevance adapters)

The helpers are pure and deterministic to keep tests lightweight.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from math import log2
from typing import Iterable, List, Sequence


class ClassificationMetrics:
    """Classification metric helpers for binary labels.

    Labels are interpreted as:
    - 1: positive
    - 0: negative
    """

    @staticmethod
    def precision(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
        denom = tp + fp
        return tp / denom if denom > 0 else 0.0

    @staticmethod
    def recall(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
        denom = tp + fn
        return tp / denom if denom > 0 else 0.0

    @staticmethod
    def f1(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
        p = ClassificationMetrics.precision(y_true, y_pred)
        r = ClassificationMetrics.recall(y_true, y_pred)
        denom = p + r
        return 2 * p * r / denom if denom > 0 else 0.0


class RankingMetrics:
    """Ranking metric helpers for recommendation/search evaluation."""

    @staticmethod
    def mrr(relevance_rows: Sequence[Sequence[int]]) -> float:
        """Compute Mean Reciprocal Rank.

        Each row is a ranked list where 1 marks relevant, 0 non-relevant.
        """
        if not relevance_rows:
            return 0.0
        reciprocal_sum = 0.0
        for row in relevance_rows:
            rr = 0.0
            for idx, rel in enumerate(row, start=1):
                if rel > 0:
                    rr = 1.0 / idx
                    break
            reciprocal_sum += rr
        return reciprocal_sum / len(relevance_rows)

    @staticmethod
    def ndcg(relevances: Sequence[int], k: int | None = None) -> float:
        """Compute NDCG for a single ranked list.

        Relevances may be graded (0,1,2,...).
        """
        if not relevances:
            return 0.0
        if k is None:
            k = len(relevances)
        k = max(0, min(k, len(relevances)))
        if k == 0:
            return 0.0

        def dcg(vals: Sequence[int]) -> float:
            return sum((2**rel - 1) / log2(idx + 1) for idx, rel in enumerate(vals, start=1))

        actual = list(relevances[:k])
        ideal = sorted(relevances, reverse=True)[:k]
        idcg = dcg(ideal)
        if idcg == 0:
            return 0.0
        return dcg(actual) / idcg


class GenerationMetrics(ABC):
    """Interface hooks for generation-specific scoring adapters.

    Implementers can wire external faithfulness/relevance evaluators while
    keeping evaluation runner APIs unchanged.
    """

    @abstractmethod
    def faithfulness(self, answer: str, context: str) -> float:
        """Return faithfulness score in [0, 1]."""

    @abstractmethod
    def relevance(self, query: str, answer: str) -> float:
        """Return relevance score in [0, 1]."""


class HeuristicGenerationMetrics(GenerationMetrics):
    """Simple deterministic baseline generation metrics.

    This implementation is intentionally lightweight for local testing and
    demonstration. It should be replaced with stronger judge/eval adapters
    in production.
    """

    def faithfulness(self, answer: str, context: str) -> float:
        answer_tokens = set(answer.lower().split())
        context_tokens = set(context.lower().split())
        if not answer_tokens:
            return 0.0
        overlap = answer_tokens & context_tokens
        return len(overlap) / len(answer_tokens)

    def relevance(self, query: str, answer: str) -> float:
        query_tokens = set(query.lower().split())
        answer_tokens = set(answer.lower().split())
        if not query_tokens:
            return 0.0
        overlap = query_tokens & answer_tokens
        return len(overlap) / len(query_tokens)
