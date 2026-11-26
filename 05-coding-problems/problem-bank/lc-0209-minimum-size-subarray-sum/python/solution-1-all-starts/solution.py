from typing import List


class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        best = len(nums) + 1
        for start in range(len(nums)):
            running = 0
            for end in range(start, len(nums)):
                running += nums[end]
                if running >= target:
                    best = min(best, end - start + 1)
                    break
        return 0 if best == len(nums) + 1 else best
