"""
LRU Cache - V1 Basic

Least Recently Used (LRU) cache implementation.
Uses HashMap for O(1) lookup and Doubly Linked List for O(1) order maintenance.
"""
from typing import Dict, Optional, TypeVar, Generic
from cache_node import CacheNode, DoublyLinkedList

K = TypeVar('K')
V = TypeVar('V')


class LRUCache(Generic[K, V]):
    """
    LRU Cache with O(1) get and put operations.
    
    Attributes:
        capacity: Maximum number of entries
    """
    
    def __init__(self, capacity: int):
        """
        Create an LRU cache with specified capacity.
        
        Args:
            capacity: Maximum number of entries (must be >= 1)
        """
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        
        self._capacity = capacity
        self._cache: Dict[K, CacheNode[K, V]] = {}
        self._list: DoublyLinkedList[K, V] = DoublyLinkedList()

    def get(self, key: K) -> Optional[V]:
        """
        Get value by key. Returns None if key doesn't exist.
        Marks the entry as recently used.
        
        Time: O(1)
        """
        node = self._cache.get(key)
        if node is None:
            return None
        
        # Move to front (most recently used)
        self._list.move_to_front(node)
        return node.value

    def put(self, key: K, value: V) -> None:
        """
        Insert or update a key-value pair.
        If cache is full and inserting new key, evicts least recently used entry.
        
        Time: O(1)
        """
        if key is None:
            raise ValueError("Key cannot be None")

        existing_node = self._cache.get(key)

        if existing_node is not None:
            # Update existing entry
            existing_node.value = value
            self._list.move_to_front(existing_node)
        else:
            # Insert new entry
            if len(self._cache) >= self._capacity:
                self._evict()

            new_node = CacheNode(key, value)
            self._cache[key] = new_node
            self._list.add_to_front(new_node)

    def remove(self, key: K) -> Optional[V]:
        """
        Remove an entry by key.
        
        Returns:
            The removed value, or None if key didn't exist
        """
        node = self._cache.pop(key, None)
        if node is None:
            return None
        
        self._list.remove(node)
        return node.value

    def contains_key(self, key: K) -> bool:
        """
        Check if key exists in cache.
        Does NOT update access order.
        """
        return key in self._cache

    def size(self) -> int:
        """Get current number of entries."""
        return len(self._cache)

    @property
    def capacity(self) -> int:
        """Get maximum capacity."""
        return self._capacity

    def clear(self) -> None:
        """Remove all entries."""
        self._cache.clear()
        while not self._list.is_empty():
            self._list.remove_last()

    def _evict(self) -> None:
        """Evict the least recently used entry."""
        lru = self._list.remove_last()
        if lru is not None:
            del self._cache[lru.key]

    def __str__(self) -> str:
        return f"LRUCache{{capacity={self._capacity}, size={self.size()}, order={self._list}}}"

    def __repr__(self) -> str:
        return self.__str__()
