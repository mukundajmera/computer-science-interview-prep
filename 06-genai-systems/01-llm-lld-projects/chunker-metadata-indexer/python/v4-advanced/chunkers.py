"""
Advanced chunking strategies for the Document Ingestion Pipeline.

Contains:
    - TokenChunker
    - RecursiveCharacterChunker
    - MarkdownHeaderChunker
"""

import re
import uuid
from typing import List, Tuple, Optional, Callable, Dict
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
import chunker as base_chunker
from chunker import Document, Chunk, ChunkingStrategy, MetadataTag

class SimpleTokenizer:
    """A dummy tokenizer for environments restricted to the standard library.

    Splits text on whitespace and punctuation to approximate tokenization.
    """

    def encode(self, text: str) -> List[Tuple[str, int, int]]:
        """Encode text into a list of string 'tokens'."""
        words = []
        for match in re.finditer(r'\S+', text):
            words.append((match.group(), match.start(), match.end()))
        return words

    def decode(self, tokens: List[Tuple[str, int, int]]) -> str:
        """Decode a list of tokens back into text."""
        return " ".join(t[0] for t in tokens)

class TokenChunker(ChunkingStrategy):
    """Chunking strategy based on fixed-size token counts.

    Args:
        chunk_size: Maximum tokens per chunk.
        overlap: Token overlap between chunks.
    """

    def __init__(self, chunk_size: int = 100, overlap: int = 0) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")
        
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.tokenizer = SimpleTokenizer()

    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        tokens = self.tokenizer.encode(text)
        if not tokens:
            return []

        step = self.chunk_size - self.overlap
        segments = []
        start_idx = 0

        while start_idx < len(tokens):
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]

            start_pos = chunk_tokens[0][1]
            end_pos = chunk_tokens[-1][2]
            chunk_text = text[start_pos:end_pos]

            segments.append((chunk_text, start_pos, end_pos))

            start_idx += step
            if start_idx < len(tokens) and start_idx + self.overlap >= len(tokens):
                break

        return segments

class RecursiveCharacterChunker(ChunkingStrategy):
    """Recursive character splitting strategy.
    
    Tries splitting on paragraphs (\n\n), then sentences (.), then words ( ), 
    to fit within `chunk_size` characters.
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
        self.separators = ['\n\n', '\n', ' ', '']

    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        return self._recursive_split(text, 0, len(text), self.separators)

    def _recursive_split(self, text: str, global_start: int, global_end: int, separators: List[str]) -> List[Tuple[str, int, int]]:
        if len(text) <= self.chunk_size:
            return [(text, global_start, global_end)]

        separator = separators[0] if separators else ""
        for sep in separators:
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                break
                
        if separator == "":
            segments = []
            start = 0
            step = self.chunk_size - self.overlap
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                segments.append((text[start:end], global_start + start, global_start + end))
                start += step
                if start < len(text) and start + self.overlap >= len(text):
                    break
            return segments

        # Splitting logic
        if separator == '\n\n' or separator == '\n':
            parts = text.split(separator)
        else:
            parts = text.split(separator)
            
        # Add separators back except for the last element to preserve original text exactly
        sub_texts = []
        for i, part in enumerate(parts):
            if i < len(parts) - 1:
                sub_texts.append(part + separator)
            else:
                if part: # don't add empty trailing part if it was exactly separated at end
                    sub_texts.append(part)
            
        if len(sub_texts) <= 1:
            if not separators:
                return [(text, global_start, global_end)]
            return self._recursive_split(text, global_start, global_end, separators[separators.index(separator) + 1:])
            
        segments = []
        current_chunk = ""
        current_start = global_start
        
        for sub in sub_texts:
            if len(current_chunk) + len(sub) > self.chunk_size and current_chunk:
                segments.append((current_chunk, current_start, current_start + len(current_chunk)))
                current_start = current_start + len(current_chunk)
                current_chunk = sub
            else:
                current_chunk += sub
                
        if current_chunk:
            segments.append((current_chunk, current_start, current_start + len(current_chunk)))

        final_segments = []
        for seg_text, seg_start, seg_end in segments:
            if len(seg_text) > self.chunk_size:
                final_segments.extend(self._recursive_split(seg_text, seg_start, seg_end, separators[separators.index(separator) + 1:]))
            else:
                final_segments.append((seg_text, seg_start, seg_end))
                
        return final_segments

class MarkdownHeaderChunker(ChunkingStrategy):
    """Markdown header-aware semantic chunking.
    
    Groups text under markdown headers. Preserves heading breadcrumbs in the text 
    or adds them as metadata (we will add them as metadata).
    """

    def chunk(self, document: Document) -> List[Chunk]:
        """Override chunk to attach header breadcrumbs as metadata."""
        self._validate(document)
        segments = self._split_text_with_headers(document.text)
        
        chunks = []
        for text, start, end, headers in segments:
            chunk = Chunk(
                chunk_id=str(uuid.uuid4()),
                text=text.strip(),
                doc_id=document.doc_id,
                start_pos=start,
                end_pos=end,
            )
            for k, v in headers.items():
                chunk.metadata.append(MetadataTag(key=k, value=v))
            chunks.append(chunk)
        return chunks

    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        return []

    def _split_text_with_headers(self, text: str) -> List[Tuple[str, int, int, Dict[str, str]]]:
        header_pattern = re.compile(r'^(#{1,6})\s+(.*)$', re.MULTILINE)
        
        matches = list(header_pattern.finditer(text))
        if not matches:
            return [(text, 0, len(text), {})]
            
        segments = []
        current_headers: Dict[str, str] = {}
        
        if matches[0].start() > 0:
            start_text = text[0:matches[0].start()]
            if start_text.strip():
                segments.append((start_text, 0, matches[0].start(), current_headers.copy()))
                
        for i, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            
            keys_to_remove = [k for k in current_headers.keys() if int(k.replace('Header ', '')) >= level]
            for k in keys_to_remove:
                del current_headers[k]
                
            current_headers[f"Header {level}"] = title
            
            start_pos = match.start()
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(text)
            
            chunk_text = text[start_pos:end_pos]
            if chunk_text.strip():
                segments.append((chunk_text, start_pos, end_pos, current_headers.copy()))
                
        return segments
