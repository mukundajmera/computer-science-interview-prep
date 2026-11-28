"""
Context Window Manager - v2-extended.

A deliberate step up from ``v1-basic/context_manager.py``. It keeps the v1
public API names (``ContextWindowManager``, ``Priority``, ``TokenizerInterface``,
``FallbackTokenizer``, ``ContextSegment``, ``ContextOverflowError`` and the
``add_segment`` / ``compile`` / ``cancel`` / ``requires_summarization``
signatures) while addressing weaknesses the project docs already name:

1. **Thread safety.** v1 mutates ``self._segments`` with no locking, so
   concurrent ``add_segment`` / ``compile`` / ``cancel`` calls can interleave
   and produce inconsistent budgets. v2 guards all segment-state operations
   with a reentrant lock (coarse-grained; the trade-off is documented on
   ``ContextWindowManager``). Single-threaded callers can pass
   ``enable_locking=False``.

2. **Dynamic priority scoring** (FOLLOW-UPS.md section 3). v1 hardcodes the
   eviction order HISTORY -> RAG_CONTEXT -> TOOL_DEF. v2 accepts an optional
   ``DynamicScorer`` that assigns each evictable segment a float score per
   turn, so a turn where an older query matters more than unrelated RAG chunks
   can keep it. Mandatory SYSTEM + USER_QUERY protection and the
   ``ContextOverflowError`` boundary are unchanged.

3. **Active summarization hook** (FOLLOW-UPS.md section 2). v1's
   ``requires_summarization()`` trips a flag nobody consumes. v2 adds an
   injectable, provider-independent ``SummarizerInterface`` and
   ``compact_history()``, which replaces overflowing history segments with a
   single dense summary segment so budgets recompute cleanly.

Additionally, constructor and input validation now fail fast on a non-positive
budget, an out-of-range soft-limit ratio, or empty segment text/IDs.

Standard library only. Python 3.8 compatible. No external tokenizer, network,
or provider dependencies; all guarantees unsupported in v1 remain unsupported.
"""

import asyncio
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Priority(Enum):
    """
    Priority levels for context segments.
    Lower numerical values indicate higher priority.
    """
    SYSTEM = 1
    USER_QUERY = 2
    TOOL_DEF = 3
    RAG_CONTEXT = 4
    HISTORY = 5


class TokenizerInterface(ABC):
    """Interface for estimating token counts."""

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimates the number of tokens in the given text."""


class FallbackTokenizer(TokenizerInterface):
    """
    A simple, standard library tokenizer approximation.
    Uses word count * 1.3 as an estimate.
    """

    def estimate_tokens(self, text: str) -> int:
        """
        Time Complexity: O(N) where N is the length of the string.
        Space Complexity: O(N) due to string splitting.
        """
        words = text.split()
        return int(len(words) * 1.3)


class ContextOverflowError(Exception):
    """Raised when mandatory context (Priority 1 and 2) exceeds the total budget."""
    pass


@dataclass
class ContextSegment:
    """Represents a discrete piece of prompt information."""
    id: str
    text: str
    priority: Priority
    token_count: int


@dataclass
class TurnContext:
    """
    Per-turn metadata handed to a DynamicScorer.

    ``turn_index`` is the zero-based conversation turn; ``metadata`` is an
    open string map for caller-specific signals (e.g. "topic": "billing").
    """
    turn_index: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)


class DynamicScorer(ABC):
    """
    Interface for dynamic eviction scoring (FOLLOW-UPS.md code parity).

    Higher scores are kept longer; the lowest-scored evictable segment is
    evicted first. Scores apply only to evictable priorities (TOOL_DEF,
    RAG_CONTEXT, HISTORY); SYSTEM and USER_QUERY remain mandatory.
    """

    @abstractmethod
    def calculate_score(self, segment: ContextSegment, context: TurnContext) -> float:
        """Returns the keep-score for a segment in the current turn."""


class SummarizerInterface(ABC):
    """
    Provider-independent summarization hook (FOLLOW-UPS.md code parity).

    Implementations may call an external LLM in production; tests inject a
    deterministic fake. The interface is synchronous by design: queueing and
    async execution belong to the caller's side-car, per FOLLOW-UPS.md.
    """

    @abstractmethod
    def summarize(self, texts: List[str]) -> str:
        """Compresses the given history texts (oldest first) into one summary."""


class _NullLock:
    """A no-op context manager used when locking is disabled."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False


class ContextWindowManager:
    """
    Manages prompt context within a token budget via priorities, optional
    dynamic scoring, and attention-aware reordering.

    v2 concurrency contract: one coarse reentrant lock serializes all
    segment-state operations, favoring correctness over throughput; a
    production variant would shard per conversation. Operates as a single
    microcomponent with model/provider-independent interfaces. Explicitly
    unsupported guarantees (as in v1): production safety, real tokenization,
    and embeddings.
    """

    EVICTABLE_PRIORITIES = (Priority.HISTORY, Priority.RAG_CONTEXT, Priority.TOOL_DEF)

    def __init__(self, total_budget: int, soft_limit_ratio: float = 0.8,
                 tokenizer: TokenizerInterface = None,
                 scorer: DynamicScorer = None,
                 summarizer: SummarizerInterface = None,
                 enable_locking: bool = True) -> None:
        """
        Initializes the manager.

        Raises:
            ValueError: If total_budget < 1 or soft_limit_ratio is not in
                the open interval (0.0, 1.0).
        """
        if total_budget < 1:
            raise ValueError("total_budget must be at least 1")
        if not 0.0 < soft_limit_ratio < 1.0:
            raise ValueError("soft_limit_ratio must be in (0.0, 1.0)")
        self._total_budget: int = total_budget
        self._soft_limit_ratio: float = soft_limit_ratio
        self._tokenizer: TokenizerInterface = tokenizer if tokenizer is not None else FallbackTokenizer()
        self._scorer: Optional[DynamicScorer] = scorer
        self._summarizer: Optional[SummarizerInterface] = summarizer
        self._segments: List[ContextSegment] = []
        self._is_cancelled: bool = False
        self._lock = threading.RLock() if enable_locking else _NullLock()

    def cancel(self) -> None:
        """Cancels the context assembly process."""
        with self._lock:
            self._is_cancelled = True

    def add_segment(self, text: str, priority: Priority, id: str) -> None:
        """
        Registers a new block of text with a specific priority level.

        Time Complexity: O(T) where T is the time taken by the tokenizer.
        Space Complexity: O(1) beyond the stored segment.

        Raises:
            ValueError: If text or id is empty.
        """
        if not text:
            raise ValueError("Segment text cannot be empty")
        if not id:
            raise ValueError("Segment id cannot be empty")
        estimated_tokens = self._tokenizer.estimate_tokens(text)
        new_segment = ContextSegment(id=id, text=text, priority=priority,
                                     token_count=estimated_tokens)
        with self._lock:
            self._segments.append(new_segment)

    def requires_summarization(self) -> bool:
        """
        Checks if HISTORY segments consume more than the soft_limit_ratio of
        the total budget.

        Time Complexity: O(N) where N is the number of segments.
        Space Complexity: O(1).
        """
        with self._lock:
            history_token_sum = sum(seg.token_count for seg in self._segments
                                    if seg.priority == Priority.HISTORY)
            threshold = self._total_budget * self._soft_limit_ratio
            return history_token_sum > threshold

    def compact_history(self) -> bool:
        """
        Replaces all HISTORY segments with one summary segment when the soft
        limit is exceeded (FOLLOW-UPS.md section 2).

        Returns:
            True if compaction happened, False if history is under the soft
            limit.

        Raises:
            RuntimeError: If no SummarizerInterface was configured.
            ValueError: If the summarizer returns an empty summary.
            asyncio.CancelledError: If the manager was cancelled.
        """
        with self._lock:
            if self._is_cancelled:
                raise asyncio.CancelledError("Context assembly cancelled")
            if not self.requires_summarization():
                return False
            if self._summarizer is None:
                raise RuntimeError(
                    "compact_history requires a SummarizerInterface; "
                    "configure one at construction time"
                )
            history_segments = [seg for seg in self._segments
                                if seg.priority == Priority.HISTORY]
            summary_text = self._summarizer.summarize(
                [seg.text for seg in history_segments]
            )
            if not summary_text:
                raise ValueError("Summarizer returned an empty summary")
            summary_tokens = self._tokenizer.estimate_tokens(summary_text)
            summary_segment = ContextSegment(
                id="history-summary", text=summary_text,
                priority=Priority.HISTORY, token_count=summary_tokens,
            )
            self._segments = [seg for seg in self._segments
                              if seg.priority != Priority.HISTORY]
            self._segments.append(summary_segment)
            return True

    def _evict_to_fit(self, turn_context: TurnContext) -> List[ContextSegment]:
        """
        Evicts segments until the total fits the budget.

        Without a scorer, keeps the v1 order: HISTORY, then RAG_CONTEXT, then
        TOOL_DEF, oldest first within each priority. With a scorer, evicts the
        lowest-scored evictable segment first; ties break toward the lower
        importance (higher priority value), then older insertion order, so the
        result is fully deterministic.

        Raises ContextOverflowError if mandatory segments (Priority 1 & 2)
        alone exceed budget.

        Time Complexity: O(N log N) with a scorer, O(N) without.
        Space Complexity: O(N).
        """
        if self._is_cancelled:
            raise asyncio.CancelledError("Context assembly cancelled")

        segments = list(self._segments)
        current_total_tokens = sum(seg.token_count for seg in segments)

        if current_total_tokens <= self._total_budget:
            return segments

        mandatory_tokens = sum(seg.token_count for seg in segments
                               if seg.priority in (Priority.SYSTEM, Priority.USER_QUERY))
        if mandatory_tokens > self._total_budget:
            raise ContextOverflowError(
                "Mandatory context (System + User Query) exceeds total token budget."
            )

        indexed = list(enumerate(segments))
        if self._scorer is not None:
            scored = []
            for index, seg in indexed:
                if seg.priority in self.EVICTABLE_PRIORITIES:
                    score = self._scorer.calculate_score(seg, turn_context)
                    # Evict lowest score first; tie-break to lower importance,
                    # then older insertion order, for full determinism.
                    scored.append((score, -seg.priority.value, index, seg))
            scored.sort(key=lambda item: (item[0], item[1], item[2]))
            eviction_sequence = [seg for _, _, _, seg in scored]
        else:
            eviction_sequence = []
            for priority in self.EVICTABLE_PRIORITIES:
                for _, seg in indexed:
                    if seg.priority is priority:
                        eviction_sequence.append(seg)

        evicted_ids = set()
        remaining_tokens = current_total_tokens
        for seg in eviction_sequence:
            if remaining_tokens <= self._total_budget:
                break
            evicted_ids.add(id(seg))
            remaining_tokens -= seg.token_count

        return [seg for seg in segments if id(seg) not in evicted_ids]

    def _reorder_for_attention(self, remaining: List[ContextSegment]) -> List[ContextSegment]:
        """
        Ensures Priority.SYSTEM is at index 0 and Priority.USER_QUERY at -1.

        Time Complexity: O(N) where N is the number of remaining segments.
        Space Complexity: O(N) for the newly ordered list.
        """
        if not remaining:
            return []

        sys_segs = [s for s in remaining if s.priority == Priority.SYSTEM]
        query_segs = [s for s in remaining if s.priority == Priority.USER_QUERY]
        mid_segs = [s for s in remaining
                    if s.priority not in (Priority.SYSTEM, Priority.USER_QUERY)]

        ordered_list = []
        ordered_list.extend(sys_segs)
        ordered_list.extend(mid_segs)
        ordered_list.extend(query_segs)

        return ordered_list

    def compile(self, turn_context: TurnContext = None) -> List[str]:
        """
        Executes eviction, reordering, and returns a finalized list of strings.

        Time Complexity: O(N log N) with a scorer, otherwise O(N).
        Space Complexity: O(N) for returning the string list.

        Raises:
            asyncio.CancelledError: If the manager was cancelled.
            ContextOverflowError: If mandatory segments exceed the budget.
        """
        if turn_context is None:
            turn_context = TurnContext()
        with self._lock:
            if self._is_cancelled:
                raise asyncio.CancelledError("Context assembly cancelled")
            fitted_segments = self._evict_to_fit(turn_context)
            attention_ordered = self._reorder_for_attention(fitted_segments)
            return [seg.text for seg in attention_ordered]
