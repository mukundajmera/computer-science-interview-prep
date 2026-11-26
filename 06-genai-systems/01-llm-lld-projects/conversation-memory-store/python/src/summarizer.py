"""
Summarizer interface and stubs for the conversation memory store.

Provides a pluggable summarization abstraction.  In production the concrete
implementation would call an LLM; the stubs here are deterministic and
dependency-free, suitable for testing and design demonstration.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from message import Message


class Summarizer(ABC):
    """Abstract base for message summarizers.

    Subclasses compress a sequence of messages into a shorter textual
    summary.  The interface is intentionally simple so that both
    deterministic stubs and real LLM-backed implementations conform to it.
    """

    @abstractmethod
    def summarize(self, messages: "List[Message]") -> str:
        """Produce a summary string from *messages*.

        Args:
            messages: Ordered list of conversation messages to summarize.

        Returns:
            A concise textual summary.
        """


class SimpleSummarizer(Summarizer):
    """Deterministic stub that extracts the first sentence of each message.

    'First sentence' is defined as text up to and including the first
    period.  If no period is present the entire content is used.  This is
    intentionally naive — it exists to show *where* a real LLM summarizer
    would plug in.
    """

    def summarize(self, messages: "List[Message]") -> str:
        sentences: List[str] = []
        for msg in messages:
            text = msg.content.strip()
            dot_idx = text.find(".")
            if dot_idx != -1:
                sentences.append(text[: dot_idx + 1])
            else:
                sentences.append(text)
        return " ".join(sentences)


class NullSummarizer(Summarizer):
    """No-op summarizer that always returns an empty string.

    Useful as a safe default or when summarization should be disabled.
    """

    def summarize(self, messages: "List[Message]") -> str:
        return ""
