import time
import hashlib
import heapq
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import threading


class CountMinSketch:
    def __init__(self, width: int = 1000, depth: int = 5):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]
        
    def _hash(self, item: str, seed: int) -> int:
        h = hashlib.md5(f"{seed}_{item}".encode()).hexdigest()
        return int(h, 16) % self.width
        
    def add(self, item: str, count: int = 1):
        for i in range(self.depth):
            idx = self._hash(item, i)
            self.table[i][idx] += count
            
    def estimate(self, item: str) -> int:
        min_count = float('inf')
        for i in range(self.depth):
            idx = self._hash(item, i)
            min_count = min(min_count, self.table[i][idx])
        return min_count


@dataclass(order=True)
class HeapItem:
    count: int
    video_id: str = field(compare=False)


class ViewEventIngestor:
    def __init__(self, k: int = 10, window_sec: float = 60.0, sketch_width: int = 1000, sketch_depth: int = 5):
        self.k = k
        self.window_sec = window_sec
        
        self.cms = CountMinSketch(width=sketch_width, depth=sketch_depth)
        # Min-Heap for top-K: stores tuples of (count, video_id)
        self.top_k_heap: List[HeapItem] = []
        self.top_k_set = set() # To keep track of what's in the heap
        
        # Keep track of events for decaying window
        self.events: List[Tuple[float, str]] = []
        
        self.lock = threading.RLock()

    def _cleanup_old_events(self, current_time: float):
        # Remove events older than window
        cutoff_time = current_time - self.window_sec
        removed_counts: Dict[str, int] = {}
        
        while self.events and self.events[0][0] < cutoff_time:
            _, video_id = self.events.pop(0)
            removed_counts[video_id] = removed_counts.get(video_id, 0) + 1
            
        # Update CMS (allow negative values or rebuild, here we just subtract)
        # In a real system CMS subtraction is tricky if not conservative, but for simple decaying we do it.
        for vid, count in removed_counts.items():
            for i in range(self.cms.depth):
                idx = self.cms._hash(vid, i)
                self.cms.table[i][idx] = max(0, self.cms.table[i][idx] - count)
                
        # Rebuild heap if we removed elements
        if removed_counts:
            self._rebuild_heap()

    def _rebuild_heap(self):
        # We need a source of all distinct vids to rebuild.
        # For simplicity in this mock, we extract unique vids from remaining events.
        unique_vids = set(vid for _, vid in self.events)
        
        self.top_k_heap = []
        self.top_k_set = set()
        
        for vid in unique_vids:
            est_count = self.cms.estimate(vid)
            self._update_heap(vid, est_count)

    def _update_heap(self, video_id: str, count: int):
        if not count:
            return
            
        # If it's already in the top K, we need to rebuild the heap to update its count
        if video_id in self.top_k_set:
            # Rebuild is costly but necessary for standard heapq when updating arbitrary elements
            # Alternatively, we just append and heapify
            new_heap = []
            self.top_k_set = set()
            for item in self.top_k_heap:
                if item.video_id == video_id:
                    continue
                new_heap.append(item)
                self.top_k_set.add(item.video_id)
                
            heapq.heapify(new_heap)
            self.top_k_heap = new_heap
            
        item = HeapItem(count, video_id)
        if len(self.top_k_heap) < self.k:
            heapq.heappush(self.top_k_heap, item)
            self.top_k_set.add(video_id)
        elif count > self.top_k_heap[0].count:
            removed = heapq.heappushpop(self.top_k_heap, item)
            self.top_k_set.remove(removed.video_id)
            self.top_k_set.add(video_id)

    def ingest_view(self, video_id: str, current_time: float = None):
        if current_time is None:
            current_time = time.time()
            
        with self.lock:
            self._cleanup_old_events(current_time)
            
            self.events.append((current_time, video_id))
            self.cms.add(video_id, 1)
            
            est_count = self.cms.estimate(video_id)
            self._update_heap(video_id, est_count)

    def get_top_k(self) -> List[Tuple[str, int]]:
        with self.lock:
            # Return sorted descending by count
            sorted_items = sorted(self.top_k_heap, key=lambda x: x.count, reverse=True)
            return [(item.video_id, item.count) for item in sorted_items]

