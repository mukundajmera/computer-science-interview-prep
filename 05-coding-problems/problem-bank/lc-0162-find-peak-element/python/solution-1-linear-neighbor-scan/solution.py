from typing import List


class Solution:
    def findPeakElement(self, nums: List[int]) -> int:
        for index, value in enumerate(nums):
            left_ok = index == 0 or nums[index - 1] < value
            right_ok = index == len(nums) - 1 or value > nums[index + 1]
            if left_ok and right_ok:
                return index
        return 0
