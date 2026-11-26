
import time
import threading
from typing import Dict, Any, Optional, Type, List
from enum import Enum
import abc
import random

class EvictionPolicy(Enum):
    LRU = "LRU"
    LFU = "LFU"
    FIFO = "FIFO"

class CacheStats:
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0

class CacheEntry:
    __slots__ = ['key', 'value', 'expire_at', 'frequency', 'created_at', 'last_accessed_at', 'prev', 'next', 'freq_node']
    
    def __init__(self, key: Any, value: Any, ttl_ms: int = -1):
        self.key = key
        self.value = value
        now = time.time() * 1000
        self.expire_at = now + ttl_ms if ttl_ms > 0 else -1
        self.frequency = 1
        self.created_at = now
        self.last_accessed_at = now
        
        self.prev = None
        self.next = None
        self.freq_node = None

    def is_expired(self, now_ms=None) -> bool:
        if self.expire_at < 0:
            return False
        if now_ms is None:
            now_ms = time.time() * 1000
        return now_ms > self.expire_at

class EvictionStrategy(abc.ABC):
    @abc.abstractmethod
    def on_access(self, entry: CacheEntry) -> None:
        pass
    @abc.abstractmethod
    def on_insert(self, entry: CacheEntry) -> None:
        pass
    @abc.abstractmethod
    def on_remove(self, entry: CacheEntry) -> None:
        pass
    @abc.abstractmethod
    def evict(self) -> Optional[CacheEntry]:
        pass
    @abc.abstractmethod
    def clear(self) -> None:
        pass

class LruStrategy(EvictionStrategy):
    def __init__(self):
        self.head = CacheEntry(None, None)
        self.tail = CacheEntry(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove_node(self, node: CacheEntry):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node: CacheEntry):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def on_access(self, entry: CacheEntry) -> None:
        self._remove_node(entry)
        self._add_to_head(entry)

    def on_insert(self, entry: CacheEntry) -> None:
        self._add_to_head(entry)

    def on_remove(self, entry: CacheEntry) -> None:
        self._remove_node(entry)

    def evict(self) -> Optional[CacheEntry]:
        if self.tail.prev == self.head:
            return None
        to_evict = self.tail.prev
        self._remove_node(to_evict)
        return to_evict

    def clear(self) -> None:
        self.head.next = self.tail
        self.tail.prev = self.head

class FifoStrategy(EvictionStrategy):
    def __init__(self):
        self.head = CacheEntry(None, None)
        self.tail = CacheEntry(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove_node(self, node: CacheEntry):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node: CacheEntry):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def on_access(self, entry: CacheEntry) -> None:
        pass

    def on_insert(self, entry: CacheEntry) -> None:
        self._add_to_head(entry)

    def on_remove(self, entry: CacheEntry) -> None:
        self._remove_node(entry)

    def evict(self) -> Optional[CacheEntry]:
        if self.tail.prev == self.head:
            return None
        to_evict = self.tail.prev
        self._remove_node(to_evict)
        return to_evict

    def clear(self) -> None:
        self.head.next = self.tail
        self.tail.prev = self.head

class FreqNode:
    __slots__ = ['freq', 'prev', 'next', 'head', 'tail']
    def __init__(self, freq: int):
        self.freq = freq
        self.prev = None
        self.next = None
        self.head = CacheEntry(None, None)
        self.tail = CacheEntry(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def add_entry(self, entry: CacheEntry):
        entry.next = self.head.next
        entry.prev = self.head
        self.head.next.prev = entry
        self.head.next = entry
        entry.freq_node = self

    def remove_entry(self, entry: CacheEntry):
        entry.prev.next = entry.next
        entry.next.prev = entry.prev

    def is_empty(self) -> bool:
        return self.head.next == self.tail

class LfuStrategy(EvictionStrategy):
    def __init__(self):
        self.freq_head = FreqNode(0)
        self.freq_tail = FreqNode(float('inf'))
        self.freq_head.next = self.freq_tail
        self.freq_tail.prev = self.freq_head
        self.freq_map = {}

    def _add_freq_node_after(self, freq: int, prev_node: FreqNode) -> FreqNode:
        new_node = FreqNode(freq)
        new_node.prev = prev_node
        new_node.next = prev_node.next
        prev_node.next.prev = new_node
        prev_node.next = new_node
        self.freq_map[freq] = new_node
        return new_node

    def _remove_freq_node(self, node: FreqNode):
        node.prev.next = node.next
        node.next.prev = node.prev
        if node.freq in self.freq_map:
            del self.freq_map[node.freq]

    def on_access(self, entry: CacheEntry) -> None:
        current_freq_node: FreqNode = entry.freq_node
        next_freq = current_freq_node.freq + 1
        
        current_freq_node.remove_entry(entry)
        
        next_freq_node = current_freq_node.next
        if next_freq_node.freq != next_freq:
            next_freq_node = self._add_freq_node_after(next_freq, current_freq_node)
            
        next_freq_node.add_entry(entry)
        entry.frequency = next_freq
        
        if current_freq_node.is_empty() and current_freq_node.freq != 0:
            self._remove_freq_node(current_freq_node)

    def on_insert(self, entry: CacheEntry) -> None:
        if entry.frequency <= 0:
            entry.frequency = 1
        freq = entry.frequency
        
        node = self.freq_map.get(freq)
        if node is None:
            prev_node = self.freq_head
            while prev_node.next != self.freq_tail and prev_node.next.freq < freq:
                prev_node = prev_node.next
            node = self._add_freq_node_after(freq, prev_node)
            
        node.add_entry(entry)

    def on_remove(self, entry: CacheEntry) -> None:
        node: FreqNode = entry.freq_node
        if node is not None:
            node.remove_entry(entry)
            if node.is_empty() and node.freq != 0:
                self._remove_freq_node(node)

    def evict(self) -> Optional[CacheEntry]:
        least_freq_node = self.freq_head.next
        if least_freq_node == self.freq_tail:
            return None
            
        to_evict = least_freq_node.tail.prev
        least_freq_node.remove_entry(to_evict)
        
        if least_freq_node.is_empty():
            self._remove_freq_node(least_freq_node)
            
        return to_evict

    def clear(self) -> None:
        self.freq_head.next = self.freq_tail
        self.freq_tail.prev = self.freq_head
        self.freq_map.clear()


class CacheSegment:
    def __init__(self, capacity: int, policy: EvictionPolicy):
        self.capacity = capacity
        self.current_policy = policy
        self.cache_map = {}
        self.lock = threading.RLock()
        self.strategy = self._create_strategy(policy)
        self.stats = CacheStats()
        self._pool = []
        for _ in range(capacity):
            self._pool.append(CacheEntry(None, None))


    def _create_strategy(self, policy: EvictionPolicy) -> EvictionStrategy:
        if policy == EvictionPolicy.LRU:
            return LruStrategy()
        elif policy == EvictionPolicy.LFU:
            return LfuStrategy()
        elif policy == EvictionPolicy.FIFO:
            return FifoStrategy()
        raise ValueError("Unknown policy")

    def put(self, key: Any, value: Any, ttl_ms: int = -1):
        with self.lock:
            now = time.time() * 1000
            if key in self.cache_map:
                entry = self.cache_map[key]
                entry.value = value
                entry.expire_at = now + ttl_ms if ttl_ms > 0 else -1
                entry.last_accessed_at = now
                entry.frequency += 1
                self.strategy.on_access(entry)
            else:
                entry = None
                if len(self.cache_map) >= self.capacity and self.capacity > 0:
                    evicted = self.strategy.evict()
                    if evicted is not None:
                        del self.cache_map[evicted.key]
                        self.stats.evictions += 1
                        entry = evicted
                
                if entry is None and self._pool:
                    entry = self._pool.pop()
                elif entry is None:
                    entry = CacheEntry(None, None)

                    
                entry.key = key
                entry.value = value
                entry.expire_at = now + ttl_ms if ttl_ms > 0 else -1
                entry.frequency = 1
                entry.created_at = now
                entry.last_accessed_at = now
                entry.prev = None
                entry.next = None
                entry.freq_node = None
                
                self.cache_map[key] = entry
                self.strategy.on_insert(entry)

    def get(self, key: Any) -> Any:
        with self.lock:
            entry = self.cache_map.get(key)
            if entry is None:
                self.stats.misses += 1
                return None
            
            now = time.time() * 1000
            if entry.is_expired(now):
                del self.cache_map[key]
                self.strategy.on_remove(entry)
                self._pool.append(entry)
                self.stats.misses += 1
                return None
                
            entry.last_accessed_at = now
            entry.frequency += 1
            self.strategy.on_access(entry)
            self.stats.hits += 1
            return entry.value

    def remove(self, key: Any):
        with self.lock:
            entry = self.cache_map.pop(key, None)
            if entry is not None:
                self.strategy.on_remove(entry)
                self._pool.append(entry)

    def change_policy(self, new_policy: EvictionPolicy):
        with self.lock:
            if self.current_policy == new_policy:
                return
            self.current_policy = new_policy
            new_strategy = self._create_strategy(new_policy)
            
            entries = list(self.cache_map.values())
            if new_policy == EvictionPolicy.LRU:
                entries.sort(key=lambda x: x.last_accessed_at)
            elif new_policy == EvictionPolicy.FIFO:
                entries.sort(key=lambda x: x.created_at)
            elif new_policy == EvictionPolicy.LFU:
                entries.sort(key=lambda x: x.last_accessed_at)
                
            self.cache_map.clear()
            now = time.time() * 1000
            for entry in entries:
                if not entry.is_expired(now):
                    new_strategy.on_insert(entry)
                    self.cache_map[entry.key] = entry
            self.strategy = new_strategy

    def active_expiration(self):
        with self.lock:
            if not self.cache_map:
                return
            
            # Probabilistic sweeping without O(N) allocation
            # We can pick a random key by using a dictionary iterator and advancing it randomly.
            # But dict iteration is deterministic and not random access in python.
            # However, for Python 3.7+, dicts are ordered.
            size = len(self.cache_map)
            if size == 0:
                return
            
            sample_size = min(20, size)
            to_remove = []
            
            import itertools
            import random
            start_idx = random.randint(0, size - 1) if size > sample_size else 0
            
            now = time.time() * 1000
            
            # Efficient slice over dict keys without full list() allocation
            iterator = iter(self.cache_map.items())
            
            # fast-forward iterator
            try:
                for _ in range(start_idx):
                    next(iterator)
                
                # collect sample
                for _ in range(sample_size):
                    try:
                        k, v = next(iterator)
                        if v.is_expired(now):
                            to_remove.append(k)
                    except StopIteration:
                        # wrap around
                        iterator = iter(self.cache_map.items())
                        k, v = next(iterator)
                        if v.is_expired(now):
                            to_remove.append(k)
            except Exception:
                pass
                
            for k in to_remove:
                entry = self.cache_map.pop(k, None)
                if entry:
                    self.strategy.on_remove(entry)
                    self._pool.append(entry)

    def size(self) -> int:
        with self.lock:
            return len(self.cache_map)

class MultiPolicyCache:
    def __init__(self, capacity: int, policy: EvictionPolicy, num_segments: int = 16):
        self.capacity = capacity
        self.num_segments = num_segments
        segment_capacity = max(1, capacity // num_segments)
        self.segments = [CacheSegment(segment_capacity, policy) for _ in range(num_segments)]
        
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._active_expiration, daemon=True)
        self.cleanup_thread.start()

    def _get_segment(self, key: Any) -> CacheSegment:
        return self.segments[hash(key) % self.num_segments]

    def _active_expiration(self):
        while self.running:
            time.sleep(1.0)
            for segment in self.segments:
                if not self.running:
                    break
                segment.active_expiration()

    def shutdown(self):
        self.running = False

    def put(self, key: Any, value: Any, ttl_ms: int = -1):
        self._get_segment(key).put(key, value, ttl_ms)

    def get(self, key: Any) -> Any:
        return self._get_segment(key).get(key)

    def remove(self, key: Any):
        self._get_segment(key).remove(key)

    def change_policy(self, new_policy: EvictionPolicy):
        for segment in self.segments:
            segment.change_policy(new_policy)

    def size(self) -> int:
        return sum(segment.size() for segment in self.segments)

    def get_stats(self) -> CacheStats:
        total_stats = CacheStats()
        for segment in self.segments:
            with segment.lock:
                total_stats.hits += segment.stats.hits
                total_stats.misses += segment.stats.misses
                total_stats.evictions += segment.stats.evictions
        return total_stats
