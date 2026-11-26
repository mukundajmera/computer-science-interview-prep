from typing import List


class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        combined = [interval[:] for interval in intervals] + [newInterval[:]]
        combined.sort(key=lambda interval: interval[0])
        merged = []
        for start, end in combined:
            if not merged or merged[-1][1] < start:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)
        return merged
