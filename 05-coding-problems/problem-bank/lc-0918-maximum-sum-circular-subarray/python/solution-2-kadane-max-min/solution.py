from typing import List


class Solution:
    def maxSubarraySumCircular(self, nums: List[int]) -> int:
        total = 0
        max_ending = min_ending = nums[0]
        best_max = best_min = nums[0]
        for index, value in enumerate(nums):
            total += value
            if index == 0:
                continue
            max_ending = max(value, max_ending + value)
            best_max = max(best_max, max_ending)
            min_ending = min(value, min_ending + value)
            best_min = min(best_min, min_ending)
        if best_max < 0:
            return best_max
        return max(best_max, total - best_min)
