"""
Dynamic Batching Embedder.

Uses a background thread and a micro-batch timeout queue to aggregate
individual embedding requests into batches to maximize model/GPU throughput.
"""

import threading
import time
import queue
from typing import List, Optional
from concurrent.futures import Future

from multi_model_registry import EmbeddingModel


class DynamicBatchEmbedder:
    """Aggregates single embed requests into batches based on max batch size or timeout.

    Args:
        model: The underlying EmbeddingModel.
        max_batch_size: Maximum number of texts to process in one batch.
        timeout_ms: Maximum time to wait in milliseconds before processing an incomplete batch.
    """
    def __init__(self, model: EmbeddingModel, max_batch_size: int = 32, timeout_ms: int = 50):
        self._model = model
        self._max_batch_size = max_batch_size
        self._timeout_s = timeout_ms / 1000.0

        # Queue stores tuples of (text, Future)
        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def embed_async(self, text: str) -> Future:
        """Submit text for embedding and get a future for the result."""
        future: Future = Future()
        self._queue.put((text, future))
        return future

    def embed(self, text: str) -> List[float]:
        """Synchronously embed a text, blocking until the batch is processed."""
        future = self.embed_async(text)
        return future.result()

    def _worker_loop(self):
        """Background loop to collect and process batches."""
        while not self._stop_event.is_set():
            batch = []
            try:
                # Wait for the first item up to 100ms
                item = self._queue.get(timeout=0.1)
                batch.append(item)
            except queue.Empty:
                continue

            # We have at least one item, try to gather more up to max_batch_size or timeout
            start_time = time.time()
            while len(batch) < self._max_batch_size:
                elapsed = time.time() - start_time
                remaining = self._timeout_s - elapsed
                if remaining <= 0:
                    break
                try:
                    item = self._queue.get(timeout=remaining)
                    batch.append(item)
                except queue.Empty:
                    break

            # Process the batch
            texts = [item[0] for item in batch]
            futures = [item[1] for item in batch]
            try:
                # Use the batch method of the underlying model
                results = self._model.embed_batch(texts)
                for f, res in zip(futures, results):
                    if not f.set_running_or_notify_cancel():
                        continue
                    f.set_result(res)
            except Exception as e:
                for f in futures:
                    f.set_exception(e)

    def shutdown(self):
        """Stop the background worker thread."""
        self._stop_event.set()
        self._worker_thread.join(timeout=1.0)
