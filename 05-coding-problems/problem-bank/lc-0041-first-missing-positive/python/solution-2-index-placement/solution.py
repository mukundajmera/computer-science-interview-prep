from typing import List


class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        index = 0
        while index < len(nums):
            value = nums[index]
            if 1 <= value <= len(nums) and nums[value - 1] != value:
                target = value - 1
                nums[index], nums[target] = nums[target], nums[index]
            else:
                index += 1
        for index, value in enumerate(nums):
            if value != index + 1:
                return index + 1
        return len(nums) + 1
