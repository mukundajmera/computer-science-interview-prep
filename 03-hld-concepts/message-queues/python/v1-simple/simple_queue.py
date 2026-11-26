import threading
import time
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')

class SimpleQueue(Generic[T]):
    """
    A bounded blocking queue implementation using threading.Condition.
    This provides back-pressure by blocking publishers when the queue is full.
    
    This queue is designed to be thread-safe and can be used in multi-threaded
    applications where producers and consumers operate independently.
    """
    def __init__(self, max_size: int = 100):
        """
        Initialize the bounded blocking queue.
        
        Args:
            max_size: The maximum number of items the queue can hold.
                      Defaults to 100.
        """
        self._max_size = max_size
        self._queue: List[T] = []
        
        # Lock for synchronizing access to the queue state
        self._lock = threading.Lock()
        
        # Conditions for blocking/signaling
        # _not_empty is notified when an item is added (so waiting consumers can wake up)
        # _not_full is notified when an item is removed (so waiting producers can wake up)
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)

    def enqueue(self, message: T, timeout: Optional[float] = None) -> bool:
        """
        Add a message to the queue.
        Blocks if the queue is full, up to 'timeout' seconds.
        
        Args:
            message: The item to add to the queue.
            timeout: Optional maximum time to wait (in seconds) before giving up.
            
        Returns:
            True if the item was successfully added, False if the timeout expired.
        """
        with self._not_full:
            if timeout is None:
                # Block indefinitely until there is space
                while len(self._queue) >= self._max_size:
                    self._not_full.wait()
            else:
                # Block with a timeout
                end_time = time.time() + timeout
                while len(self._queue) >= self._max_size:
                    remaining = end_time - time.time()
                    if remaining <= 0:
                        return False
                    self._not_full.wait(remaining)

            self._queue.append(message)
            # Notify a waiting consumer that an item is available
            self._not_empty.notify()
            return True

    def dequeue(self, timeout: Optional[float] = None) -> Optional[T]:
        """
        Remove and return a message from the queue.
        Blocks if the queue is empty, up to 'timeout' seconds.
        
        Args:
            timeout: Optional maximum time to wait (in seconds) before giving up.
            
        Returns:
            The message if successful, None if the timeout expired.
        """
        with self._not_empty:
            if timeout is None:
                # Block indefinitely until an item is available
                while not self._queue:
                    self._not_empty.wait()
            else:
                # Block with a timeout
                end_time = time.time() + timeout
                while not self._queue:
                    remaining = end_time - time.time()
                    if remaining <= 0:
                        return None
                    self._not_empty.wait(remaining)

            message = self._queue.pop(0)
            # Notify a waiting producer that space is available
            self._not_full.notify()
            return message

    def size(self) -> int:
        """Return the current number of items in the queue."""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        with self._lock:
            return len(self._queue) == 0

    def is_full(self) -> bool:
        """Check if the queue is at capacity."""
        with self._lock:
            return len(self._queue) >= self._max_size

    def clear(self) -> None:
        """Remove all items from the queue."""
        with self._lock:
            self._queue.clear()
            self._not_full.notify_all()
