import hashlib
import time
from urllib.parse import urlparse
from typing import Dict, List, Optional, Set
import queue


class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_second: int):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_second
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def try_consume(self) -> bool:
        self._refill()
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    def _refill(self):
        now = time.time()
        passed = now - self.last_refill
        self.tokens = min(float(self.capacity), self.tokens + (passed * self.refill_rate))
        self.last_refill = now


class LocalBloomFilter:
    def __init__(self, size: int = 1000, hash_count: int = 3):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [False] * size

    def _hashes(self, item: str) -> List[int]:
        hashes = []
        for i in range(self.hash_count):
            h = int(hashlib.sha256((item + str(i)).encode('utf-8')).hexdigest(), 16)
            hashes.append(h % self.size)
        return hashes

    def add(self, item: str):
        for h in self._hashes(item):
            self.bit_array[h] = True

    def might_contain(self, item: str) -> bool:
        for h in self._hashes(item):
            if not self.bit_array[h]:
                return False
        return True


class Coordinator:
    def __init__(self):
        self.global_dedup: Set[str] = set()
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.last_heartbeat: Dict[str, float] = {}

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) & 0xffffffff

    def register_worker(self, worker_id: str):
        h = self._hash(worker_id)
        self.ring[h] = worker_id
        self.sorted_keys = sorted(self.ring.keys())
        self.last_heartbeat[worker_id] = time.time()

    def remove_worker(self, worker_id: str):
        to_del = [k for k, v in self.ring.items() if v == worker_id]
        for k in to_del:
            del self.ring[k]
        self.sorted_keys = sorted(self.ring.keys())
        self.last_heartbeat.pop(worker_id, None)

    def heartbeat(self, worker_id: str):
        self.last_heartbeat[worker_id] = time.time()

    def get_worker_for_host(self, host: str) -> Optional[str]:
        if not self.sorted_keys:
            return None
        h = self._hash(host)
        for key in self.sorted_keys:
            if h <= key:
                return self.ring[key]
        return self.ring[self.sorted_keys[0]]

    def check_and_set_global_dedup(self, item_hash: str) -> bool:
        if item_hash in self.global_dedup:
            return False
        self.global_dedup.add(item_hash)
        return True

    def unset_global_dedup(self, item_hash: str):
        self.global_dedup.discard(item_hash)

    def get_dead_workers(self, timeout_seconds: float) -> List[str]:
        now = time.time()
        return [w for w, last_hb in self.last_heartbeat.items() if (now - last_hb) > timeout_seconds]


class WorkerNode:
    def __init__(self, worker_id: str, coordinator: Coordinator):
        self.worker_id = worker_id
        self.coordinator = coordinator
        self.local_frontier: List[str] = []
        self.local_dedup = LocalBloomFilter()
        self.rate_limits: Dict[str, TokenBucket] = {}
        self.is_running = True
        self.coordinator.register_worker(worker_id)

    def submit_url(self, url: str):
        host = self.get_host(url)
        if not host:
            return
        target = self.coordinator.get_worker_for_host(host)
        if target == self.worker_id:
            if self._is_unique(url):
                self.local_frontier.append(url)

    def force_submit_local(self, url: str):
        self.local_frontier.append(url)

    def fetch_next(self) -> Optional[str]:
        if not self.local_frontier:
            return None
        url = self.local_frontier.pop(0)
        host = self.get_host(url)
        if host:
            if host not in self.rate_limits:
                self.rate_limits[host] = TokenBucket(5, 1)
            bucket = self.rate_limits[host]
            if not bucket.try_consume():
                self.local_frontier.insert(0, url)
                return None
        return url

    def heartbeat(self):
        if self.is_running:
            self.coordinator.heartbeat(self.worker_id)

    def stop(self):
        self.is_running = False

    def get_local_frontier(self) -> List[str]:
        return self.local_frontier

    def _is_unique(self, url: str) -> bool:
        url_hash = self._hash(url)
        if self.local_dedup.might_contain(url_hash):
            return self.coordinator.check_and_set_global_dedup(url_hash)
        else:
            self.local_dedup.add(url_hash)
            self.coordinator.check_and_set_global_dedup(url_hash)
            return True

    def get_host(self, url_str: str) -> Optional[str]:
        try:
            parsed = urlparse(url_str)
            return parsed.netloc or None
        except Exception:
            return None

    def _hash(self, input_str: str) -> str:
        return hashlib.sha256(input_str.encode('utf-8')).hexdigest()


class DistributedWebCrawler:
    def __init__(self):
        self.coordinator = Coordinator()
        self.workers: Dict[str, WorkerNode] = {}

    def add_worker(self, worker_id: str) -> WorkerNode:
        worker = WorkerNode(worker_id, self.coordinator)
        self.workers[worker_id] = worker
        return worker

    def submit_to_cluster(self, url: str):
        try:
            parsed = urlparse(url)
            host = parsed.netloc
            if not host:
                return
            worker_id = self.coordinator.get_worker_for_host(host)
            if worker_id and worker_id in self.workers:
                self.workers[worker_id].submit_url(url)
        except Exception:
            pass

    def remove_worker(self, worker_id: str):
        worker = self.workers.pop(worker_id, None)
        if worker:
            worker.stop()
        self.coordinator.remove_worker(worker_id)

    def detect_and_recover_failures(self, timeout_seconds: float):
        dead_workers = self.coordinator.get_dead_workers(timeout_seconds)
        for dead_id in dead_workers:
            dead_worker = self.workers.pop(dead_id, None)
            self.coordinator.remove_worker(dead_id)

            if dead_worker:
                orphans = list(dead_worker.get_local_frontier())
                dead_worker.local_frontier.clear()
                for url in orphans:
                    self.coordinator.unset_global_dedup(dead_worker._hash(url))
                    host = dead_worker.get_host(url)
                    if host:
                        target_id = self.coordinator.get_worker_for_host(host)
                        if target_id and target_id in self.workers:
                            self.workers[target_id].force_submit_local(url)
