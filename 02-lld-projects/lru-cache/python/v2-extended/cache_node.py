"""
LRU Cache - V1 Basic

Cache node and doubly linked list for maintaining access order.
"""
from typing import Optional, TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')


class CacheNode(Generic[K, V]):
    """Node for doubly linked list."""
    
    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value
        self.prev: Optional['CacheNode[K, V]'] = None
        self.next: Optional['CacheNode[K, V]'] = None

    def __str__(self) -> str:
        return f"({self.key}={self.value})"


class DoublyLinkedList(Generic[K, V]):
    """
    Doubly linked list for maintaining access order.
    Uses sentinel nodes (dummy head and tail) to simplify operations.
    """
    
    def __init__(self):
        self.head: CacheNode[K, V] = CacheNode(None, None)  # Dummy head
        self.tail: CacheNode[K, V] = CacheNode(None, None)  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def add_to_front(self, node: CacheNode[K, V]) -> None:
        """Add node right after head (most recently used position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        self._size += 1

    def remove(self, node: CacheNode[K, V]) -> None:
        """Remove a node from its current position."""
        node.prev.next = node.next
        node.next.prev = node.prev
        self._size -= 1

    def move_to_front(self, node: CacheNode[K, V]) -> None:
        """Move an existing node to the front."""
        self.remove(node)
        self.add_to_front(node)

    def remove_last(self) -> Optional[CacheNode[K, V]]:
        """Remove and return the last node (least recently used)."""
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
