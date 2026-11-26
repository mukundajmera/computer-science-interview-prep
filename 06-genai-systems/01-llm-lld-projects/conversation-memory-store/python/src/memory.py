"""
Memory strategies and conversation store for the conversation memory store.

Implements the Strategy pattern: callers program to the ``MemoryStrategy``
ABC while concrete classes (BufferMemory, WindowMemory, SummaryMemory,
TokenLimitedMemory) decide which messages are surfaced as LLM context.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from message import Conversation, Message, Role
from summarizer import NullSummarizer, Summarizer


class MemoryStrategy(ABC):
    """Abstract base for conversation memory strategies.

    Every strategy stores messages and exposes them through a uniform
    interface.  The ``get_messages`` and ``get_context`` methods apply the
    strategy's policy to decide which subset of history is returned.
    """

    @abstractmethod
    def add_message(self, message: Message) -> None:
        """Append a message to the conversation."""

    @abstractmethod
    def get_messages(self) -> List[Message]:
        """Return the messages visible under this strategy's policy."""

    @abstractmethod
    def get_context(self) -> str:
        """Render visible messages as a single LLM-ready context string."""

    @abstractmethod
    def clear(self) -> None:
        """Reset all internal state."""

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _format_messages(messages: List[Message]) -> str:
        """Format a list of messages into a readable context string."""
        return "\n".join(str(m) for m in messages)


class BufferMemory(MemoryStrategy):
    """Keep every message — unbounded buffer.

    Suitable for short conversations where the full history fits within
    the LLM context window.

    Complexity:
        add_message  — O(1)
        get_messages — O(N)
        get_context  — O(N)
    """

    def __init__(self) -> None:
        self._conversation = Conversation()

    def add_message(self, message: Message) -> None:
        self._conversation.add_message(message)

    def get_messages(self) -> List[Message]:
        return self._conversation.get_messages()

    def get_context(self) -> str:
        return self._format_messages(self.get_messages())

    def clear(self) -> None:
        self._conversation.clear()


class WindowMemory(MemoryStrategy):
    """Keep the last *window_size* messages (sliding window).

    Older messages are retained internally but excluded from context.

    Args:
        window_size: Number of recent messages to surface.

    Complexity:
        add_message  — O(1)
        get_messages — O(W) where W = window_size
        get_context  — O(W)
    """

    def __init__(self, window_size: int = 10) -> None:
        if window_size < 1:
            raise ValueError("window_size must be at least 1")
        self._conversation = Conversation()
        self._window_size = window_size

    def add_message(self, message: Message) -> None:
        self._conversation.add_message(message)

    def get_messages(self) -> List[Message]:
        return self._conversation.get_last_n(self._window_size)

    def get_context(self) -> str:
        return self._format_messages(self.get_messages())

    def clear(self) -> None:
        self._conversation.clear()


class SummaryMemory(MemoryStrategy):
    """Summarize older messages, keep the most recent verbatim.

    When the conversation exceeds *max_recent* messages the older turns
    are compressed via an injected :class:`Summarizer`.  The summary is
    prepended as a system message so the LLM retains long-term context.

    Args:
        summarizer: Pluggable summarizer implementation.
        max_recent: Number of recent messages kept verbatim.

    Complexity:
        add_message  — O(1) amortized; O(S) when summarization fires
        get_messages — O(R) where R = max_recent
        get_context  — O(R)
    """

    def __init__(
        self,
        summarizer: Optional[Summarizer] = None,
        max_recent: int = 5,
    ) -> None:
        if max_recent < 1:
            raise ValueError("max_recent must be at least 1")
        self._conversation = Conversation()
        self._summarizer = summarizer or NullSummarizer()
        self._max_recent = max_recent
        self._running_summary: str = ""

    def add_message(self, message: Message) -> None:
        self._conversation.add_message(message)
        self._maybe_summarize()

    def get_messages(self) -> List[Message]:
        recent = self._conversation.get_last_n(self._max_recent)
        if self._running_summary:
            summary_msg = Message(
                role=Role.SYSTEM,
                content=f"[Summary of earlier conversation]: {self._running_summary}",
            )
            return [summary_msg] + recent
        return recent

    def get_context(self) -> str:
        return self._format_messages(self.get_messages())

    def clear(self) -> None:
        self._conversation.clear()
        self._running_summary = ""

    @property
    def running_summary(self) -> str:
        """Expose the current summary for inspection/testing."""
        return self._running_summary

    def _maybe_summarize(self) -> None:
        """Summarize overflow messages when conversation exceeds max_recent."""
        all_msgs = self._conversation.get_messages()
        if len(all_msgs) > self._max_recent:
            overflow_count = len(all_msgs) - self._max_recent
            overflow = all_msgs[:overflow_count]
            self._running_summary = self._summarizer.summarize(overflow)


class TokenLimitedMemory(MemoryStrategy):
    """Keep as many recent messages as fit within a token budget.

    Uses :meth:`Message.token_count` (word-count heuristic) to estimate
    per-message cost.  Messages are collected newest-first until the
    budget is exhausted.  At least the most recent message is always
    included, even if it alone exceeds the budget.

    Args:
        max_tokens: Maximum token budget for the context window.

    Complexity:
        add_message  — O(1)
        get_messages — O(N) worst-case (scans from newest)
        get_context  — O(N) worst-case
    """

    def __init__(self, max_tokens: int = 1000) -> None:
        if max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        self._conversation = Conversation()
        self._max_tokens = max_tokens

    def add_message(self, message: Message) -> None:
        self._conversation.add_message(message)

    def get_messages(self) -> List[Message]:
        all_msgs = self._conversation.get_messages()
        if not all_msgs:
            return []

        selected: List[Message] = []
        remaining_tokens = self._max_tokens

        for msg in reversed(all_msgs):
            cost = msg.token_count()
            if not selected:
                # Always include the most recent message
                selected.append(msg)
                remaining_tokens -= cost
            elif remaining_tokens >= cost:
                selected.append(msg)
                remaining_tokens -= cost
            else:
                break

        selected.reverse()
        return selected

    def get_context(self) -> str:
        return self._format_messages(self.get_messages())

    def clear(self) -> None:
        self._conversation.clear()


class MemoryStore:
    """Registry that manages multiple conversations by unique ID.

    Each conversation is backed by an independent ``MemoryStrategy``
    instance, ensuring complete isolation between sessions.
    """

    def __init__(self) -> None:
        self._conversations: Dict[str, MemoryStrategy] = {}

    def create_conversation(
        self, conversation_id: str, strategy: MemoryStrategy
    ) -> MemoryStrategy:
        """Register a new conversation.

        Raises:
            ValueError: If *conversation_id* is already in use.
        """
        if conversation_id in self._conversations:
            raise ValueError(f"Conversation '{conversation_id}' already exists")
        self._conversations[conversation_id] = strategy
        return strategy

    def get_conversation(self, conversation_id: str) -> MemoryStrategy:
        """Retrieve a conversation by ID.

        Raises:
            KeyError: If the conversation does not exist.
        """
        if conversation_id not in self._conversations:
            raise KeyError(f"Conversation '{conversation_id}' not found")
        return self._conversations[conversation_id]

    def delete_conversation(self, conversation_id: str) -> bool:
        """Remove a conversation. Returns True if it existed."""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False

    def list_conversations(self) -> List[str]:
        """Return all registered conversation IDs."""
        return list(self._conversations.keys())
