from typing import List


class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        if not nums:
            return 0
        sorted_nums = sorted(nums)
        best = 1
        current = 1
        for i in range(1, len(sorted_nums)):
            if sorted_nums[i] == sorted_nums[i - 1]:
                continue
            if sorted_nums[i] == sorted_nums[i - 1] + 1:
                current += 1
            else:
                current = 1
            best = max(best, current)
        return best
