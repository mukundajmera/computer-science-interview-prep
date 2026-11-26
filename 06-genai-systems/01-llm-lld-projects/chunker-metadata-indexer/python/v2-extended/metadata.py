"""
Metadata extraction module.

Derives standard annotations for each chunk: position within the
document, word/character counts, source reference, and offsets.
"""

from __future__ import annotations

from typing import List

from chunker import Chunk, Document, MetadataTag


class MetadataExtractor:
    """Enrich :class:`Chunk` objects with computed metadata tags.

    Standard tags produced for every chunk:
        - ``source``     — origin file or URL
        - ``doc_id``     — parent document identifier
        - ``position``   — human-readable "chunk N of M"
        - ``word_count`` — whitespace-delimited word count
        - ``char_count`` — character length
        - ``start_pos``  — starting character offset
        - ``end_pos``    — ending character offset
    """

    def extract(self, chunks: List[Chunk], document: Document) -> List[Chunk]:
        """Attach metadata tags to each chunk and return the enriched list.

        Args:
            chunks:   Chunks produced by a :class:`ChunkingStrategy`.
            document: The source :class:`Document`.

        Returns:
            The same list of chunks, now with metadata populated.

        Complexity: O(n) — single pass over all chunks.
        """
        standard_keys = {
            "source", "doc_id", "position", "word_count",
            "char_count", "start_pos", "end_pos",
        }
        total = len(chunks)
        for idx, chunk in enumerate(chunks):
            # Preserve any pre-existing custom tags (filter out standard keys
            # to avoid duplicates when re-running extraction).
            existing = [t for t in chunk.metadata if t.key not in standard_keys]
            standard_tags = [
                MetadataTag(key="source", value=document.source),
                MetadataTag(key="doc_id", value=document.doc_id),
                MetadataTag(key="position", value=f"chunk {idx + 1} of {total}"),
                MetadataTag(key="word_count", value=str(self._word_count(chunk.text))),
                MetadataTag(key="char_count", value=str(self._char_count(chunk.text))),
                MetadataTag(key="start_pos", value=str(chunk.start_pos)),
                MetadataTag(key="end_pos", value=str(chunk.end_pos)),
            ]
            chunk.metadata = existing + standard_tags
        return chunks

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _word_count(text: str) -> int:
        """Count whitespace-delimited words in *text*."""
        return len(text.split())

    @staticmethod
    def _char_count(text: str) -> int:
        """Return the character length of *text*."""
        return len(text)
