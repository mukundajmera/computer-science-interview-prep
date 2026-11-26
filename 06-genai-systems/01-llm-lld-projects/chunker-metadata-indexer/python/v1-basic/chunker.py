"""
Document chunking module.

Provides a Strategy-based framework for splitting documents into
retrieval-friendly chunks.  Three built-in strategies are included:
fixed-size, sentence-based, and paragraph-based.

Design patterns:
    - Strategy   — interchangeable chunking algorithms
    - Template Method — shared validation / ID-assignment in the ABC
"""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Document:
    """Raw input document to be chunked.

    Attributes:
        text:   Plain UTF-8 content.
        source: Origin reference (filename, URL, etc.).
        doc_id: Unique identifier, auto-generated if omitted.
    """

    text: str
    source: str = ""
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class MetadataTag:
    """Key-value annotation attached to a :class:`Chunk`."""

    key: str
    value: str


@dataclass
class Chunk:
    """A slice of a :class:`Document` with positional information.

    Attributes:
        chunk_id:  Unique identifier.
        text:      Chunk content.
        doc_id:    Parent document ID.
        start_pos: Starting character offset in the original document.
        end_pos:   Ending character offset in the original document.
        metadata:  List of :class:`MetadataTag` annotations.
    """

    chunk_id: str
    text: str
    doc_id: str
    start_pos: int
    end_pos: int
    metadata: List[MetadataTag] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Strategy ABC (Template Method)
# ---------------------------------------------------------------------------

class ChunkingStrategy(ABC):
    """Abstract base for chunking algorithms.

    Subclasses implement :meth:`_split_text` which returns a list of
    ``(text, start_pos, end_pos)`` tuples.  The public :meth:`chunk`
    method handles validation and wraps results in :class:`Chunk` objects.
    """

    def chunk(self, document: Document) -> List[Chunk]:
        """Split *document* into a list of :class:`Chunk` objects.

        Raises:
            ValueError: If the document text is empty or whitespace-only.
        """
        self._validate(document)
        segments = self._split_text(document.text)
        return [
            Chunk(
                chunk_id=str(uuid.uuid4()),
                text=text,
                doc_id=document.doc_id,
                start_pos=start,
                end_pos=end,
            )
            for text, start, end in segments
        ]

    @abstractmethod
    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        """Return a list of ``(chunk_text, start_pos, end_pos)`` tuples."""

    @staticmethod
    def _validate(document: Document) -> None:
        """Raise ``ValueError`` for empty or whitespace-only documents."""
        if not document.text or not document.text.strip():
            raise ValueError("Document text must not be empty or whitespace-only")


# ---------------------------------------------------------------------------
# Concrete strategies
# ---------------------------------------------------------------------------

class FixedSizeChunker(ChunkingStrategy):
    """Split text into fixed-size character windows with optional overlap.

    Args:
        chunk_size: Maximum characters per chunk.
        overlap:    Number of overlapping characters between consecutive chunks.

    Raises:
        ValueError: If *overlap* >= *chunk_size* or either value is <= 0.

    Complexity: O(n) where n = len(text).
    """

    def __init__(self, chunk_size: int = 200, overlap: int = 0) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        """Slide a window of *chunk_size* with step = chunk_size - overlap."""
        step = self.chunk_size - self.overlap
        segments: List[Tuple[str, int, int]] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            segments.append((text[start:end], start, end))
            start += step
            # Avoid a trailing micro-chunk that duplicates the previous one
            if start < len(text) and start + self.overlap >= len(text):
                # Last remaining bit is already covered by overlap
                break
        return segments


class SentenceChunker(ChunkingStrategy):
    """Group sentences into chunks.

    Sentence boundaries are detected with a simple regex heuristic:
    a period, exclamation mark, or question mark followed by whitespace
    or end-of-string.

    Args:
        max_sentences: Maximum sentences per chunk.
        overlap:       Number of overlapping sentences between chunks.

    Complexity: O(n) where n = len(text).
    """

    _SENTENCE_RE = re.compile(r'(?<=[.!?])\s+')

    def __init__(self, max_sentences: int = 3, overlap: int = 0) -> None:
        if max_sentences <= 0:
            raise ValueError("max_sentences must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= max_sentences:
            raise ValueError("overlap must be less than max_sentences")
        self.max_sentences = max_sentences
        self.overlap = overlap

    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        """Split *text* into sentence groups."""
        # Identify sentence boundaries
        sentences: List[Tuple[str, int, int]] = []
        prev = 0
        for match in self._SENTENCE_RE.finditer(text):
            end = match.start()
            segment = text[prev:end + 1]
            stripped = segment.strip()
            if stripped:
                leading = len(segment) - len(segment.lstrip())
                trailing = len(segment) - len(segment.rstrip())
                sentences.append((stripped, prev + leading, end + 1 - trailing))
            prev = match.end()
        # Trailing text (last sentence without trailing space)
        if prev < len(text):
            segment = text[prev:]
            stripped = segment.strip()
            if stripped:
                leading = len(segment) - len(segment.lstrip())
                trailing = len(segment) - len(segment.rstrip())
                sentences.append((stripped, prev + leading, len(text) - trailing))

        if not sentences:
            return [(text, 0, len(text))]

        step = self.max_sentences - self.overlap
        segments: List[Tuple[str, int, int]] = []
        idx = 0
        while idx < len(sentences):
            group = sentences[idx:idx + self.max_sentences]
            combined = " ".join(s[0] for s in group)
            start_pos = group[0][1]
            end_pos = group[-1][2]
            segments.append((combined, start_pos, end_pos))
            idx += step

        return segments


class ParagraphChunker(ChunkingStrategy):
    """Split text on paragraph boundaries (double newlines).

    Each non-empty paragraph becomes its own chunk.

    Complexity: O(n) where n = len(text).
    """

    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        """Split *text* on ``\\n\\n`` boundaries."""
        segments: List[Tuple[str, int, int]] = []
        start = 0
        for match in re.finditer(r'\n\n+', text):
            segment = text[start:match.start()]
            stripped = segment.strip()
            if stripped:
                leading = len(segment) - len(segment.lstrip())
                trailing = len(segment) - len(segment.rstrip())
                segments.append((stripped, start + leading, match.start() - trailing))
            start = match.end()
        # Trailing paragraph
        segment = text[start:]
        stripped = segment.strip()
        if stripped:
            leading = len(segment) - len(segment.lstrip())
            trailing = len(segment) - len(segment.rstrip())
            segments.append((stripped, start + leading, len(text) - trailing))
        if not segments:
            return [(text, 0, len(text))]
        return segments


# ---------------------------------------------------------------------------
# Context / orchestrator
# ---------------------------------------------------------------------------

class DocumentChunker:
    """Orchestrator that applies a :class:`ChunkingStrategy` to a document.

    This is the *context* role in the Strategy pattern.

    Args:
        strategy: The chunking algorithm to use.
    """

    def __init__(self, strategy: ChunkingStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> ChunkingStrategy:
        """Return the current chunking strategy."""
        return self._strategy

    def set_strategy(self, strategy: ChunkingStrategy) -> None:
        """Replace the chunking strategy at runtime."""
        self._strategy = strategy

    def chunk(self, document: Document) -> List[Chunk]:
        """Chunk *document* using the current strategy.

        Returns:
            A list of :class:`Chunk` objects derived from the document.
        """
        return self._strategy.chunk(document)
