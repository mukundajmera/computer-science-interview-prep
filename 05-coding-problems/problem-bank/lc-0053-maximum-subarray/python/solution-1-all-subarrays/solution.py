from typing import List


class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        best = nums[0]
        for start in range(len(nums)):
            running = 0
            for end in range(start, len(nums)):
                running += nums[end]
                best = max(best, running)
        return best
