"""
Message, Role, and Conversation models for the conversation memory store.

Provides the core data structures for representing chat turns and
organizing them into conversation histories.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import time


class Role(Enum):
    """Identifies the author of a conversation message."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """A single conversation turn.

    Attributes:
        role: Who produced the message (user, assistant, or system).
        content: The text body of the message.
        timestamp: Unix timestamp of creation; auto-set if omitted.
        metadata: Extensible key-value pairs (e.g. model name, latency).
    """
    role: Role
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, object] = field(default_factory=dict)

    def token_count(self) -> int:
        """Estimate token count using a simple word-count heuristic.

        In production this would delegate to a real tokenizer (e.g. tiktoken).
        The word-count approximation is sufficient for design-level demonstration.

        Returns:
            Estimated number of tokens.
        """
        return len(self.content.split())

    def __str__(self) -> str:
        return f"[{self.role.value}]: {self.content}"


class Conversation:
    """An ordered collection of messages forming a single chat session.

    Conversation is a thin container that supports append, retrieval, and
    simple keyword search.  Memory strategies wrap a Conversation to
    decide which messages are surfaced as context.
    """

    def __init__(self) -> None:
        self._messages: List[Message] = []

    def add_message(self, message: Message) -> None:
        """Append a message to the conversation."""
        self._messages.append(message)

    def get_messages(self) -> List[Message]:
        """Return all messages in insertion order."""
        return list(self._messages)

    def get_last_n(self, n: int) -> List[Message]:
        """Return the last *n* messages.

        If *n* exceeds the conversation length, all messages are returned.
        """
        if n <= 0:
            return []
        return list(self._messages[-n:])

    def search(self, keyword: str) -> List[Message]:
        """Return messages whose content contains *keyword* (case-insensitive)."""
        keyword_lower = keyword.lower()
        return [m for m in self._messages if keyword_lower in m.content.lower()]

    def clear(self) -> None:
        """Remove all messages."""
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)

    def __repr__(self) -> str:
        return f"Conversation(messages={len(self._messages)})"
