import math
from typing import List, Dict, Optional
from enum import Enum

class AggregationType(Enum):
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    SUM = "SUM"

class DataPoint:
    def __init__(self, metric_name: str, timestamp: int, value: float, tags: Optional[Dict[str, str]] = None):
        self.metric_name = metric_name
        self.timestamp = timestamp
        self.value = value
        self.tags = tags or {}

    def __repr__(self):
        return f"DataPoint({self.metric_name}, {self.timestamp}, {self.value}, {self.tags})"

class TimeSeriesDownsampler:
    def __init__(self):
        # Maps metric_name to list of DataPoints
        self.data: Dict[str, List[DataPoint]] = {}

    def insert(self, point: DataPoint):
        """Inserts a new data point into the time series database."""
        if point.metric_name not in self.data:
            self.data[point.metric_name] = []
        self.data[point.metric_name].append(point)
        # Keep them sorted by timestamp for easier range queries
        self.data[point.metric_name].sort(key=lambda p: p.timestamp)

    def range_query(self, metric_name: str, start_time: int, end_time: int, tags: Optional[Dict[str, str]] = None) -> List[DataPoint]:
        """Queries data points within a specific time range, optionally filtering by tags."""
        if metric_name not in self.data:
            return []

        result = []
        for p in self.data[metric_name]:
            if start_time <= p.timestamp <= end_time:
                # Check tags if provided
                if tags:
                    match = True
                    for k, v in tags.items():
                        if p.tags.get(k) != v:
                            match = False
                            break
                    if not match:
                        continue
                result.append(p)
        return result

    def downsample(self, metric_name: str, bucket_size_seconds: int, agg_type: AggregationType) -> List[DataPoint]:
        """
        Rolls up raw points to buckets (e.g., 60 for 1-minute, 300 for 5-minute, 3600 for 1-hour).
        Returns a list of downsampled DataPoints.
        """
        if metric_name not in self.data or not self.data[metric_name]:
            return []

        # Group by bucket
        # Bucket is determined by (timestamp // bucket_size_seconds) * bucket_size_seconds
        buckets: Dict[int, List[float]] = {}
        for p in self.data[metric_name]:
            bucket_ts = (p.timestamp // bucket_size_seconds) * bucket_size_seconds
            if bucket_ts not in buckets:
                buckets[bucket_ts] = []
            buckets[bucket_ts].append(p.value)

        downsampled_points = []
        for bucket_ts in sorted(buckets.keys()):
            values = buckets[bucket_ts]
            if agg_type == AggregationType.AVG:
                val = sum(values) / len(values)
            elif agg_type == AggregationType.MIN:
                val = min(values)
            elif agg_type == AggregationType.MAX:
                val = max(values)
            elif agg_type == AggregationType.SUM:
                val = sum(values)
            else:
                raise ValueError("Unsupported aggregation type")

            # Downsampled data points omit specific tags as they represent aggregated data
            downsampled_points.append(DataPoint(metric_name, bucket_ts, val, {}))

        return downsampled_points

    def apply_retention(self, current_time: int, retention_period_seconds: int):
        """
        Simulates retention tiering by removing points that are older than current_time - retention_period_seconds.
        """
        cutoff_time = current_time - retention_period_seconds
        for metric in list(self.data.keys()):
            self.data[metric] = [p for p in self.data[metric] if p.timestamp >= cutoff_time]
            if not self.data[metric]:
                del self.data[metric]
