"""
V1: Simple Metric Collection

Basic metric collection and storage.
"""

import time
from typing import Dict, List
from dataclasses import dataclass
from collections import defaultdict
import threading


@dataclass
class DataPoint:
    """A single metric data point."""
    timestamp: float
    value: float


class SimpleMetrics:
    """
    Simple metric collection.
    
    Example:
        metrics = SimpleMetrics()
        metrics.record("request_latency_ms", 45.2)
        metrics.increment("request_count")
    """
    
    def __init__(self):
        self._metrics: Dict[str, List[DataPoint]] = defaultdict(list)
        self._lock = threading.Lock()

    def record(self, name: str, value: float) -> None:
        """Record a metric value."""
        with self._lock:
            self._metrics[name].append(DataPoint(time.time(), value))

    def increment(self, name: str) -> None:
        """Increment a counter."""
        self.record(name, 1.0)

    def get_sum(self, name: str) -> float:
        """Get sum of metric values."""
        with self._lock:
            return sum(p.value for p in self._metrics.get(name, []))

    def get_average(self, name: str) -> float:
        """Get average of metric values."""
        with self._lock:
            points = self._metrics.get(name, [])
            if not points:
                return 0
            return sum(p.value for p in points) / len(points)

    def print_all(self) -> None:
        """Print all metrics."""
        print("=== Metrics ===")
        with self._lock:
            for name, points in self._metrics.items():
                total = sum(p.value for p in points)
                avg = total / len(points) if points else 0
                print(f"{name}: count={len(points)}, sum={total:.2f}, avg={avg:.2f}")


if __name__ == "__main__":
    import random
    
    metrics = SimpleMetrics()
    
    for _ in range(100):
        metrics.increment("http_requests_total")
        metrics.record("http_request_duration_ms", random.random() * 100)
    
    metrics.print_all()
