"""
Dynamic Batcher for embedding-service v3-optimized.

Features an asyncio-based DynamicBatcher that queues incoming items,
flushing them either when `max_batch_size` is reached or when a timeout occurs.
"""

import asyncio
from typing import Any, Callable, Awaitable, List

class DynamicBatcher:
    """
    A dynamic micro-batching processor.
    Collects items until `max_batch_size` is reached or `timeout_ms` elapses.
    Then passes the batch to the provided asynchronous processing function.
    """
    def __init__(self, process_batch_fn: Callable[[List[Any]], Awaitable[List[Any]]], max_batch_size: int = 32, timeout_ms: int = 50):
        self._process_batch_fn = process_batch_fn
        self._max_batch_size = max_batch_size
        self._timeout_s = timeout_ms / 1000.0

        self._queue: asyncio.Queue = asyncio.Queue()
        self._loop_task: asyncio.Task = None
        self._is_running = False

    def start(self):
        """Starts the background batching loop."""
        if self._is_running:
            return
        self._is_running = True
        loop = asyncio.get_running_loop()
        self._loop_task = loop.create_task(self._worker_loop())

    async def stop(self):
        """Stops the background batching loop and processes remaining items."""
        self._is_running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass

            # Process any remaining items
            batch = []
            while not self._queue.empty():
                batch.append(self._queue.get_nowait())

            if batch:
                await self._process_current_batch(batch)

    async def submit(self, item: Any) -> Any:
        """Submits an item for processing and returns its result asynchronously."""
        if not self._is_running:
            raise RuntimeError("DynamicBatcher is not running.")
        future = asyncio.get_running_loop().create_future()
        await self._queue.put((item, future))
        return await future

    async def _process_current_batch(self, batch: List[tuple]):
        items = [i[0] for i in batch]
        futures = [i[1] for i in batch]

        try:
            results = await self._process_batch_fn(items)
            for f, r in zip(futures, results):
                if not f.done():
                    f.set_result(r)
        except Exception as e:
            for f in futures:
                if not f.done():
                    f.set_exception(e)

    async def _worker_loop(self):
        """The core batching loop."""
        while self._is_running:
            batch = []

            try:
                # Wait indefinitely for the first item
                item = await self._queue.get()
                batch.append(item)
            except asyncio.CancelledError:
                break

            # Now we have the first item, try to gather more up to max_batch_size or timeout
            start_time = asyncio.get_running_loop().time()
            while len(batch) < self._max_batch_size:
                elapsed = asyncio.get_running_loop().time() - start_time
                remaining = self._timeout_s - elapsed

                if remaining <= 0:
                    break

                try:
                    item = await asyncio.wait_for(self._queue.get(), timeout=remaining)
                    batch.append(item)
                except asyncio.TimeoutError:
                    break
                except asyncio.CancelledError:
                    break

            # Flush batch
            if batch:
                asyncio.create_task(self._process_current_batch(batch))
