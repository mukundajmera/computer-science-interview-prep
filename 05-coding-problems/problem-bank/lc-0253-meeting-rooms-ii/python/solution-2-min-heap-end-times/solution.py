import heapq
from typing import List


class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        intervals = sorted(intervals, key=lambda interval: interval[0])
        ends: List[int] = []
        for start, end in intervals:
            if ends and ends[0] <= start:
                heapq.heappop(ends)
            heapq.heappush(ends, end)
        return len(ends)
