"""Bounded producer-consumer queue for scheduler coordination."""

from __future__ import annotations

from collections import deque
from threading import Condition
from time import monotonic
from typing import Deque, Generic, Optional, TypeVar

T = TypeVar("T")


class BoundedTaskQueue(Generic[T]):
    """Thread-safe bounded queue with timeout-based offer/poll operations."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._items: Deque[T] = deque()
        self._condition = Condition()

    @property
    def capacity(self) -> int:
        return self._capacity

    def size(self) -> int:
        with self._condition:
            return len(self._items)

    def offer(self, item: T, timeout_ms: int) -> bool:
        deadline = monotonic() + max(timeout_ms, 0) / 1000.0
        with self._condition:
            while len(self._items) >= self._capacity:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    return False
                self._condition.wait(timeout=remaining)
            self._items.append(item)
            self._condition.notify()
            return True

    def poll(self, timeout_ms: int) -> Optional[T]:
        deadline = monotonic() + max(timeout_ms, 0) / 1000.0
        with self._condition:
            while not self._items:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    return None
                self._condition.wait(timeout=remaining)
            item = self._items.popleft()
            self._condition.notify()
            return item
