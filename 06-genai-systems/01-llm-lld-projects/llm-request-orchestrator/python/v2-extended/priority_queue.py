"""Multi-tier priority queue and load shedding."""

import heapq
import threading
import time
from typing import Any, Tuple, Optional
from enum import IntEnum

class Tier(IntEnum):
    VIP = 1
    PAID = 2
    FREE = 3

class PriorityQueue:
    """Thread-safe multi-tier priority queue for load shedding."""

    def __init__(self, max_size: int):
        self.max_size = max_size
        self._queue = []
        self._lock = threading.Lock()
        self._counter = 0

    def enqueue(self, item: Any, tier: Tier, priority: int = 0) -> bool:
        """
        Enqueues an item. If queue is full, attempts to load shed the lowest priority
        (highest numerical tier value) item. Returns True if enqueued, False if rejected.
        Higher priority within the same tier can be specified with a lower 'priority' integer.
        """
        with self._lock:
            # heapq acts as a min-heap. So we store (Tier, priority, counter, item)
            # This ensures Tier.VIP (1) is popped before Tier.FREE (3).
            # If tiers are equal, lower priority number wins.
            # If both are equal, insertion order (counter) wins.
            entry = (tier.value, priority, self._counter, item)

            if len(self._queue) < self.max_size:
                heapq.heappush(self._queue, entry)
                self._counter += 1
                return True
            else:
                # Queue is full, let's see if we can shed a lower tier item
                # The "lowest" priority item would be the one with the maximum tier value,
                # maximum priority value, maximum counter.
                # heapq doesn't support easy finding of the max element, but we can do a linear scan
                # because the queue size for this project is reasonably small, or we can maintain a max-heap.
                # For simplicity, let's just find the max element linearly.
                max_idx = 0
                for i in range(1, len(self._queue)):
                    # Compare (tier, priority, -counter) to find the absolute worst item to keep
                    # Note: we want to shed the item that was added last if everything else is equal,
                    # so a higher counter is worse.
                    if self._queue[i][:3] > self._queue[max_idx][:3]:
                        max_idx = i

                worst_entry = self._queue[max_idx]
                if entry[:2] < worst_entry[:2]:
                    # Our new entry is better than the worst entry, swap them
                    self._queue[max_idx] = self._queue[-1]
                    self._queue.pop()
                    heapq.heapify(self._queue)
                    heapq.heappush(self._queue, entry)
                    self._counter += 1
                    return True
                else:
                    return False

    def dequeue(self) -> Optional[Any]:
        """Dequeues the highest priority item."""
        with self._lock:
            if not self._queue:
                return None
            return heapq.heappop(self._queue)[3]

    def qsize(self) -> int:
        with self._lock:
            return len(self._queue)
