"""
LRU Cache - V2 Extended

Cache entry with TTL (Time-To-Live) support.
"""
import time
from typing import Optional, TypeVar, Generic
from enum import Enum

K = TypeVar('K')
V = TypeVar('V')


class EvictionCause(Enum):
    """Cause of eviction."""
    CAPACITY = "CAPACITY"      # Evicted due to capacity limit
    EXPIRED = "EXPIRED"        # Evicted due to TTL expiration
    EXPLICIT = "EXPLICIT"      # Explicitly removed by user
    REPLACED = "REPLACED"      # Value replaced with new value


class CacheEntry(Generic[K, V]):
    """Cache entry with TTL support."""
    
    def __init__(self, key: K, value: V, ttl_ms: int = -1):
        self.key = key
        self.value = value
        self.created_at = int(time.time() * 1000)
        self.expires_at = self.created_at + ttl_ms if ttl_ms > 0 else -1
        self.access_count = 0
        
        self.prev: Optional['CacheEntry[K, V]'] = None
        self.next: Optional['CacheEntry[K, V]'] = None

    def touch(self) -> None:
        """Mark entry as accessed (for statistics)."""
        self.access_count += 1

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return self.expires_at > 0 and int(time.time() * 1000) > self.expires_at

    def remaining_ttl_ms(self) -> int:
        """Get remaining time-to-live in milliseconds."""
        if self.expires_at <= 0:
            return -1  # No expiration
        remaining = self.expires_at - int(time.time() * 1000)
        return max(0, remaining)

    def __str__(self) -> str:
        return f"({self.key}={self.value})"


class DoublyLinkedList(Generic[K, V]):
    """Doubly linked list for maintaining access order."""
    
    def __init__(self):
        self.head: CacheEntry[K, V] = CacheEntry(None, None)
        self.tail: CacheEntry[K, V] = CacheEntry(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def add_to_front(self, entry: CacheEntry[K, V]) -> None:
        entry.prev = self.head
        entry.next = self.head.next
        self.head.next.prev = entry
        self.head.next = entry
        self._size += 1

    def remove(self, entry: CacheEntry[K, V]) -> None:
        entry.prev.next = entry.next
        entry.next.prev = entry.prev
        self._size -= 1

    def move_to_front(self, entry: CacheEntry[K, V]) -> None:
        self.remove(entry)
        self.add_to_front(entry)

    def remove_last(self) -> Optional[CacheEntry[K, V]]:
        if self.is_empty():
            return None
        last = self.tail.prev
        self.remove(last)
        return last

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def __str__(self) -> str:
        nodes = []
        current = self.head.next
        while current != self.tail:
            nodes.append(str(current))
            current = current.next
        return "[" + " -> ".join(nodes) + "]"
