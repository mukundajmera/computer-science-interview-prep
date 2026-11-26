from bisect import bisect_right
from typing import List


class Solution:
    def jobScheduling(self, startTime: List[int], endTime: List[int], profit: List[int]) -> int:
        jobs = sorted(zip(startTime, endTime, profit), key=lambda job: job[1])
        ends = [end for _, end, _ in jobs]
        dp = [0] * (len(jobs) + 1)
        for index, (start, _, value) in enumerate(jobs, start=1):
            previous_count = bisect_right(ends, start, 0, index - 1)
            dp[index] = max(dp[index - 1], dp[previous_count] + value)
        return dp[-1]
