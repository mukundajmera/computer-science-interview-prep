import asyncio
import logging
from typing import List, Iterator
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from chunker import Chunk
from index import IndexBackend

logger = logging.getLogger(__name__)

class AsyncBatchIndexer:
    """Async batch indexer with bounded concurrency, partial batch failure handling, and retry queues."""

    def __init__(self, backend: IndexBackend, batch_size: int = 10, max_concurrency: int = 3, max_retries: int = 3):
        self.backend = backend
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries
        self.failed_chunks = asyncio.Queue()

    async def generate_embedding(self, chunk: Chunk) -> List[float]:
        """Simulate generating an embedding asynchronously."""
        await asyncio.sleep(0.01) # Simulate network/IO delay
        val = len(chunk.text) % 100 / 100.0
        return [val] * 10

    async def index_batch(self, batch: List[Chunk]) -> List[Chunk]:
        """Indexes a batch of chunks. Returns a list of chunks that failed to index."""
        async with self.semaphore:
            failed = []

            # Generate embeddings for the batch
            # We assume embedding generation can also fail, so we handle it per-chunk
            for chunk in batch:
                try:
                    embedding = await self.generate_embedding(chunk)
                    # We use a synchronous backend, so we call it directly.
                    # If this were a real async backend, we'd await here.
                    self.backend.add(chunk, embedding)
                except Exception as e:
                    logger.error(f"Failed to index chunk {chunk.chunk_id}: {e}")
                    failed.append(chunk)

            return failed

    async def process_stream(self, chunk_stream: Iterator[Chunk]) -> None:
        """Processes a stream of chunks asynchronously in batches."""
        batch = []
        tasks = []

        for chunk in chunk_stream:
            batch.append(chunk)
            if len(batch) >= self.batch_size:
                tasks.append(self._schedule_batch(batch))
                batch = []

        if batch:
            tasks.append(self._schedule_batch(batch))

        if tasks:
            await asyncio.gather(*tasks)

        # Process retry queues
        await self._process_retries()

    async def _schedule_batch(self, batch: List[Chunk], retry_count: int = 0) -> None:
        failed_chunks = await self.index_batch(batch)
        if failed_chunks:
            if retry_count < self.max_retries:
                logger.warning(f"Retrying {len(failed_chunks)} failed chunks, attempt {retry_count + 1}")
                # We put the failed chunks back as a new partial batch
                await self.failed_chunks.put((failed_chunks, retry_count + 1))
            else:
                logger.error(f"Max retries reached for {len(failed_chunks)} chunks. Dropping.")

    async def _process_retries(self) -> None:
        tasks = []
        while not self.failed_chunks.empty():
            batch, retry_count = await self.failed_chunks.get()
            tasks.append(self._schedule_batch(batch, retry_count))

        if tasks:
            await asyncio.gather(*tasks)
            # Recursively process if there are still failures
            await self._process_retries()
