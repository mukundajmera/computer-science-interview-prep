"""
LRU Cache - V3 Optimized

Thread-safe LRU cache using Segmented Lock Striping for high concurrency.
"""
import threading
from typing import Dict, Optional, TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')


class CacheNode(Generic[K, V]):
    """Node for doubly linked list."""
    
    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value
        self.prev: Optional['CacheNode[K, V]'] = None
        self.next: Optional['CacheNode[K, V]'] = None


class DoublyLinkedList(Generic[K, V]):
    """Doubly linked list for maintaining access order."""
    
    def __init__(self):
        self.head: CacheNode[K, V] = CacheNode(None, None)
        self.tail: CacheNode[K, V] = CacheNode(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def add_to_front(self, node: CacheNode[K, V]) -> None:
        node.prev = self.head
        node.next = self.head.next
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node
        self._size += 1

    def remove(self, node: CacheNode[K, V]) -> None:
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        self._size -= 1

    def move_to_front(self, node: CacheNode[K, V]) -> None:
        self.remove(node)
        self.add_to_front(node)

    def remove_last(self) -> Optional[CacheNode[K, V]]:
        if self.is_empty():
            return None
        last = self.tail.prev
        if last and last != self.head:
            self.remove(last)
            return last
        return None

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size


class Segment(Generic[K, V]):
    """A single segment of the concurrent cache acting as an independent LRU."""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[K, CacheNode[K, V]] = {}
        self.list: DoublyLinkedList[K, V] = DoublyLinkedList()
        self.lock = threading.Lock()
        
        # Segment statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: K) -> Optional[V]:
        with self.lock:
            node = self.cache.get(key)
            if node is None:
                self.misses += 1
                return None
            
            self.list.move_to_front(node)
            self.hits += 1
            return node.value

    def put(self, key: K, value: V) -> None:
        with self.lock:
            existing_node = self.cache.get(key)
            if existing_node is not None:
                existing_node.value = value
                self.list.move_to_front(existing_node)
            else:
                if len(self.cache) >= self.capacity:
                    lru = self.list.remove_last()
                    if lru is not None:
                        del self.cache[lru.key]
                        self.evictions += 1
                
                new_node = CacheNode(key, value)
                self.cache[key] = new_node
                self.list.add_to_front(new_node)

    def remove(self, key: K) -> Optional[V]:
        with self.lock:
            node = self.cache.pop(key, None)
            if node is None:
                return None
            self.list.remove(node)
            return node.value

    def contains_key(self, key: K) -> bool:
        with self.lock:
            return key in self.cache

    def size(self) -> int:
        with self.lock:
            return len(self.cache)

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
            while not self.list.is_empty():
                self.list.remove_last()


class ConcurrentLRUCache(Generic[K, V]):
    """
    Thread-safe LRU cache using Segmented Lock Striping.
    
    Improves concurrency by sharding the cache into segments, reducing lock contention.
    """
    
    def __init__(self, capacity: int, num_segments: int = 16):
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        if num_segments < 1:
            raise ValueError("Number of segments must be at least 1")
            
        self._capacity = capacity
        self._num_segments = num_segments
        
        # Calculate capacity per segment (round up)
        segment_capacity = (capacity + num_segments - 1) // num_segments
        
        self._segments = [Segment(segment_capacity) for _ in range(num_segments)]

    def _get_segment(self, key: K) -> Segment[K, V]:
        # Hash the key to find the segment
        segment_index = hash(key) % self._num_segments
        return self._segments[segment_index]

    def get(self, key: K) -> Optional[V]:
        """Get value by key. Thread-safe."""
        if key is None:
            raise ValueError("Key cannot be None")
        return self._get_segment(key).get(key)

    def put(self, key: K, value: V) -> None:
        """Insert or update a key-value pair. Thread-safe."""
        if key is None:
            raise ValueError("Key cannot be None")
        self._get_segment(key).put(key, value)

    def remove(self, key: K) -> Optional[V]:
        """Remove an entry by key. Thread-safe."""
        if key is None:
            raise ValueError("Key cannot be None")
        return self._get_segment(key).remove(key)

    def contains_key(self, key: K) -> bool:
        """Check if key exists. Thread-safe."""
        if key is None:
            raise ValueError("Key cannot be None")
        return self._get_segment(key).contains_key(key)

    def size(self) -> int:
        """Get current size. Thread-safe."""
        return sum(segment.size() for segment in self._segments)

    @property
    def capacity(self) -> int:
        return self._capacity

    def clear(self) -> None:
        """Remove all entries. Thread-safe."""
        for segment in self._segments:
            segment.clear()

    # Statistics methods
    
    @property
    def hits(self) -> int:
        return sum(segment.hits for segment in self._segments)

    @property
    def misses(self) -> int:
        return sum(segment.misses for segment in self._segments)

    @property
    def evictions(self) -> int:
        return sum(segment.evictions for segment in self._segments)

    @property
    def hit_ratio(self) -> float:
        h = self.hits
        m = self.misses
        total = h + m
        return h / total if total > 0 else 0.0

    def reset_statistics(self) -> None:
        for segment in self._segments:
            with segment.lock:
                segment.hits = 0
                segment.misses = 0
                segment.evictions = 0

    def __str__(self) -> str:
        return (f"ConcurrentLRUCache{{capacity={self._capacity}, "
                f"size={self.size()}, hits={self.hits}, "
                f"misses={self.misses}, hitRatio={self.hit_ratio:.2%}}}")
