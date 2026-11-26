from typing import List


class Solution:
    def maxSubarraySumCircular(self, nums: List[int]) -> int:
        n = len(nums)
        best = nums[0]
        for start in range(n):
            total = 0
            for length in range(n):
                total += nums[(start + length) % n]
                best = max(best, total)
        return best
