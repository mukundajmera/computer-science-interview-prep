import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

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
    """
    Interface for estimating token counts.
    """
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """
        Estimates the number of tokens in the given text.
        """
        pass

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

class ContextWindowManager:
    """
    Manages prompt context, ensuring it fits within a token budget by prioritizing
    and reordering segments to maximize model attention.
    Operates as a single microcomponent with model/provider-independent interfaces.
    There are no external provider calls or sensitive prompt logs. Explicitly 
    unsupported guarantees: production safety, real tokenization, and embeddings.
    """
    def __init__(self, total_budget: int, soft_limit_ratio: float = 0.8, tokenizer: TokenizerInterface = None):
        self._total_budget: int = total_budget
        self._soft_limit_ratio: float = soft_limit_ratio
        self._tokenizer: TokenizerInterface = tokenizer if tokenizer is not None else FallbackTokenizer()
        self._segments: List[ContextSegment] = []
        self._is_cancelled: bool = False

    def cancel(self) -> None:
        """Cancels the context assembly process."""
        self._is_cancelled = True

    def add_segment(self, text: str, priority: Priority, id: str) -> None:
        """
        Registers a new block of text with a specific priority level.
        
        Time Complexity: O(T) where T is the time taken by the tokenizer.
        Space Complexity: O(1) beyond the stored segment.
        """
        estimated_tokens = self._tokenizer.estimate_tokens(text)
        new_segment = ContextSegment(id=id, text=text, priority=priority, token_count=estimated_tokens)
        self._segments.append(new_segment)

    def requires_summarization(self) -> bool:
        """
        Checks if HISTORY segments consume more than the soft_limit_ratio of the total budget.
        
        Time Complexity: O(N) where N is the number of segments.
        Space Complexity: O(1).
        """
        history_token_sum = sum(seg.token_count for seg in self._segments if seg.priority == Priority.HISTORY)
        threshold = self._total_budget * self._soft_limit_ratio
        return history_token_sum > threshold

    def _evict_to_fit(self) -> List[ContextSegment]:
        """
        Evicts lowest priority segments until the total token count is within budget.
        Raises ContextOverflowError if mandatory segments (Priority 1 & 2) alone exceed budget.
        
        Time Complexity: O(N) where N is the number of segments, using list manipulations.
        Space Complexity: O(N) to group and store surviving segments.
        """
        if self._is_cancelled:
            raise asyncio.CancelledError("Context assembly cancelled")
            
        current_total_tokens = sum(seg.token_count for seg in self._segments)
        
        if current_total_tokens <= self._total_budget:
            return list(self._segments)
            
        grouped_segments: Dict[Priority, List[ContextSegment]] = {p: [] for p in Priority}
        for seg in self._segments:
            grouped_segments[seg.priority].append(seg)
            
        system_tokens = sum(seg.token_count for seg in grouped_segments[Priority.SYSTEM])
        query_tokens = sum(seg.token_count for seg in grouped_segments[Priority.USER_QUERY])
        mandatory_total = system_tokens + query_tokens
        
        if mandatory_total > self._total_budget:
            raise ContextOverflowError("Mandatory context (System + User Query) exceeds total token budget.")

        remaining_tokens = current_total_tokens
        
        eviction_order = [Priority.HISTORY, Priority.RAG_CONTEXT, Priority.TOOL_DEF]
        for p in eviction_order:
            priority_list = grouped_segments[p]
            while priority_list and remaining_tokens > self._total_budget:
                evicted_seg = priority_list.pop(0)
                remaining_tokens -= evicted_seg.token_count
                
        surviving_segments = []
        for seg in self._segments:
            if seg in grouped_segments[seg.priority]:
                surviving_segments.append(seg)
                 
        return surviving_segments

    def _reorder_for_attention(self, remaining: List[ContextSegment]) -> List[ContextSegment]:
        """
        Ensures Priority.SYSTEM is at index 0 and Priority.USER_QUERY is at index -1.
        
        Time Complexity: O(N) where N is the number of remaining segments.
        Space Complexity: O(N) for the newly ordered list.
        """
        if not remaining:
            return []
            
        sys_segs = [s for s in remaining if s.priority == Priority.SYSTEM]
        query_segs = [s for s in remaining if s.priority == Priority.USER_QUERY]
        mid_segs = [s for s in remaining if s.priority not in (Priority.SYSTEM, Priority.USER_QUERY)]
        
        ordered_list = []
        ordered_list.extend(sys_segs)
        ordered_list.extend(mid_segs)
        ordered_list.extend(query_segs)
        
        return ordered_list

    def compile(self) -> List[str]:
        """
        Executes eviction, reordering, and returns a finalized list of strings.
        
        Time Complexity: O(N) dominated by eviction and reordering.
        Space Complexity: O(N) for returning the string list.
        """
        if self._is_cancelled:
            raise asyncio.CancelledError("Context assembly cancelled")
            
        fitted_segments = self._evict_to_fit()
        attention_ordered = self._reorder_for_attention(fitted_segments)
        return [seg.text for seg in attention_ordered]
