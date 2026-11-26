from typing import List


class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        if not intervals:
            return 0
        intervals = sorted(intervals, key=lambda interval: (interval[0], interval[1]))
        dp = [1] * len(intervals)
        best = 1
        for index in range(len(intervals)):
            for previous in range(index):
                if intervals[previous][1] <= intervals[index][0]:
                    dp[index] = max(dp[index], dp[previous] + 1)
            best = max(best, dp[index])
        return len(intervals) - best
