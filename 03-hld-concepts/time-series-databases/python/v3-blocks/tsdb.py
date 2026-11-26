from collections import defaultdict

class SeriesBlock:
    def __init__(self):
        self.points = [] # list of (ts, value)
        
    def add(self, ts: int, value: float):
        if self.points and ts < self.points[-1][0]:
            raise ValueError("Out of order write")
        self.points.append((ts, value))
        
    def range_query(self, start: int, end: int):
        return [p for p in self.points if start <= p[0] <= end]

class TSDBEngine:
    def __init__(self, max_series=1000):
        self.series = defaultdict(SeriesBlock)
        self.max_series = max_series
        
    def insert(self, metric: str, ts: int, value: float):
        if metric not in self.series and len(self.series) >= self.max_series:
            raise ValueError("Cardinality limit reached")
        self.series[metric].add(ts, value)
        
    def range_query(self, metric: str, start: int, end: int):
        if metric not in self.series:
            return []
        return self.series[metric].range_query(start, end)
        
    def downsample(self, metric: str, bucket_size: int):
        if metric not in self.series:
            return []
            
        buckets = defaultdict(list)
        for ts, val in self.series[metric].points:
            b_ts = (ts // bucket_size) * bucket_size
            buckets[b_ts].append(val)
            
        res = []
        for b_ts in sorted(buckets.keys()):
            vals = buckets[b_ts]
            res.append((b_ts, sum(vals)/len(vals)))
        return res
        
    def apply_retention(self, cutoff_ts: int):
        to_delete = []
        for metric, block in self.series.items():
            block.points = [p for p in block.points if p[0] >= cutoff_ts]
            if not block.points:
                to_delete.append(metric)
        for metric in to_delete:
            del self.series[metric]

