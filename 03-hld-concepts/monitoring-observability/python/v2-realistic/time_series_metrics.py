"""
V2: Time-Series with Windowing

Aggregates metrics over time windows.
"""

import time
import threading
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Sample:
    """A timestamped sample."""
    timestamp: float
    value: float


@dataclass
class MetricStats:
    """Statistics for a metric."""
    count: int
    min: float
    max: float
    avg: float
    p99: float


class WindowedMetric:
    """Metric with time-windowed aggregation."""
    
    def __init__(self, window_size_seconds: float):
        self._window_size = window_size_seconds
        self._samples: List[Sample] = []
        self._lock = threading.Lock()

    def record(self, value: float) -> None:
        """Record a value."""
        with self._lock:
            self._samples.append(Sample(time.time(), value))
            self._cleanup()

    def _cleanup(self) -> None:
        """Remove old samples."""
        cutoff = time.time() - self._window_size
        self._samples = [s for s in self._samples if s.timestamp >= cutoff]

    def get_stats(self) -> MetricStats:
        """Get statistics for current window."""
        with self._lock:
            self._cleanup()
            if not self._samples:
                return MetricStats(0, 0, 0, 0, 0)
            
            values = sorted(s.value for s in self._samples)
            count = len(values)
            min_val = values[0]
            max_val = values[-1]
            avg = sum(values) / count
            p99 = values[int(count * 0.99)] if count > 0 else 0
            
            return MetricStats(count, min_val, max_val, avg, p99)


class TimeSeriesMetrics:
    """
    Time-series metrics with windowing.
    
    Example:
        metrics = TimeSeriesMetrics(window_size_seconds=60)
        metrics.record("latency", 45.2)
        stats = metrics.get_stats("latency")
    """
    
    def __init__(self, window_size_seconds: float = 60):
        self._window_size = window_size_seconds
        self._metrics: Dict[str, WindowedMetric] = {}
        self._lock = threading.Lock()

    def record(self, name: str, value: float) -> None:
        """Record a metric value."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = WindowedMetric(self._window_size)
        self._metrics[name].record(value)

    def get_stats(self, name: str) -> MetricStats:
        """Get statistics for a metric."""
        metric = self._metrics.get(name)
        return metric.get_stats() if metric else MetricStats(0, 0, 0, 0, 0)

    def print_all(self) -> None:
        """Print all metrics."""
        print("=== Time Series Metrics (last window) ===")
        for name, metric in self._metrics.items():
            stats = metric.get_stats()
            print(f"{name}: count={stats.count}, min={stats.min:.2f}, "
                  f"max={stats.max:.2f}, avg={stats.avg:.2f}, p99={stats.p99:.2f}")


if __name__ == "__main__":
    import random
    
    metrics = TimeSeriesMetrics(window_size_seconds=5)
    
    for _ in range(1000):
        metrics.record("request_latency_ms", random.gauss(100, 20))
        metrics.record("requests", 1)
    
    metrics.print_all()
