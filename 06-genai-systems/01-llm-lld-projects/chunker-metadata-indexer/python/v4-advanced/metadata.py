"""
Advanced metadata extraction module.

Attaches source document ID, chunk index, byte offsets, and token estimates to chunks.
"""

from typing import List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from chunker import Chunk, Document, MetadataTag
from chunkers import SimpleTokenizer

class AdvancedMetadataExtractor:
    """Enrich :class:`Chunk` objects with advanced metadata tags.
    """

    def __init__(self):
        self.tokenizer = SimpleTokenizer()

    def extract(self, chunks: List[Chunk], document: Document) -> List[Chunk]:
        """Attach metadata tags to each chunk and return the enriched list.
        """
        standard_keys = {
            "source", "doc_id", "position", "word_count",
            "char_count", "start_pos", "end_pos", "byte_start", "byte_end", "token_estimate"
        }
        total = len(chunks)
        
        # Calculate byte offsets by converting to utf-8 up to the character pos
        doc_bytes = document.text.encode('utf-8')
        
        for idx, chunk in enumerate(chunks):
            existing = [t for t in chunk.metadata if t.key not in standard_keys]
            
            # byte offsets
            byte_start = len(document.text[:chunk.start_pos].encode('utf-8'))
            byte_end = len(document.text[:chunk.end_pos].encode('utf-8'))
            
            token_estimate = len(self.tokenizer.encode(chunk.text))
            
            standard_tags = [
                MetadataTag(key="source", value=document.source),
                MetadataTag(key="doc_id", value=document.doc_id),
                MetadataTag(key="position", value=f"chunk {idx + 1} of {total}"),
                MetadataTag(key="word_count", value=str(self._word_count(chunk.text))),
                MetadataTag(key="char_count", value=str(self._char_count(chunk.text))),
                MetadataTag(key="start_pos", value=str(chunk.start_pos)),
                MetadataTag(key="end_pos", value=str(chunk.end_pos)),
                MetadataTag(key="byte_start", value=str(byte_start)),
                MetadataTag(key="byte_end", value=str(byte_end)),
                MetadataTag(key="token_estimate", value=str(token_estimate)),
            ]
            chunk.metadata = existing + standard_tags
        return chunks

    @staticmethod
    def _word_count(text: str) -> int:
        return len(text.split())

    @staticmethod
    def _char_count(text: str) -> int:
        return len(text)
