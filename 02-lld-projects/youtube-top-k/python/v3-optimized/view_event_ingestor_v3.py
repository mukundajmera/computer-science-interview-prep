import hashlib
import heapq
import json
from typing import Dict, List, Optional, Protocol
import threading

class IdempotencyStore(Protocol):
    def claim(self, key: str, ttl_ms: int) -> bool: ...


class DistributedRepository(Protocol):
    def save(self, key: str, value: str, region: str) -> None: ...
    def find(self, key: str, region: str) -> Optional[str]: ...


class CountMinSketch:
    def __init__(self, width: int = 1000, depth: int = 5):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]
        
    def _hash(self, item: str, seed: int) -> int:
        h = hashlib.md5(f"{seed}_{item}".encode()).hexdigest()
        return int(h, 16) % self.width
        
    def add(self, item: str, count: int = 1):
        if count < 0:
            return
        for i in range(self.depth):
            idx = self._hash(item, i)
            self.table[i][idx] += count
            
    def estimate(self, item: str) -> int:
        min_count = float('inf')
        for i in range(self.depth):
            idx = self._hash(item, i)
            min_count = min(min_count, self.table[i][idx])
        return min_count


class HeapItem:
    def __init__(self, count: int, video_id: str):
        self.count = count
        self.video_id = video_id
        
    def __lt__(self, other):
        if self.count != other.count:
            return self.count < other.count
        return self.video_id > other.video_id


class WindowState:
    def __init__(self, sketch_width: int, sketch_depth: int):
        self.cms = CountMinSketch(width=sketch_width, depth=sketch_depth)
        self.top_k_heap: List[HeapItem] = []
        self.top_k_map: Dict[str, HeapItem] = {}

    def to_payload(self) -> str:
        heap_items = [{"count": item.count, "video_id": item.video_id} for item in self.top_k_heap]
        return json.dumps({
            "cms_table": self.cms.table,
            "top_k_heap": heap_items
        })
        
    @staticmethod
    def from_payload(payload: str, sketch_width: int, sketch_depth: int) -> 'WindowState':
        ws = WindowState(sketch_width, sketch_depth)
        if not payload:
            return ws
        try:
            data = json.loads(payload)
            ws.cms.table = data["cms_table"]
            for item_data in data["top_k_heap"]:
                item = HeapItem(item_data["count"], item_data["video_id"])
                ws.top_k_heap.append(item)
                ws.top_k_map[item.video_id] = item
            heapq.heapify(ws.top_k_heap)
        except Exception:
            pass
        return ws
        
    def update(self, video_id: str, k: int):
        self.cms.add(video_id, 1)
        est_count = self.cms.estimate(video_id)
        
        if video_id in self.top_k_map:
            self.top_k_map[video_id].count = est_count
            heapq.heapify(self.top_k_heap)
        else:
            item = HeapItem(est_count, video_id)
            if len(self.top_k_heap) < k:
                heapq.heappush(self.top_k_heap, item)
                self.top_k_map[video_id] = item
            elif est_count > self.top_k_heap[0].count:
                removed = heapq.heappushpop(self.top_k_heap, item)
                del self.top_k_map[removed.video_id]
                self.top_k_map[video_id] = item


class ViewEventIngestorV3:
    def __init__(self, repository: DistributedRepository, idempotency: IdempotencyStore, k: int = 10):
        self.repository = repository
        self.idempotency = idempotency
        self.k = k
        self.sketch_width = 1000
        self.sketch_depth = 5
        self.windows: Dict[str, WindowState] = {}
        self.window_keys: List[str] = []
        self.max_windows = 5
        self.lock = threading.RLock()
        self.window_size_ms = 60 * 60 * 1000

    def _get_window_key(self, event_time_ms: int) -> str:
        window_start = (event_time_ms // self.window_size_ms) * self.window_size_ms
        return f"window_{window_start}"

    def ingest(self, video_id: str, event_time_ms: int, event_id: str, region: str) -> bool:
        idempotency_key = f"{video_id}:{event_id}"
        if not self.idempotency.claim(idempotency_key, 60_000):
            return False
            
        window_key = self._get_window_key(event_time_ms)
        
        with self.lock:
            if window_key not in self.windows:
                payload = self.repository.find(window_key, region)
                if payload:
                    self.windows[window_key] = WindowState.from_payload(payload, self.sketch_width, self.sketch_depth)
                else:
                    self.windows[window_key] = WindowState(self.sketch_width, self.sketch_depth)
                self.window_keys.append(window_key)
                if len(self.window_keys) > self.max_windows:
                    oldest = self.window_keys.pop(0)
                    if oldest in self.windows:
                        del self.windows[oldest]
                
            window = self.windows[window_key]
            window_update_k = self.k
            window.update(video_id, window_update_k)
            
            payload_to_save = window.to_payload()
            self.repository.save(window_key, payload_to_save, region)
            
        return True

    def top_k(self, window_key: str, k: int, region: str) -> List[str]:
        with self.lock:
            if window_key not in self.windows:
                payload = self.repository.find(window_key, region)
                if not payload:
                    return []
                window = WindowState.from_payload(payload, self.sketch_width, self.sketch_depth)
            else:
                window = self.windows[window_key]
                
            sorted_items = sorted(window.top_k_heap, key=lambda x: (-x.count, x.video_id))
            result_k = min(k, len(sorted_items))
            return [item.video_id for item in sorted_items[:result_k]]

