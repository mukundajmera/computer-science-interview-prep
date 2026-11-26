import uuid
from typing import Iterator, List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from chunker import Chunk, Document

class StreamingChunker:
    """Memory-bounded streaming chunker that processes an iterator of strings."""

    def __init__(self, chunk_size: int = 200, overlap: int = 0) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_stream(self, stream: Iterator[str], doc_id: str = None) -> Iterator[Chunk]:
        """Yield chunks one by one from a stream of strings."""
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        buffer = ""
        current_pos = 0

        for chunk_str in stream:
            buffer += chunk_str

            while len(buffer) >= self.chunk_size:
                chunk_text = buffer[:self.chunk_size]
                yield Chunk(
                    chunk_id=str(uuid.uuid4()),
                    text=chunk_text,
                    doc_id=doc_id,
                    start_pos=current_pos,
                    end_pos=current_pos + self.chunk_size
                )

                step = self.chunk_size - self.overlap
                buffer = buffer[step:]
                current_pos += step

        # Process any remaining text in the buffer
        if buffer:
            yield Chunk(
                chunk_id=str(uuid.uuid4()),
                text=buffer,
                doc_id=doc_id,
                start_pos=current_pos,
                end_pos=current_pos + len(buffer)
            )
