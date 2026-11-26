from typing import List


class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        sorted_nums = sorted(nums)
        for index in range(1, len(sorted_nums)):
            if sorted_nums[index] == sorted_nums[index - 1]:
                return True
        return False
