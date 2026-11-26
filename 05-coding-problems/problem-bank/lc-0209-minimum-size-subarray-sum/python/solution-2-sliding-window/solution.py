from typing import List


class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        best = len(nums) + 1
        left = 0
        running = 0
        for right, value in enumerate(nums):
            running += value
            while running >= target:
                best = min(best, right - left + 1)
                running -= nums[left]
                left += 1
        return 0 if best == len(nums) + 1 else best
