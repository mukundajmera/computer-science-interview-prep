"""Dynamic worker-ID lease pool (v2 improvement #2).

Simulates the ZooKeeper ephemeral sequential node lease design from
FOLLOW-UPS.md #3: a node claims an available worker ID at startup, the ID
stays leased while the node lives, and releasing it (session expiry in the
real design) returns the ID to the available pool so a replacement node can
pick it up. Acquisition is collision-proof by construction and exhaustion
is loud instead of a silent collision (PITFALLS.md #2).
"""
import bisect
import threading

from exceptions import WorkerIdPoolExhaustedError


class WorkerIdPool:
    def __init__(self, max_worker_id: int = 1023):
        if max_worker_id < 0:
            raise ValueError("max_worker_id can't be less than 0")
        self.max_worker_id = max_worker_id
        self._available = list(range(max_worker_id + 1))
        self._leased = set()
        self._lock = threading.Lock()

    def acquire(self) -> int:
        """Claims the lowest available worker ID. Raises
        WorkerIdPoolExhaustedError when every ID is leased."""
        with self._lock:
            if not self._available:
                raise WorkerIdPoolExhaustedError(
                    f"All {self.max_worker_id + 1} worker IDs are leased")
            worker_id = self._available.pop(0)
            self._leased.add(worker_id)
            return worker_id

    def release(self, worker_id: int):
        """Returns a leased ID to the pool (the ephemeral node dropped)."""
        with self._lock:
            if worker_id not in self._leased:
                raise ValueError(f"Worker ID {worker_id} is not leased")
            self._leased.remove(worker_id)
            bisect.insort(self._available, worker_id)

    def is_leased(self, worker_id: int) -> bool:
        with self._lock:
            return worker_id in self._leased

    def leased_count(self) -> int:
        with self._lock:
            return len(self._leased)
