import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))
from streaming_chunker import StreamingChunker
from async_batch_indexer import AsyncBatchIndexer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from chunker import Chunk
from index import InMemoryIndex

def test_streaming_chunker_basic():
    chunker = StreamingChunker(chunk_size=10, overlap=2)
    stream = iter(["Hello ", "world! ", "This is a ", "test."])
    # Total length: 6 + 7 + 10 + 5 = 28

    chunks = list(chunker.chunk_stream(stream, doc_id="test-doc"))

    # Chunk 1: "Hello worl" (len 10, start 0)
    # Chunk 2: "rld! This " (len 10, start 8)
    # Chunk 3: "s is a tes" (len 10, start 16)
    # Chunk 4: "st." (len 3, start 24) -- wait, 28 - 24 = 4. Let's trace.
    # Actually, let's just check lengths and offsets.

    assert len(chunks) == 4
    assert chunks[0].text == "Hello worl"
    assert chunks[0].start_pos == 0
    assert chunks[0].end_pos == 10

    assert chunks[1].text == "rld! This "
    assert chunks[1].start_pos == 8
    assert chunks[1].end_pos == 18

    assert chunks[2].text == "s is a tes"
    assert chunks[2].start_pos == 16
    assert chunks[2].end_pos == 26

    assert chunks[3].text == "est."
    assert chunks[3].start_pos == 24
    assert chunks[3].end_pos == 28

    # All chunks should have the same doc_id
    for chunk in chunks:
        assert chunk.doc_id == "test-doc"


def test_streaming_chunker_exact_boundary():
    chunker = StreamingChunker(chunk_size=5, overlap=0)
    stream = iter(["abcde", "fghij"])

    chunks = list(chunker.chunk_stream(stream))
    assert len(chunks) == 2
    assert chunks[0].text == "abcde"
    assert chunks[1].text == "fghij"


def test_async_batch_indexer_success():
    backend = InMemoryIndex()
    indexer = AsyncBatchIndexer(backend, batch_size=2, max_concurrency=2)

    chunker = StreamingChunker(chunk_size=5, overlap=0)
    stream = iter(["12345", "67890", "abcde"])
    chunk_stream = chunker.chunk_stream(stream)

    asyncio.run(indexer.process_stream(chunk_stream))

    assert backend.size() == 3


def test_async_batch_indexer_partial_failure():
    # We will create a mock backend that fails on a specific chunk to test retries
    class MockFailingBackend(InMemoryIndex):
        def __init__(self):
            super().__init__()
            self.failure_count = 0

        def add(self, chunk: Chunk, embedding: list) -> None:
            if chunk.text == "fail " and self.failure_count < 2:
                self.failure_count += 1
                raise RuntimeError("Simulated failure")
            super().add(chunk, embedding)

    backend = MockFailingBackend()
    indexer = AsyncBatchIndexer(backend, batch_size=2, max_retries=3)

    # 4 chunks: "good1", "fail ", "good2", "good3"
    chunker = StreamingChunker(chunk_size=5, overlap=0)
    stream = iter(["good1", "fail ", "good2", "good3"])
    chunk_stream = chunker.chunk_stream(stream)

    asyncio.run(indexer.process_stream(chunk_stream))

    # Since max_retries=3, it should succeed on the 3rd attempt (after 2 failures)
    assert backend.size() == 4
    assert backend.failure_count == 2


def test_async_batch_indexer_max_retries_exceeded():
    class AlwaysFailingBackend(InMemoryIndex):
        def add(self, chunk: Chunk, embedding: list) -> None:
            raise RuntimeError("Always fails")

    backend = AlwaysFailingBackend()
    indexer = AsyncBatchIndexer(backend, batch_size=2, max_retries=1)

    chunker = StreamingChunker(chunk_size=5, overlap=0)
    stream = iter(["chunk"])
    chunk_stream = chunker.chunk_stream(stream)

    asyncio.run(indexer.process_stream(chunk_stream))

    # It will try once, fail, retry once, fail, and drop it.
    assert backend.size() == 0
