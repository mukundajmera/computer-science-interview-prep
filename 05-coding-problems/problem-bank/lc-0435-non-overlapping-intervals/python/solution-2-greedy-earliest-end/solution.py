from typing import List


class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        intervals = sorted(intervals, key=lambda interval: interval[1])
        kept = 0
        last_end = float("-inf")
        for start, end in intervals:
            if start >= last_end:
                kept += 1
                last_end = end
        return len(intervals) - kept
