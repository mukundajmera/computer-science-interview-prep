import threading
import queue
import time
from typing import Callable, List, TypeVar, Generic

T = TypeVar('T')

class WriteBatcher(Generic[T]):
    """
    A high-throughput write batcher that buffers incoming writes in memory.
    It flushes either when the batch size threshold is reached, or when the
    maximum wait duration has elapsed.
    """

    def __init__(
        self,
        capacity: int,
        batch_size_threshold: int,
        max_wait_duration_ms: int,
        batch_committer: Callable[[List[T]], None]
    ):
        if capacity < batch_size_threshold:
            raise ValueError("capacity must be >= batch_size_threshold")

        self.capacity = capacity
        self.batch_size_threshold = batch_size_threshold
        self.max_wait_duration_ms = max_wait_duration_ms
        self.batch_committer = batch_committer

        self.buffer: queue.Queue[T] = queue.Queue(maxsize=capacity)
        self._running = True

        self._worker_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._worker_thread.start()

    def write(self, item: T) -> bool:
        """
        Adds an item to the buffer.
        Returns True if added, False if the buffer is full (backpressure).
        """
        if not self._running:
            raise RuntimeError("Batcher is closed")

        try:
            self.buffer.put_nowait(item)
            return True
        except queue.Full:
            return False

    def _flush_loop(self) -> None:
        current_batch = []
        batch_start_time = time.time()
        max_wait_sec = self.max_wait_duration_ms / 1000.0

        while self._running:
            try:
                if not current_batch:
                    # Block on empty queue up to a short interval so we can periodically check self._running
                    # This avoids busy looping while empty and also prevents hanging on close
                    item = self.buffer.get(timeout=0.1)
                else:
                    time_left = max_wait_sec - (time.time() - batch_start_time)
                    if time_left <= 0:
                        self._commit_batch(current_batch)
                        batch_start_time = time.time()
                        continue
                    item = self.buffer.get(timeout=max(0.001, time_left))

                current_batch.append(item)

                if len(current_batch) == 1:
                    batch_start_time = time.time()

                if len(current_batch) >= self.batch_size_threshold:
                    self._commit_batch(current_batch)
                    batch_start_time = time.time()

            except queue.Empty:
                if current_batch and (time.time() - batch_start_time) >= max_wait_sec:
                    self._commit_batch(current_batch)
                    batch_start_time = time.time()

        # Drain remaining items
        while True:
            try:
                item = self.buffer.get_nowait()
                current_batch.append(item)
            except queue.Empty:
                break

        # Commit remaining in chunks
        for i in range(0, len(current_batch), self.batch_size_threshold):
            self._commit_batch(current_batch[i:i + self.batch_size_threshold])

    def _commit_batch(self, batch: List[T]) -> None:
        if not batch:
            return
        try:
            self.batch_committer(list(batch))
        except Exception as e:
            print(f"Error committing batch: {e}")
        finally:
            batch.clear()

    def close(self) -> None:
        """
        Stops the background thread and flushes remaining items.
        """
        self._running = False
        self._worker_thread.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
