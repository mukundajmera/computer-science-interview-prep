import bisect

class AppendStore:
    def __init__(self):
        self.points = []
    
    def append(self, timestamp: int, value: float):
        if self.points and timestamp < self.points[-1][0]:
            raise ValueError("Out of order write")
        self.points.append((timestamp, value))
        
    def range_query(self, start: int, end: int):
        timestamps = [p[0] for p in self.points]
        left = bisect.bisect_left(timestamps, start)
        right = bisect.bisect_right(timestamps, end)
        return self.points[left:right]
