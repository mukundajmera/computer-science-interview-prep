from typing import List


class Solution:
    def jobScheduling(self, startTime: List[int], endTime: List[int], profit: List[int]) -> int:
        jobs = sorted(zip(startTime, endTime, profit), key=lambda job: job[1])
        dp = [0] * len(jobs)
        best = 0
        for index, (start, _, value) in enumerate(jobs):
            take = value
            for previous in range(index):
                if jobs[previous][1] <= start:
                    take = max(take, dp[previous] + value)
            best = max(best, take)
            dp[index] = best
        return best
